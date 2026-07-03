from app.auth import AuthService


class FakeUserRepository:
    def __init__(self):
        self.users = {}
        self.login_marks = []

    def find_by_email(self, email):
        return self.users.get(email)

    def create(self, user):
        user = {**user, "_id": len(self.users) + 1}
        self.users[user["email"]] = user
        return user

    def mark_login(self, email):
        self.login_marks.append(email)


def test_register_rejects_short_password():
    service = AuthService(FakeUserRepository())

    result = service.register("Arihant Sharma", "arihant@example.com", "short")

    assert result.ok is False
    assert "at least 8" in result.message


def test_register_normalizes_email_and_rejects_duplicate():
    repo = FakeUserRepository()
    service = AuthService(repo)

    first = service.register("Arihant Sharma", "ARIHANT@example.com", "securepass")
    second = service.register("Arihant Sharma", "arihant@example.com", "securepass")

    assert first.ok is True
    assert second.ok is False
    assert "already exists" in second.message


def test_login_accepts_registered_user():
    repo = FakeUserRepository()
    service = AuthService(repo)
    service.register("Arihant Sharma", "arihant@example.com", "securepass")

    result = service.login("arihant@example.com", "securepass")

    assert result.ok is True
    assert result.user["email"] == "arihant@example.com"
    assert repo.login_marks == ["arihant@example.com"]


def test_login_rejects_wrong_password():
    repo = FakeUserRepository()
    service = AuthService(repo)
    service.register("Arihant Sharma", "arihant@example.com", "securepass")

    result = service.login("arihant@example.com", "wrongpass")

    assert result.ok is False
    assert "Invalid" in result.message
