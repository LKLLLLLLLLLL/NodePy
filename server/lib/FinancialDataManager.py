from datetime import datetime, timedelta, timezone
from typing import Literal

import httpx
import pandas as pd
import yfinance as yf
from loguru import logger
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm.session import Session

from server.celery import celery_app
from server.config import CORE_SYMBOLS
from server.models.data import ColType, Table
from server.models.database import (
    DatabaseTransaction,
    FinancialDataRecord,
    TrackedSymbolRecord,
)

DATA_TYPE_SOURCE_MAP = {
    "crypto": "binance",
    "stock": "yfinance",
}
DataType = Literal["crypto", "stock"]

Interval = Literal[
    "1m",
    "1h",
    "1d",
]

class FinancialDataManager:
    db_client: Session

    def __init__(self, db_client: Session):
        self.db_client = db_client

    def get_data(
        self, 
        symbol: str, 
        data_type: DataType, 
        start_time: datetime, 
        end_time: datetime,
        interval: Interval = "1m",
    ) -> Table:
        logger.info(
            f"Node request for {symbol} from {start_time} to {end_time} with interval {interval}."
        )

        # 1. make sure the symbol is being tracked
        self._ensure_symbol_is_tracked(symbol, data_type)

        # 2 & 3. check and fill missing data
        self._fetch_and_store_missing_data(symbol, data_type, start_time, end_time)

        # 4. query final results from the database
        records = (
            self.db_client.query(FinancialDataRecord)
            .filter(
                FinancialDataRecord.symbol == symbol,
                FinancialDataRecord.data_type == data_type,
                FinancialDataRecord.open_time >= start_time,
                FinancialDataRecord.open_time <= end_time,
            )
            .order_by(FinancialDataRecord.open_time.asc())
            .all()
        )

        df = self._records_to_dataframe(records)

        # 5. resample if needed
        if interval != "1m":
            df.set_index('Open Time', inplace=True)
            
            # aggregation rules for resampling
            aggregation_rules = {
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            }
            
            df = df.resample(interval).apply(aggregation_rules) # type: ignore

            df.dropna(inplace=True)
            df.reset_index(inplace=True)

        col_types = {
            "Open Time": ColType.DATETIME,
            "Open": ColType.FLOAT,
            "High": ColType.FLOAT,
            "Low": ColType.FLOAT,
            "Close": ColType.FLOAT,
            "Volume": ColType.FLOAT,
        }
        return Table(df=df, col_types=col_types)

    def _ensure_symbol_is_tracked(self, symbol: str, data_type: DataType):
        """If the symbol is not in the tracking list, add it"""
        tracked = (
            self.db_client.query(TrackedSymbolRecord)
            .filter_by(symbol=symbol, data_type=data_type)
            .first()
        )
        if not tracked:
            new_tracked = TrackedSymbolRecord(symbol=symbol, data_type=data_type)
            self.db_client.add(new_tracked)
            logger.info(f"Added new symbol {symbol} ({data_type}) to tracking list.")
        else:
            tracked.last_requested_at = datetime.now(tz=timezone.utc) # type: ignore

    def _fetch_and_store_missing_data(
        self, symbol: str, data_type: DataType, start: datetime, end: datetime
    ):
        """Core logic: check DB and only fetch missing time periods"""
        # Find existing data points in the DB for the given time range
        existing_times = {
            r[0]
            for r in self.db_client.query(FinancialDataRecord.open_time)
            .filter(
                FinancialDataRecord.symbol == symbol,
                FinancialDataRecord.data_type == data_type,
                FinancialDataRecord.open_time >= start,
                FinancialDataRecord.open_time <= end,
            )
            .all()
        }

        # Generate all required minute-level timestamps
        required_times = set(
            pd.date_range(
                start.replace(second=0, microsecond=0),
                end.replace(second=0, microsecond=0),
                freq="1min",
            )
        )

        missing_times = sorted(list(required_times - existing_times))

        if not missing_times:
            logger.info(
                f"Data for {symbol} in range is complete. No live fetch needed."
            )
            return

        logger.info(
            f"Found {len(missing_times)} missing data points for {symbol}. Fetching live."
        )

        df_live = self._fetch_from_live_api(
            symbol, data_type, missing_times[0], missing_times[-1]
        )

        if not df_live.empty:
            self._store_dataframe(df_live, symbol, data_type)
        else:
            logger.warning(f"No live data fetched for {symbol}.")

    def _fetch_from_live_api(
        self, symbol: str, data_type: DataType, start: datetime, end: datetime
    ) -> pd.DataFrame:
        """Fetch data from external API for the specified time range"""
        source = DATA_TYPE_SOURCE_MAP[data_type]
        try:
            if source == "binance":
                # Binance API uses start/end time (ms)
                start_ms = int(start.timestamp() * 1000)
                end_ms = int(end.timestamp() * 1000)
                klines = self._fetch_binance_api(
                    symbol, "1m", startTime=start_ms, endTime=end_ms
                )
                df = pd.DataFrame(
                    klines,
                    columns=[
                        "Open Time",
                        "Open",
                        "High",
                        "Low",
                        "Close",
                        "Volume",
                        "Close Time",
                        "Quote Asset Volume",
                        "Number of Trades",
                        "Taker Buy Base Asset Volume",
                        "Taker Buy Quote Asset Volume",
                        "Ignore",
                    ],
                )
                df = df[["Open Time", "Open", "High", "Low", "Close", "Volume"]]
                df["Open Time"] = pd.to_datetime(df["Open Time"], unit="ms")
                return df

            elif source == "yfinance":
                # yfinance uses start/end date string
                stock = yf.Ticker(symbol)
                # yfinance's minute-level data is limited to the last 60 days
                hist = stock.history(
                    start=start.strftime("%Y-%m-%d"),
                    end=(end + timedelta(days=1)).strftime("%Y-%m-%d"),
                    interval="1m",
                )

                if hist.empty:
                    logger.warning(
                        f"yfinance returned no data for {symbol} for the requested period."
                    )
                    return pd.DataFrame()

                hist = hist.reset_index()
                hist.rename(columns={"Datetime": "Open Time"}, inplace=True)

                # yfinance returns timezone-aware timestamps, convert to UTC
                # Check if 'Open Time' column exists and is of Datetime type
                if "Open Time" in hist.columns and pd.api.types.is_datetime64_any_dtype(
                    hist["Open Time"]
                ):
                    if hist["Open Time"].dt.tz is not None:  # type: ignore 
                        # If timezone info exists, convert to UTC
                        hist["Open Time"] = hist["Open Time"].dt.tz_convert("UTC") # type: ignore
                    else:
                        # If no timezone info, assume UTC
                        hist["Open Time"] = hist["Open Time"].dt.tz_localize("UTC") # type: ignore

                return hist
            else:
                assert False, f"Unknown data source: {source}"
        except Exception as e:
            logger.error(f"Failed to fetch live data for {symbol} from {source}: {e}")
            return pd.DataFrame()

    def _store_dataframe(self, df: pd.DataFrame, symbol: str, data_type: DataType):
        """Batch store DataFrame data into the database, ignoring existing records"""
        if df.empty:
            return

        # Construct a clean list of dictionaries directly from the DataFrame to avoid _sa_instance_state issues
        records_to_insert = []
        for _, row in df.iterrows():
            # Ensure all required columns for insertion exist
            if not all(
                k in row
                for k in ["Open Time", "Open", "High", "Low", "Close", "Volume"]
            ):
                logger.warning(f"Skipping row with missing columns for {symbol}: {row}")
                continue

            records_to_insert.append(
                {
                    "symbol": symbol,
                    "data_type": data_type,
                    "open_time": row["Open Time"],
                    "open": str(row["Open"]),
                    "high": str(row["High"]),
                    "low": str(row["Low"]),
                    "close": str(row["Close"]),
                    "volume": str(row["Volume"]),
                }
            )

        if not records_to_insert:
            logger.warning(
                f"No valid records to insert for {symbol} after processing DataFrame."
            )
            return

        insert_stmt = insert(FinancialDataRecord).values(records_to_insert)
        on_conflict_stmt = insert_stmt.on_conflict_do_nothing(
            index_elements=["symbol", "data_type", "open_time"]
        )
        self.db_client.execute(on_conflict_stmt)
        logger.info(
            f"Attempted to store {len(records_to_insert)} records for {symbol} ({data_type}) into database."
        )

    def _records_to_dataframe(self, records: list) -> pd.DataFrame:
        if not records:
            return pd.DataFrame()
        data_list = [
            {
                "Open Time": r.open_time,
                "Open": float(r.open),
                "High": float(r.high),
                "Low": float(r.low),
                "Close": float(r.close),
                "Volume": float(r.volume),
            }
            for r in records
        ]
        return pd.DataFrame(data_list)

    @staticmethod
    def _fetch_binance_api(symbol: str, interval: str, **kwargs):
        url = "https://api.binance.com/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": 1000,
        }  # limit max 1000
        params.update(kwargs)
        with httpx.Client() as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            return response.json()

