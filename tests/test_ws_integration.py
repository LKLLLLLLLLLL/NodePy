import json
import time
import asyncio
import requests
import websockets

request = [
    """
{
    "project_id": 1,
  "nodes": [
    {
      "id": "n1",
      "type": "ConstNode",
      "name": "const_one",
      "params": {
        "value": 3,
        "data_type": "int"
      }
    }
  ],
  "edges": []
}
""",
    """
{
    "project_id": 1,
  "nodes": [
    {
      "id": "n1",
      "type": "ConstNode",
      "name": "const_a",
      "params": {
        "value": 2,
        "data_type": "int"
      }
    },
    {
      "id": "n2",
      "type": "ConstNode",
      "name": "const_b",
      "params": {
        "value": 5,
        "data_type": "int"
      }
    },
    {
      "id": "n3",
      "type": "NumBinComputeNode",
      "name": "add_node",
      "params": {
        "op": "ADD"
      }
    }
  ],
  "edges": [
    {"src": "n1", "src_port": "const", "tar": "n3", "tar_port": "x"},
    {"src": "n2", "src_port": "const", "tar": "n3", "tar_port": "y"}
  ]
}
""",
    """{
        "project_id": 1,
  "nodes": [
    {
      "id": "c1",
      "type": "ConstNode",
      "name": "const_10",
      "params": {
        "value": 10,
        "data_type": "int"
      }
    },
    {
      "id": "u1",
      "type": "NumUnaryComputeNode",
      "name": "negate",
      "params": {
        "op": "NEG"
      }
    },
    {
      "id": "b1",
      "type": "NumBinComputeNode",
      "name": "add_with_neg",
      "params": {
        "op": "ADD"
      }
    }
  ],
  "edges": [
    {"src": "c1", "src_port": "const", "tar": "u1", "tar_port": "x"},
    {"src": "c1", "src_port": "const", "tar": "b1", "tar_port": "x"},
    {"src": "u1", "src_port": "result", "tar": "b1", "tar_port": "y"}
  ]
}""",
    """
{
    "project_id": 1,
  "nodes": [
    {
      "id": "t_gdp",
      "type": "TableNode",
      "name": "gdp_table",
      "params": {
        "col_names": ["year", "gdp", "population"],
        "rows": [
          {"year": 2018, "gdp": 500000000000, "population": 25000000},
          {"year": 2019, "gdp": 520000000000, "population": 25500000},
          {"year": 2020, "gdp": 510000000000, "population": 25800000},
          {"year": 2021, "gdp": 560000000000, "population": 26000000}
        ]
      }
    },
    {
      "id": "compute_pc",
      "type": "ColBinNumComputeNode",
      "name": "gdp_per_capita",
      "params": {
        "op": "DIV",
        "col1": "gdp",
        "col2": "population",
        "result_col": "gdp_per_capita"
      }
    },
    {
      "id": "plot_pc",
      "type": "PlotNode",
      "name": "plot_per_capita",
      "params": {
        "x_column": "year",
        "y_column": "gdp_per_capita",
        "plot_type": "line",
        "title": "GDP per Capita over Years"
      }
    }
  ],
  "edges": [
    {"src": "t_gdp", "src_port": "table", "tar": "compute_pc", "tar_port": "table"},
    {"src": "compute_pc", "src_port": "table", "tar": "plot_pc", "tar_port": "input"}
  ]
}
""",
    """
{
    "project_id": 1,
  "nodes": [
    {
      "id": "t_products",
      "type": "TableNode",
      "name": "products",
      "params": {
        "col_names": ["id", "name", "code"],
        "rows": [
          {"id": 1, "name": "Alpha Pro", "code": "X100"},
          {"id": 2, "name": "Beta", "code": "Y20"},
          {"id": 3, "name": "Gamma Pro Max", "code": "X200"},
          {"id": 4, "name": "Delta", "code": "Z5"}
        ]
      }
    },
    {
      "id": "string_pro",
      "type": "StringNode",
      "name": "flag_string_pro",
      "params": {
        "value": "Pro"
      }
    },
    {
      "id": "contains_pro",
      "type": "TableContainsStringNode",
      "name": "flag_contains_pro",
      "params": {
        "column": "name",
        "result_col": "has_pro"
      }
    },
    {
      "id": "string_x",
      "type": "StringNode",
      "name": "flag_string_x",
      "params": {
        "value": "X"
      }
    },
    {
      "id": "starts_x",
      "type": "TableStartWithStringNode",
      "name": "flag_code_starts_x",
      "params": {
        "column": "code",
        "result_col": "code_starts_X"
      }
    },
    {
      "id": "append_tag",
      "type": "TableAppendStringNode",
      "name": "append_version_tag",
      "params": {
        "column": "code",
        "result_col": "code_v"
      }
    },
    {
      "id": "tag_value",
      "type": "StringNode",
      "name": "tag_string",
      "params": {
        "value": "-2025"
      }
    }
  ],
  "edges": [
    {"src": "t_products", "src_port": "table", "tar": "contains_pro", "tar_port": "table"},
    {"src": "string_pro", "src_port": "string", "tar": "contains_pro", "tar_port": "substring"},
    {"src": "string_x", "src_port": "string", "tar": "starts_x", "tar_port": "substring"},
    {"src": "t_products", "src_port": "table", "tar": "starts_x", "tar_port": "table"},
    {"src": "t_products", "src_port": "table", "tar": "append_tag", "tar_port": "table"},
    {"src": "tag_value", "src_port": "string", "tar": "append_tag", "tar_port": "string"}
  ]
}
""",
    """
{
    "project_id": 1,
  "nodes": [
    {
      "id": "t_sales",
      "type": "TableNode",
      "name": "sales_history",
      "params": {
        "col_names": ["date", "sales", "cost"],
        "rows": [
          {"date": "202501", "sales": 12000.0, "cost": 8000.0},
          {"date": "202502", "sales": 15000.0, "cost": 9500.0},
          {"date": "202503", "sales": 13000.0, "cost": 7000.0},
          {"date": "202504", "sales": 18000.0, "cost": 11000.0}
        ]
      }
    },
    {
      "id": "profit_calc",
      "type": "ColBinNumComputeNode",
      "name": "compute_profit",
      "params": {
        "col1": "sales",
        "col2": "cost",
        "result_col": "profit",
        "op": "SUB"
      }
    },
    {
      "id": "tax_rate",
      "type": "ConstNode",
      "name": "tax_rate_const",
      "params": {
        "value": 0.2,
        "data_type": "float"
      }
    },
    {
      "id": "tax_per_row",
      "type": "TabBinPrimNumComputeNode",
      "name": "compute_tax",
      "params": {
        "op": "MUL",
        "col": "profit",
        "result_col": "tax"
      }
    },
    {
      "id": "profit_after_tax",
      "type": "ColBinNumComputeNode",
      "name": "profit_after_tax",
      "params": {
        "col1": "profit",
        "col2": "tax",
        "result_col": "profit_after_tax",
        "op": "SUB"
      }
    },
    {
      "id": "plot_after_tax",
      "type": "PlotNode",
      "name": "plot_after_tax",
      "params": {
        "x_column": "date",
        "y_column": "profit_after_tax",
        "plot_type": "bar",
        "title": "Profit after Tax (monthly)"
      }
    }
  ],
  "edges": [
    {"src": "t_sales", "src_port": "table", "tar": "profit_calc", "tar_port": "table"},
    {"src": "profit_calc", "src_port": "table", "tar": "tax_per_row", "tar_port": "table"},
    {"src": "tax_rate", "src_port": "const", "tar": "tax_per_row", "tar_port": "num"},
    {"src": "tax_per_row", "src_port": "table", "tar": "profit_after_tax", "tar_port": "table"},
    {"src": "profit_after_tax", "src_port": "table", "tar": "plot_after_tax", "tar_port": "input"}
  ]
}
""",
    """
{
    "project_id": 1,
  "nodes": [
    {
      "id": "c_a",
      "type": "ConstNode",
      "name": "const_a",
      "params": { "value": 7, "data_type": "int" }
    },
    {
      "id": "c_b",
      "type": "ConstNode",
      "name": "const_b",
      "params": { "value": -3, "data_type": "int" }
    },
    {
      "id": "neg_b",
      "type": "NumUnaryComputeNode",
      "name": "negate_b",
      "params": { "op": "NEG" }
    },
    {
      "id": "sum_ab",
      "type": "NumBinComputeNode",
      "name": "add_a_bneg",
      "params": { "op": "ADD" }
    },
    {
      "id": "square",
      "type": "NumBinComputeNode",
      "name": "square_sum",
      "params": { "op": "POW" }
    }
  ],
  "edges": [
    {"src": "c_b", "src_port": "const", "tar": "neg_b", "tar_port": "x"},
    {"src": "c_a", "src_port": "const", "tar": "sum_ab", "tar_port": "x"},
    {"src": "neg_b", "src_port": "result", "tar": "sum_ab", "tar_port": "y"},
    {"src": "sum_ab", "src_port": "result", "tar": "square", "tar_port": "x"},
    {"src": "c_a", "src_port": "const", "tar": "square", "tar_port": "y"}
  ]
}
""",
    """
{
    "project_id": 1,
  "nodes": [
    {
      "id": "t_catalog",
      "type": "TableNode",
      "name": "monthly_metrics",
      "params": {
        "col_names": ["month", "active_users", "new_signups"],
        "rows": [
          {"month": 202501, "active_users": 5000, "new_signups": 300},
          {"month": 202502, "active_users": 5200, "new_signups": 350},
          {"month": 202503, "active_users": 5400, "new_signups": 420},
          {"month": 202504, "active_users": 5800, "new_signups": 500}
        ]
      }
    },
    {
      "id": "growth_calc",
      "type": "ColBinNumComputeNode",
      "name": "signup_growth",
      "params": {
        "col1": "new_signups",
        "col2": "active_users",
        "result_col": "signup_rate",
        "op": "DIV"
      }
    },
    {
      "id": "plot_users",
      "type": "PlotNode",
      "name": "plot_active_users",
      "params": {
        "x_column": "month",
        "y_column": "active_users",
        "plot_type": "line",
        "title": "Active Users over Months"
      }
    }
  ],
  "edges": [
    {"src": "t_catalog", "src_port": "table", "tar": "growth_calc", "tar_port": "table"},
    {"src": "t_catalog", "src_port": "table", "tar": "plot_users", "tar_port": "input"}
  ]
}
""",
]


