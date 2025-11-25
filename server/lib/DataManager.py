from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from server import logger
from server.models.data import Data, DataRef, DataView
from server.models.database import NodeOutputRecord, ProjectRecord
from server.models.project import ProjWorkflow


class DataManager:
    """
    The class to manage data output from nodes.
    """
    def __init__(self, sync_db_session: Session | None = None, async_db_session: AsyncSession | None = None):
        if sync_db_session:
            assert async_db_session is None
            self.db_client = sync_db_session
        elif async_db_session:
            assert sync_db_session is None
            self.async_db_client = async_db_session
        else:
            raise ValueError("Either sync_db_session or async_db_session must be provided")
    
    def read_sync(self, data_ref: DataRef) -> Data:
        """ Read data synchronously from database given a DataRef """
        if self.db_client is None:
            raise AssertionError("Synchronous DB client is not initialized")
        
        data_record = self.db_client.query(NodeOutputRecord).filter(
            NodeOutputRecord.id == data_ref.data_id
        ).first()
        if not data_record:
            raise KeyError(f"Data not found for DataRef: {data_ref}")

        data_view = DataView.model_validate(data_record.data)
        data = Data.from_view(data_view)
        return data

    async def read_async(self, data_ref: DataRef) -> Data:
        """ Read data asynchronously from database given a DataRef """
        if self.async_db_client is None:
            raise AssertionError("Asynchronous DB client is not initialized")
        
        result = await self.async_db_client.execute(
            select(NodeOutputRecord).where(
                NodeOutputRecord.id == data_ref.data_id
            )
        )
        data_record = result.scalars().first()
        if not data_record:
            raise KeyError(f"Data not found for DataRef: {data_ref}")

        data_view = DataView.model_validate(data_record.data)
        data = Data.from_view(data_view)
        return data

    def write_sync(self, data: Data, node_id: str, project_id: int, port: str) -> DataRef:
        """ Write data synchronously to database, return a DataRef """
        # Notice: for cache system in frontend, if data not chaged, we should reuse old data_id
        if self.db_client is None:
            raise AssertionError("Synchronous DB client is not initialized")

        # 1. get old data record in database
        old_data_record = self.db_client.query(NodeOutputRecord).filter_by(
            project_id=project_id,
            node_id=node_id,
            port=port
        ).first()

        # 2. if an old record exists, compare data
        if old_data_record:
            old_data_view = DataView(**old_data_record.data) # type: ignore
            old_data = Data.from_view(old_data_view)
            # 2.1. if data is unchanged, reuse old data_id and return
            if old_data == data:
                return DataRef(data_id=old_data_record.id) # type: ignore
            # 2.2. if data has changed, delete the old record.
            # A new record will be inserted later.
            self.db_client.delete(old_data_record)
            self.db_client.flush() # Use flush to execute the delete without committing the transaction

        # 3. Insert a new record for the new/changed data
        new_data_record = NodeOutputRecord(
            project_id=project_id,
            node_id=node_id,
            port=port,
            data=data.to_view().to_dict()
        )
        self.db_client.add(new_data_record)
        self.db_client.flush() # Flush to assign the new ID to the object

        # 4. Construct and return the new DataRef
        data_ref = DataRef(data_id=new_data_record.id) # type: ignore
        return data_ref

    def clean_orphan_data_sync(self, project_id: int) -> None:
        """ Clean data records with no project reference """
        if self.db_client is None:
            raise AssertionError("Synchronous DB client is not initialized")
        # 1. get all data ref for the project
        project_record = self.db_client.query(ProjectRecord).filter(
            ProjectRecord.id == project_id
        ).first()
        if not project_record:
            raise ValueError(f"Project not found: {project_id}")
        # 2. get all data ids referenced by the project
        referenced_data_ids = set()
        workflow = ProjWorkflow.model_validate(project_record.workflow)
        nodes = workflow.nodes
        for node in nodes:
            for _, data_ref in node.data_out.items():
                referenced_data_ids.add(data_ref.data_id)
        # 3. delete data records not in referenced_data_ids
        data_records = self.db_client.query(NodeOutputRecord).filter(
            NodeOutputRecord.project_id == project_id
        ).all()
        deleted_datas = []
        for data_record in data_records:
            if data_record.id not in referenced_data_ids:
                deleted_datas.append(data_record.data)
                self.db_client.delete(data_record)
        self.db_client.commit()
        logger.info(f"Cleaned {len(deleted_datas)} orphan data records for project {project_id}")
        return
  
        