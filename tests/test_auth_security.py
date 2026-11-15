from app import create_app


def test_upload_requires_login():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/documents/upload")

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]
