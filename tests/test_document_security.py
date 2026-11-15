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
