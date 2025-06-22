import enum
from enum import IntEnum


class LoginMethod(enum.Enum):
    PASSWORD = "password"
    GOOGLE = "google"
    GITHUB = "github"
    FACEBOOK = "facebook"
    
    @classmethod
    def from_firebase_provider(cls, sign_in_provider: str) -> str:
        """Map Firebase sign_in_provider to LoginMethod enum value"""
        provider_map = {
            'google.com': cls.GOOGLE.value,
            'password': cls.PASSWORD.value,
            'github.com': cls.GITHUB.value,
            'facebook.com': cls.FACEBOOK.value
        }
        return provider_map.get(sign_in_provider, 'unknown')