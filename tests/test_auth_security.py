import io
import re
import uuid

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
def test_upload_rejects_unsupported_extension():
    app = create_app()
    app.config["TESTING"] = True

    unique_id = uuid.uuid4().hex

    with app.app_context():
        user = User(
            name="Upload Test User",
            email=f"upload_security_{unique_id}@test.local"
        )
        user.set_password("Password123!")

        db.session.add(user)
        db.session.commit()

        user_id = user.id

    client = app.test_client()

    with client.session_transaction() as session:
        session["_user_id"] = str(user_id)
        session["_fresh"] = True

    response = client.get("/documents/upload")

    assert response.status_code == 200

    html = response.get_data(as_text=True)

    match = re.search(
        r'name="csrf_token"\s+value="([^"]+)"',
        html
    )

    assert match is not None

    csrf_token = match.group(1)

    response = client.post(
        "/documents/upload",
        data={
            "csrf_token": csrf_token,
            "file": (
                io.BytesIO(b"test content"),
                "malicious.xyz"
            )
        },
        content_type="multipart/form-data"
    )

    assert response.status_code == 302
    assert "/documents/upload" in response.headers["Location"]

    with app.app_context():
        user = db.session.get(User, user_id)

        if user:
            db.session.delete(user)
            db.session.commit()