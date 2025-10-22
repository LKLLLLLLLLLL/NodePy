INSERT INTO users (id, username, file_total_space) VALUES (1, 'test', 5368709120)
ON CONFLICT (username) DO NOTHING;

INSERT INTO projects (id, name, owner_id, graph)
VALUES (1, 'test_project', 1, NULL)
ON CONFLICT (name) DO NOTHING;