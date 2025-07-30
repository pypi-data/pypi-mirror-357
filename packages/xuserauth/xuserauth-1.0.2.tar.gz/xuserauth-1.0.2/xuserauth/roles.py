from typing import Any, List, Union

# Define a simple role hierarchy (lower index = higher privilege)
ROLE_HIERARCHY = [
    "superadmin",
    "admin",
    "moderator",
    "editor",
    "user",
    "guest"
]


def _get_role_rank(role: str) -> int:
    try:
        return ROLE_HIERARCHY.index(role)
    except ValueError:
        return len(ROLE_HIERARCHY)  # lowest rank for unknown roles


def has_role(
    user: Any,
    role_field: str,
    required_role: Union[str, List[str]],
    use_hierarchy: bool = False
) -> bool:
    """
    Check if a user has the required role(s).

    Args:
        user: The user object.
        role_field: Attribute name that stores the user's roles.
        required_role: A role or list of roles to check.
        use_hierarchy: If True, allows higher roles to satisfy lower ones.

    Returns:
        bool: Whether the user has the required role(s).
    """
    user_roles = getattr(user, role_field, [])
    if isinstance(user_roles, str):
        user_roles = [user_roles]

    if not user_roles:
        return False

    if isinstance(required_role, str):
        required_role = [required_role]

    if use_hierarchy:
        user_ranks = [_get_role_rank(role) for role in user_roles]
        required_ranks = [_get_role_rank(role) for role in required_role]
        return min(user_ranks, default=len(ROLE_HIERARCHY)) <= min(required_ranks)

    return any(role in user_roles for role in required_role)
