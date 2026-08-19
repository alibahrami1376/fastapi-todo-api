def test_create_task_success(authenticated_client, task_payload, user):
    response = authenticated_client.post(
        "/api/v1/todos",
        json=task_payload,
    )

    assert response.status_code == 201

    data = response.json()
    assert data["id"] > 0
    assert data["title"] == task_payload["title"]
    assert data["description"] == task_payload["description"]
    assert data["owner_id"] == user.id
    assert data["is_completed"] is False


def test_create_task_unauthorized(client, task_payload):
    response = client.post(
        "/api/v1/todos",
        json=task_payload,
    )

    assert response.status_code == 401


def test_get_tasks_success(authenticated_client, task_payload):
    authenticated_client.post("/api/v1/todos", json=task_payload)

    response = authenticated_client.get("/api/v1/todos")

    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 1
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert len(data["results"]) == 1
    assert data["results"][0]["title"] == task_payload["title"]


def test_filter_completed(authenticated_client, task_payload):
    pending = authenticated_client.post("/api/v1/todos", json=task_payload)
    completed_payload = {**task_payload, "title": "Completed Task"}
    completed = authenticated_client.post("/api/v1/todos", json=completed_payload)

    authenticated_client.patch(
        f"/api/v1/todos/{completed.json()['id']}",
        json={"is_completed": True},
    )

    response = authenticated_client.get(
        "/api/v1/todos",
        params={"is_completed": True},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["results"][0]["id"] == completed.json()["id"]
    assert data["results"][0]["is_completed"] is True

    pending_response = authenticated_client.get(
        "/api/v1/todos",
        params={"is_completed": False},
    )
    assert pending_response.json()["total"] == 1
    assert pending_response.json()["results"][0]["id"] == pending.json()["id"]


def test_search_tasks(authenticated_client, task_payload):
    authenticated_client.post(
        "/api/v1/todos",
        json={**task_payload, "title": "Weekly meeting notes"},
    )
    authenticated_client.post(
        "/api/v1/todos",
        json={**task_payload, "title": "Walk the dog"},
    )

    response = authenticated_client.get(
        "/api/v1/todos",
        params={"q": "meeting"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert "meeting" in data["results"][0]["title"].lower()


def test_sort_tasks(authenticated_client, task_payload):
    authenticated_client.post(
        "/api/v1/todos",
        json={**task_payload, "title": "Charlie task"},
    )
    authenticated_client.post(
        "/api/v1/todos",
        json={**task_payload, "title": "Alpha task"},
    )
    authenticated_client.post(
        "/api/v1/todos",
        json={**task_payload, "title": "Bravo task"},
    )

    response = authenticated_client.get(
        "/api/v1/todos",
        params={"sort_by": "title", "order": "asc"},
    )

    assert response.status_code == 200
    titles = [item["title"] for item in response.json()["results"]]
    assert titles == ["Alpha task", "Bravo task", "Charlie task"]


def test_get_task_success(authenticated_client, task_payload, user):
    create_response = authenticated_client.post(
        "/api/v1/todos",
        json=task_payload,
    )
    task_id = create_response.json()["id"]

    response = authenticated_client.get(f"/api/v1/todos/{task_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["owner_id"] == user.id
    assert data["title"] == task_payload["title"]


def test_get_task_not_found(authenticated_client):
    response = authenticated_client.get("/api/v1/todos/999999")

    assert response.status_code == 404


def test_update_task_success(authenticated_client, task_payload):
    create_response = authenticated_client.post(
        "/api/v1/todos",
        json=task_payload,
    )
    task_id = create_response.json()["id"]

    response = authenticated_client.patch(
        f"/api/v1/todos/{task_id}",
        json={"title": "Updated Task"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Task"


def test_update_byput_task_success(authenticated_client, task_payload, user):
    create_response = authenticated_client.post(
        "/api/v1/todos",
        json=task_payload,
    )

    task_id = create_response.json()["id"]

    new_task_payload = {
        "title": "Test Task Put",
        "description": "Task description",
        "is_completed": True,
        "priority": "low",
        "due_date": None,
    }

    response = authenticated_client.put(
        f"/api/v1/todos/{task_id}",
        json=new_task_payload,
    )

    assert response.status_code == 200

    response = authenticated_client.get(f"/api/v1/todos/{task_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["owner_id"] == user.id
    assert data["is_completed"] is True
    assert data["title"] == new_task_payload["title"]
    assert data["priority"] == new_task_payload["priority"]


def test_delete_task_success(authenticated_client, task_payload):
    create_response = authenticated_client.post(
        "/api/v1/todos",
        json=task_payload,
    )
    task_id = create_response.json()["id"]

    response = authenticated_client.delete(f"/api/v1/todos/{task_id}")

    assert response.status_code == 204

    get_response = authenticated_client.get(f"/api/v1/todos/{task_id}")
    assert get_response.status_code == 404


def test_get_task_forbidden_for_other_user(
    authenticated_client,
    second_authenticated_client,
    task_payload,
):
    create_response = authenticated_client.post(
        "/api/v1/todos",
        json=task_payload,
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    response = second_authenticated_client.get(f"/api/v1/todos/{task_id}")

    assert response.status_code == 403


def test_delete_task_permission_denied(
    authenticated_client,
    task_payload,
    second_authenticated_client,
):
    create_response = second_authenticated_client.post(
        "/api/v1/todos",
        json=task_payload,
    )

    task_id = create_response.json()["id"]

    response = authenticated_client.delete(f"/api/v1/todos/{task_id}")

    assert response.status_code == 403