def initialize_core_symbols():
    """Run at service startup to ensure core symbols are in the tracking list"""
    with DatabaseTransaction() as db:
        for data_type, symbols in CORE_SYMBOLS.items():
            for symbol in symbols:
                exists = (
                    db.query(TrackedSymbolRecord)
                    .filter_by(symbol=symbol, data_type=data_type)
                    .first()
                )
                if not exists:
                    db.add(TrackedSymbolRecord(symbol=symbol, data_type=data_type))
                    logger.info(f"Initialized core symbol: {symbol} ({data_type})")
        db.commit()


@celery_app.task
def update_forward_task():
    """
    Forward update task: For all tracked symbols, fetch data newer than the latest record in the database.
    """
    logger.info("Starting forward update task...")
    with DatabaseTransaction() as db:
        manager = FinancialDataManager(db)
        tracked_symbols = db.query(TrackedSymbolRecord).all()

        for ts in tracked_symbols:
            latest_record_time = (
                db.query(func.max(FinancialDataRecord.open_time))
                .filter_by(symbol=ts.symbol, data_type=ts.data_type)
                .scalar()
            )

            start_time = latest_record_time or datetime.now(tz=timezone.utc) - timedelta(
                days=1
            )  # If no data, start from 1 day ago
            end_time = datetime.now(tz=timezone.utc)

            logger.info(f"Forward fetching for {ts.symbol} from {start_time}")
            df = manager._fetch_from_live_api(
                ts.symbol, ts.data_type, start_time, end_time # type: ignore
            )
            if not df.empty:
                manager._store_dataframe(df, ts.symbol, ts.data_type) # type: ignore
    logger.info("Forward update task completed.")


