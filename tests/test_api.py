def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "message" in r.json()


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
    assert "x-request-id" in r.headers


def test_create_and_list(client):
    r = client.post("/tasks", json={"title": "a"})
    assert r.status_code == 201
    body = r.json()
    assert body["id"] == 1
    assert body["title"] == "a"
    assert body["completed"] is False

    assert client.get("/tasks").json() == [body]


def test_get_one(client):
    client.post("/tasks", json={"title": "a"})
    r = client.get("/tasks/1")
    assert r.status_code == 200
    assert r.json()["title"] == "a"


def test_update_partial(client):
    client.post("/tasks", json={"title": "a", "description": "old"})
    r = client.put("/tasks/1", json={"completed": True})
    assert r.status_code == 200
    body = r.json()
    assert body["completed"] is True
    assert body["description"] == "old"  # untouched


def test_delete(client):
    client.post("/tasks", json={"title": "a"})
    assert client.delete("/tasks/1").status_code == 204
    assert client.get("/tasks/1").status_code == 404


def test_missing_task_envelope(client):
    r = client.get("/tasks/999")
    assert r.status_code == 404
    body = r.json()
    assert body["error"]["code"] == 404
    assert "999" in body["error"]["message"]
    assert "request_id" in body["error"]


def test_validation_envelope(client):
    r = client.post("/tasks", json={"title": ""})
    assert r.status_code == 422
    body = r.json()
    assert body["error"]["code"] == 422
    assert isinstance(body["error"]["details"], list)


def test_request_id_round_trip(client):
    r = client.get("/health", headers={"x-request-id": "abc123"})
    assert r.headers["x-request-id"] == "abc123"
