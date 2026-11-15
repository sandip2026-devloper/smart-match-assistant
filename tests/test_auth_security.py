from app import create_app


def test_upload_requires_login():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/documents/upload")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_upload_rejects_missing_csrf_token():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    with client.session_transaction() as session:
        session["_user_id"] = "1"
        session["_fresh"] = True

    response = client.post(
        "/documents/upload",
        data={}
    )

    assert response.status_code == 400