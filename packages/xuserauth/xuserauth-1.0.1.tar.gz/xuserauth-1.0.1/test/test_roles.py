from xuserauth.roles import has_role


class DummyUser:
    def __init__(self, roles):
        self.roles = roles


def test_has_role_exact():
    user = DummyUser(["editor"])
    assert has_role(user, "roles", "editor")
    assert not has_role(user, "roles", "admin")


def test_has_role_list():
    user = DummyUser(["editor", "user"])
    assert has_role(user, "roles", ["user", "moderator"])
    assert not has_role(user, "roles", ["admin", "superadmin"])


def test_hierarchy_roles():
    user = DummyUser(["admin"])
    assert has_role(user, "roles", "user", use_hierarchy=True)
    assert not has_role(user, "roles", "superadmin", use_hierarchy=True)
