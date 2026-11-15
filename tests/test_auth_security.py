from app import create_app, db
from app.models.user import User


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


def test_password_is_stored_as_hash():
    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        user = User(
            name="Hash Test User",
            email="hash_test_user_security@test.local"
        )

        plain_password = "Password123!"
        user.set_password(plain_password)

        db.session.add(user)
        db.session.commit()

        assert user.password_hash != plain_password
        assert user.password_hash.startswith("scrypt:")

        assert user.check_password(plain_password) is True
        assert user.check_password("WrongPassword123!") is False

        db.session.delete(user)
        db.session.commit()


def test_security_headers_are_present():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == (
        "strict-origin-when-cross-origin"
    )
    assert response.headers["Permissions-Policy"] == (
        "camera=(), microphone=(), geolocation=()"
    )
def test_session_cookie_security():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/")

    set_cookie = response.headers.get("Set-Cookie", "")

    if set_cookie:
        assert "HttpOnly" in set_cookie
        assert "SameSite=Lax" in set_cookie