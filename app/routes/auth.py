from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user

from app import db, limiter
from app.models.user import User
from app.models.document import Document


auth = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


@auth.route("/test")
def test():
    return "Authentication system is working."


@auth.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:

            flash(
                "All fields are required.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash(
                "This email is already registered.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )

        user = User(
            name=name,
            email=email
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash(
            "Registration successful. You can now log in.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "auth/register.html"
    )


@auth.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:

            flash(
                "Email and password are required.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )

        user = User.query.filter_by(
            email=email
        ).first()

        if user is None or not user.check_password(password):

            flash(
                "Invalid email or password.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )

        login_user(user)

        return redirect(
            url_for("auth.dashboard")
        )

    return render_template(
        "auth/login.html"
    )


@auth.route("/dashboard")
@login_required
def dashboard():

    documents = Document.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Document.id.desc()
    ).limit(10).all()

    return render_template(
        "auth/dashboard.html",
        user=current_user,
        documents=documents
    )


@auth.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("auth.login")
    )