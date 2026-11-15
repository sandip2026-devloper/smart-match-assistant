from app import db


class MatchResult(db.Model):
    __tablename__ = "match_results"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    filename = db.Column(
        db.String(255),
        nullable=False,
        unique=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        nullable=False
    )