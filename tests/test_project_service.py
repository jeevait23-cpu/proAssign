from app.projects import ProjectService


class FakeProjectRepository:
    def __init__(self):
        self.projects = {}
        self.next_id = 1

    def list_for_user(self, owner_email):
        return [
            project
            for project in self.projects.values()
            if project["owner_email"] == owner_email
        ]

    def find_for_user(self, project_id, owner_email):
        project = self.projects.get(project_id)
        if not project or project["owner_email"] != owner_email:
            return None
        return project

    def create(self, owner_email, project):
        project_id = str(self.next_id)
        self.next_id += 1
        document = {**project, "_id": project_id, "owner_email": owner_email}
        self.projects[project_id] = document
        return document

    def update(self, project_id, owner_email, project):
        existing = self.find_for_user(project_id, owner_email)
        if not existing:
            return False
        self.projects[project_id] = {**existing, **project}
        return True

    def delete(self, project_id, owner_email):
        existing = self.find_for_user(project_id, owner_email)
        if not existing:
            return False
        del self.projects[project_id]
        return True


def valid_form(**overrides):
    form = {
        "title": "Cloud billing portal",
        "client": "Nova Systems",
        "status": "Development",
        "priority": "High",
        "deadline": "2026-08-20",
        "budget": "Rs 2,50,000",
        "notes": "Sprint one is ready for QA.",
    }
    form.update(overrides)
    return form


def test_create_project_validates_title():
    service = ProjectService(FakeProjectRepository())

    result = service.create("arihant@example.com", valid_form(title="AI"))

    assert result.ok is False
    assert "at least 3" in result.message


def test_create_and_list_projects_for_user():
    repo = FakeProjectRepository()
    service = ProjectService(repo)

    result = service.create("arihant@example.com", valid_form())

    assert result.ok is True
    assert service.list_for_user("arihant@example.com")[0]["title"] == "Cloud billing portal"
    assert service.list_for_user("other@example.com") == []


def test_update_project_for_owner_only():
    repo = FakeProjectRepository()
    service = ProjectService(repo)
    project = service.create("arihant@example.com", valid_form()).project

    blocked = service.update(project["_id"], "other@example.com", valid_form(title="Wrong"))
    updated = service.update(project["_id"], "arihant@example.com", valid_form(title="CRM Revamp"))

    assert blocked.ok is False
    assert updated.ok is True
    assert service.get_for_user(project["_id"], "arihant@example.com")["title"] == "CRM Revamp"


def test_delete_project_for_owner_only():
    repo = FakeProjectRepository()
    service = ProjectService(repo)
    project = service.create("arihant@example.com", valid_form()).project

    blocked = service.delete(project["_id"], "other@example.com")
    deleted = service.delete(project["_id"], "arihant@example.com")

    assert blocked.ok is False
    assert deleted.ok is True
    assert service.list_for_user("arihant@example.com") == []