# Choose a graph payload (use a small one to keep test quick)
topo_payload = json.loads(request[5])

# Convert to Graph format
graph_payload = {
    "project_name": "test_project",
    "project_id": 1,
    "user_id": 1,
    "nodes": [
        {
            "id": node["id"],
            "type": node["type"],
            "position": {"x": 0.0, "y": 0.0},
            "param": node.get("params", {})
        }
        for node in topo_payload["nodes"]
    ],
    "edges": [
        {
            "id": f"{edge['src']}_{edge['src_port']}_{edge['tar']}_{edge['tar_port']}",
            "src": edge["src"],
            "src_port": edge["src_port"],
            "tar": edge["tar"],
            "tar_port": edge["tar_port"]
        }
        for edge in topo_payload["edges"]
    ]
}

# Submit task via HTTP API
resp = requests.post(
    "http://localhost:8000/api/project/sync",
    json=graph_payload,
    timeout=10,
)

assert resp.status_code in (200, 202), f"Unexpected status code: {resp.status_code}, {resp.content}"
data = resp.json()
task_id = data.get("task_id")
assert task_id, "No task_id returned from /api/nodes/run"

uri = f"ws://localhost:8000/api/project/status/{task_id}"
print(f"Submitted task {task_id}, connecting to {uri}")

messages = []

async def listen():
    from websockets.exceptions import ConnectionClosedOK

    async with websockets.connect(uri) as ws:
        start = time.time()
        while True:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=10)
            except asyncio.TimeoutError:
                print("Timed out waiting for messages")
                break
            except ConnectionClosedOK:
                print("WebSocket closed normally by server (Task finished).")
                break

            print("WS MESSAGE:", msg)
            messages.append(msg)

            # # Try to stop when task finished
            # try:
            #     parsed = json.loads(msg)
            #     status = parsed.get("status")
            #     stage = parsed.get("stage")
            #     if status in ("SUCCESS", "FAILURE") and stage is None:
            #         print(f"Task finished with status: {status}")
            #         break
            # except Exception:
            #     pass

            if time.time() - start > 120:
                print("Listener timeout (120s) reached")
                break

asyncio.run(listen())

# We expect at least one progress update from the worker
assert len(messages) > 0, "No messages received from WebSocket for task"
