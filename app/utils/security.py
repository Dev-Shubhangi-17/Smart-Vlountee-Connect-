"""Security helper functions."""

import re


def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate that password meets minimum security standards."""
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, ""


def validate_email_format(email: str) -> bool:
    """Validate email format."""
    if not email:
        return False
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))
