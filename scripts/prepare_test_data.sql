INSERT INTO users (id, username, file_total_space) VALUES (1, 'test', 5368709120)
ON CONFLICT (username) DO NOTHING;

INSERT INTO projects (id, name, owner_id, graph)
VALUES (1, 'test_project', 1, '{"project_name": "test_project", "project_id": 1, "user_id": 1, "workflow": {"error_message": null, "nodes": [], "edges": []}}')
ON CONFLICT (name) DO UPDATE SET graph = EXCLUDED.graph;