@celery_app.task
def backfill_history_task():
    """
    Backfill history task: For symbols with incomplete historical backfill, fetch data older than the earliest record in the database.
    """
    logger.info("Starting history backfill task...")
    try:
        with DatabaseTransaction() as db:
            manager = FinancialDataManager(db)
            # Find symbols that need backfilling
            symbols_to_backfill = (
                db.query(TrackedSymbolRecord).filter_by(is_history_complete=False).all()
            )

            for ts in symbols_to_backfill:
                oldest_record_time = (
                    ts.oldest_data_time
                    or db.query(func.min(FinancialDataRecord.open_time))
                    .filter_by(symbol=ts.symbol, data_type=ts.data_type)
                    .scalar()
                )

                # If no data at all, let forward_task run first
                if not oldest_record_time: # type: ignore
                    logger.info(f"No data for {ts.symbol}, skipping backfill.")
                    continue

                # Backfill 7 days of data at a time
                end_time = oldest_record_time
                start_time = end_time - timedelta(days=7)

                logger.info(f"Backfilling for {ts.symbol} from {start_time} to {end_time}")
                df = manager._fetch_from_live_api(
                    ts.symbol, ts.data_type, start_time, end_time # type: ignore
                )

                if not df.empty:
                    manager._store_dataframe(df, ts.symbol, ts.data_type) # type: ignore
                    # Update the earliest data time record for the symbol
                    ts.oldest_data_time = df["Open Time"].min()
                    db.commit()
                else:
                    # If the API returns no earlier data, the history backfill is complete
                    ts.is_history_complete = True # type: ignore
                    db.commit()
                    logger.info(f"History backfill complete for {ts.symbol}")
    except Exception as e:
        logger.exception(f"Error in backfill_history_task: {e}")
