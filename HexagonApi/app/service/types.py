import enum
from enum import IntEnum


class LoginMethod(enum.Enum):
    PASSWORD = "password"
    GOOGLE = "google"
    GITHUB = "github"
    FACEBOOK = "facebook"