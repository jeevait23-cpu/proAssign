from tests.test_auth_service import (
    test_login_accepts_registered_user,
    test_login_rejects_wrong_password,
    test_register_normalizes_email_and_rejects_duplicate,
    test_register_rejects_short_password,
)
from tests.test_project_service import (
    test_create_and_list_projects_for_user,
    test_create_project_validates_title,
    test_delete_project_for_owner_only,
    test_update_project_for_owner_only,
)


def main():
    tests = [
        test_register_rejects_short_password,
        test_register_normalizes_email_and_rejects_duplicate,
        test_login_accepts_registered_user,
        test_login_rejects_wrong_password,
        test_create_project_validates_title,
        test_create_and_list_projects_for_user,
        test_update_project_for_owner_only,
        test_delete_project_for_owner_only,
    ]

    for test in tests:
        test()
        print(f"PASS {test.__name__}")


if __name__ == "__main__":
    main()
