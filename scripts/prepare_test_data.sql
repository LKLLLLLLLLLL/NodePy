INSERT INTO users (id, username, file_total_space) VALUES (1, 'test', 5368709120)
ON CONFLICT (username) DO NOTHING;

-- INSERT INTO projects (id, name, owner_id, workflow)
-- VALUES (1, 'test_project', 1, '{"error_message": null, "nodes": [], "edges": []}')
-- ON CONFLICT (name) DO UPDATE SET workflow = EXCLUDED.workflow;