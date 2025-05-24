from dataclasses import dataclass
from typing import Any, Optional, Generic, TypeVar
from fastapi import Header, Depends, HTTPException
from app.model.errors import Errors, Errorneous
from app.resources import context as r
import app.model.composite as c
from .errors import abort, abort_with


Me = TypeVar('Me')


@dataclass
class Authorized(Generic[Me]):
    me: Me
    claims: dict[str, Any]


class Authorization(Generic[Me]):
    """
    Type of dependency object that performs Bearer authentication.
    """
    async def __call__(
        self,
        authorization: Optional[str] = Header(default=None),
    ) -> Authorized[Me]:
        """
        Performs Bearer authentication against the Authorization header and returns an authentication object with the obtained user information.

        Args:
            authorization: Authorization header.
        Returns:
            Authentication object.
        """
        if not authorization:
            return Authorized(self.no_auth(), {})
        elif not authorization.startswith('Bearer '):
            abort(401, code=Errors.UNAUTHORIZED.name, message="Invalid authorization header")

        claims = r.auth.verify(authorization[7:])

        me = await self.authorize(claims)

        return Authorized(me, claims)

    def no_auth(self) -> Me:
        abort(401, code=Errors.UNAUTHORIZED.name, message="Bearer token is not set")

    async def authorize(self, claims: dict[str, Any]) -> Me:
        raise NotImplementedError()


class WithToken(Authorization[None]):
    async def authorize(self, claims: dict[str, Any]) -> None:
        return None


class WithUser(Authorization[c.Me]):
    async def authorize(self, claims: dict[str, Any]) -> c.Me:
        from app.service.account import login

        return (await login(claims['sub'])).or_else(abort_with(401, Errors.NOT_SIGNED_UP.name, "Not signed up yet"))


class MaybeUser(Authorization[Optional[c.Me]]):
    def no_auth(self, *args) -> Optional[c.Me]:
        return None

    async def authorize(self, claims: dict[str, Any]) -> Optional[c.Me]:
        from app.service.account import login

        return (await login(claims['sub'])).or_else(self.no_auth)


#----------------------------------------------------------------
# Dependencies
#----------------------------------------------------------------
with_token = WithToken()
with_user = WithUser()
maybe_user = MaybeUser()
