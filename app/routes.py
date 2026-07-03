from functools import wraps

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from .auth import AuthService
from .projects import ProjectService, VALID_PRIORITIES, VALID_STATUSES

auth_bp = Blueprint("auth", __name__)
dashboard_bp = Blueprint("dashboard", __name__)


def auth_service():
    return AuthService(current_app.user_repo)


def project_service():
    return ProjectService(current_app.project_repo)


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if not session.get("user"):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view


@auth_bp.get("/")
def index():
    if session.get("user"):
        return redirect(url_for("dashboard.dashboard"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        result = auth_service().register(
            request.form.get("name"),
            request.form.get("email"),
            request.form.get("password"),
        )
        flash(result.message, "success" if result.ok else "danger")
        if result.ok:
            session["user"] = {"name": result.user["name"], "email": result.user["email"]}
            return redirect(url_for("dashboard.dashboard"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        result = auth_service().login(
            request.form.get("email"),
            request.form.get("password"),
        )
        flash(result.message, "success" if result.ok else "danger")
        if result.ok:
            session["user"] = {"name": result.user["name"], "email": result.user["email"]}
            return redirect(url_for("dashboard.dashboard"))

    return render_template("login.html")


@auth_bp.post("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))


@dashboard_bp.get("/dashboard")
@login_required
def dashboard():
    user = session["user"]
    projects = project_service().list_for_user(user["email"])
    stats = {
        "total": len(projects),
        "active": sum(1 for project in projects if project["status"] != "Launched"),
        "launched": sum(1 for project in projects if project["status"] == "Launched"),
    }
    return render_template(
        "dashboard.html",
        priorities=VALID_PRIORITIES,
        projects=projects,
        stats=stats,
        statuses=VALID_STATUSES,
        user=user,
    )


@dashboard_bp.post("/dashboard/projects")
@login_required
def create_project():
    result = project_service().create(session["user"]["email"], request.form)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("dashboard.dashboard"))


@dashboard_bp.route("/dashboard/projects/<project_id>/edit", methods=["GET", "POST"])
@login_required
def edit_project(project_id):
    service = project_service()
    user = session["user"]

    if request.method == "POST":
        result = service.update(project_id, user["email"], request.form)
        flash(result.message, "success" if result.ok else "danger")
        return redirect(url_for("dashboard.dashboard"))

    project = service.get_for_user(project_id, user["email"])
    if not project:
        flash("Project not found.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    return render_template(
        "edit_project.html",
        priorities=VALID_PRIORITIES,
        project=project,
        statuses=VALID_STATUSES,
        user=user,
    )


@dashboard_bp.post("/dashboard/projects/<project_id>/delete")
@login_required
def delete_project(project_id):
    result = project_service().delete(project_id, session["user"]["email"])
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("dashboard.dashboard"))
