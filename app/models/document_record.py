from app import db


class DocumentRecord(db.Model):
    __tablename__ = "document_records"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    document_id = db.Column(
        db.Integer,
        db.ForeignKey("documents.id"),
        nullable=False,
        index=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    sheet_name = db.Column(
        db.String(255),
        nullable=True
    )

    source_row = db.Column(
        db.Integer,
        nullable=True
    )

    header_type = db.Column(
        db.String(50),
        nullable=True
    )

    raw_data = db.Column(
        db.JSON,
        nullable=False
    )

    normalized_data = db.Column(
        db.JSON,
        nullable=False
    )

    identifiers = db.Column(
        db.JSON,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        nullable=False
    )
    