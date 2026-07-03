from dataclasses import dataclass


VALID_STATUSES = ("Discovery", "Design", "Development", "Testing", "Launched")
VALID_PRIORITIES = ("Low", "Medium", "High", "Critical")


@dataclass
class ProjectResult:
    ok: bool
    message: str
    project: dict | None = None


class ProjectService:
    def __init__(self, project_repo):
        self.project_repo = project_repo

    def list_for_user(self, owner_email):
        return self.project_repo.list_for_user(owner_email)

    def get_for_user(self, project_id, owner_email):
        return self.project_repo.find_for_user(project_id, owner_email)

    def create(self, owner_email, form):
        payload = self._payload_from_form(form)
        if isinstance(payload, ProjectResult):
            return payload

        project = self.project_repo.create(owner_email, payload)
        return ProjectResult(True, "Project added to production board.", project)

    def update(self, project_id, owner_email, form):
        payload = self._payload_from_form(form)
        if isinstance(payload, ProjectResult):
            return payload

        updated = self.project_repo.update(project_id, owner_email, payload)
        if not updated:
            return ProjectResult(False, "Project not found.")
        return ProjectResult(True, "Project updated successfully.")

    def delete(self, project_id, owner_email):
        deleted = self.project_repo.delete(project_id, owner_email)
        if not deleted:
            return ProjectResult(False, "Project not found.")
        return ProjectResult(True, "Project deleted.")

    def _payload_from_form(self, form):
        title = (form.get("title") or "").strip()
        client = (form.get("client") or "").strip()
        status = (form.get("status") or "").strip()
        priority = (form.get("priority") or "").strip()
        deadline = (form.get("deadline") or "").strip()
        budget = (form.get("budget") or "").strip()
        notes = (form.get("notes") or "").strip()

        if len(title) < 3:
            return ProjectResult(False, "Project name must be at least 3 characters.")
        if len(client) < 2:
            return ProjectResult(False, "Client name must be at least 2 characters.")
        if status not in VALID_STATUSES:
            return ProjectResult(False, "Choose a valid project status.")
        if priority not in VALID_PRIORITIES:
            return ProjectResult(False, "Choose a valid priority.")

        return {
            "title": title,
            "client": client,
            "status": status,
            "priority": priority,
            "deadline": deadline,
            "budget": budget,
            "notes": notes,
        }
