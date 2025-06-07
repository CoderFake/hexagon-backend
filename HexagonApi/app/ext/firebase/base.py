import json
from typing import Any, Optional, Literal
from functools import cached_property
import jwt
from pydantic import BaseModel
import requests
from cachecontrol import CacheControl
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend
import firebase_admin
import firebase_admin.auth


class FirebaseSettings(BaseModel):
    project_id: str


class FirebaseAuthSettings(FirebaseSettings):
    kind: Literal['auth']


class FirebaseAdminSettings(FirebaseSettings):
    kind: Literal['admin']
    name: Optional[str]
    api_key: str
    credential: str


class FirebaseAuth:
    """
    Class that defines Firebase's JWT authentication function.
    """
    def __init__(self, settings: FirebaseSettings) -> None:
        #: Required settings for authentication.
        self.settings = settings

    def verify(self, token: str) -> dict[str, Any]:
        """
        Verifies the token and retrieves the claims.

        Args:
            token: Token.
        Returns:
            Claims.
        """
        kid = jwt.get_unverified_header(token).get('kid', '')
        key = kid and self.keys().get(kid, None)
        if not key:
            raise ValueError(f"Invalid firebase kid: {kid}")

        cert = load_pem_x509_certificate(key.encode(), default_backend())

        return jwt.decode(
            token,
            cert.public_key(), # type: ignore
            algorithms=['RS256'],
            audience=self.settings.project_id,
            issuer=f"https://securetoken.google.com/{self.settings.project_id}",
            leeway=30,
        )

    def keys(self, cache = CacheControl(requests.session())) -> dict[str, str]:
        return cache.get('https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com').json()


class FirebaseAdmin:
    """
    Class that defines Firebase's management function.
    """
    def __init__(self, settings: FirebaseAdminSettings) -> None:
        #: Required settings for management.
        self.settings = settings
        #: Authentication function.
        self.auth = FirebaseAuth(settings)

    @cached_property
    def app(self) -> firebase_admin.App:
        """
        Gets the Firebase application associated with the set name.
        """
        try:
            return firebase_admin.get_app(self.settings.name) if self.settings.name else firebase_admin.get_app()
        except ValueError:
            cred = firebase_admin.credentials.Certificate(self.settings.credential)
            return firebase_admin.initialize_app(cred, name=self.settings.name) if self.settings.name else firebase_admin.initialize_app(cred)

    def generate(self, sub: str, **claims: Any) -> tuple[str, str]:
        """
        Generates a pair of access token and refresh token.

        Args:
            sub: The `sub` attribute of the claim.
            claims: Additional claims.
        Returns:
            A pair of access token and refresh token.
        """
        custom_token = firebase_admin.auth.create_custom_token(sub, app=self.app, developer_claims=claims).decode()

        r = requests.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={self.settings.api_key}",
            headers = {'Content-type': 'application/json'},
            data = json.dumps(dict(
                token = custom_token,
                returnSecureToken = True,
            ))
        )

        return r.json()['idToken'],  r.json()['refreshToken']

    def get_users(self, uids: list[str]) -> list[firebase_admin.auth.UserRecord]:
        """
        Gets the user from UID.

        Args:
            uids: UID list.
        Returns:
            User list.
        """
        ids = [firebase_admin.auth.UidIdentifier(uid) for uid in uids]
        res = firebase_admin.auth.get_users(ids, app=self.app)
        if len(res.users) == 0:
            raise ValueError(f"User not found in firebase: {uids}")
        return res.users
