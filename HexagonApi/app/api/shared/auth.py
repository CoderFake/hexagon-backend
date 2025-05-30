from dataclasses import dataclass
from typing import Any, Optional, Generic, TypeVar
from fastapi import Header, Depends, HTTPException
from app.model.errors import Errors, Errorneous
from app.resources import context as r
import app.model.composite as c
from .errors import abort, abort_with


User = TypeVar('User')


@dataclass
class Authorized(Generic[User]):
    User: User
    claims: dict[str, Any]


class Authorization(Generic[User]):

    async def __call__(
        self,
        authorization: Optional[str] = Header(default=None),
    ) -> Authorized[User]:
        if not authorization:
            return Authorized(self.no_auth(), {})
        elif not authorization.startswith('Bearer '):
            abort(401, code=Errors.UNAUTHORIZED.name, Userssage="Invalid authorization header")

        claims = r.auth.verify(authorization[7:])

        User = await self.authorize(claims)

        return Authorized(User, claims)

    def no_auth(self) -> None:
        abort(401, code=Errors.UNAUTHORIZED.name, Userssage="Bearer token is not set")

    async def authorize(self, claims: dict[str, Any]) -> User:
        raise NotImplementedError()


class WithToken(Authorization[None]):
    async def authorize(self, claims: dict[str, Any]) -> None:
        return None


class WithUser(Authorization[c.User]):
    async def authorize(self, claims: dict[str, Any]) -> c.User:
        from app.service.account import login

        return (await login(claims['sub'])).or_else(abort_with(401, Errors.NOT_SIGNED_UP.name, "Not signed up yet"))


class MaybeUser(Authorization[Optional[c.User]]):
    def no_auth(self, *args) -> Optional[c.User]:
        return None

    async def authorize(self, claims: dict[str, Any]) -> Optional[c.User]:
        from app.service.account import login

        return (await login(claims['sub'])).or_else(self.no_auth)


#----------------------------------------------------------------
# Dependencies
#----------------------------------------------------------------
with_token = WithToken()
with_user = WithUser()
maybe_user = MaybeUser()