import io
import uuid
from app import create_app, db
from app.models.user import User
from app.models.document import Document


def test_user_cannot_access_another_users_document():
    app = create_app()
    app.config["TESTING"] = True

    unique_id = uuid.uuid4().hex

    with app.app_context():
        user1 = User(
            name="Test User One",
            email=f"security_user_one_{unique_id}@test.local"
        )
        user1.set_password("Password123!")

        user2 = User(
            name="Test User Two",
            email=f"security_user_two_{unique_id}@test.local"
        )
        user2.set_password("Password123!")

        db.session.add_all([user1, user2])
        db.session.commit()

        document = Document(
            user_id=user1.id,
            original_name="private_test.xlsx",
            stored_name=f"private_test_{unique_id}.xlsx",
            original_type="xlsx",
            status="uploaded"
        )

        db.session.add(document)
        db.session.commit()

        document_id = document.id
        user2_id = user2.id

    client = app.test_client()

    with client.session_transaction() as session:
        session["_user_id"] = str(user2_id)
        session["_fresh"] = True

    response = client.get(
        f"/documents/download/{document_id}"
    )

    assert response.status_code in (403, 404)


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

    import re

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