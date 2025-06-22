import asyncio
import logging
import sys
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from types import ModuleType
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Generic,
    Optional,
    Protocol,
    TypeVar,
    Union,
)
from uuid import uuid4

from app.config import ApplicationSettings
from app.ext.firebase.base import (
    FirebaseAdmin,
    FirebaseAuth,
    FirebaseAuthSettings,
)
from app.ext.storage.base import Storage
from app.ext.email.base import GmailEmailService
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from typing_extensions import Self


class Closeable(Protocol):
    async def close(self, exc: Optional[Exception]):
        ...


T = TypeVar("T", bound=Closeable)


@dataclass
class Resources:
    db: AsyncEngine
    storage: Storage
    firebase: Union[FirebaseAuth, FirebaseAdmin]
    email: GmailEmailService
    logger: logging.Logger

    def open(self) -> "ResourceSession":
        return ResourceSession(
            id=str(uuid4()),
            db=async_sessionmaker(self.db, expire_on_commit=False)(),
            storage=self.storage,
            firebase=self.firebase,
            email=self.email,
            logger=self.logger,
        )


@dataclass
class ResourceSession(Closeable):
    id: str
    db: AsyncSession
    storage: Storage
    firebase: Union[FirebaseAuth, FirebaseAdmin]
    email: GmailEmailService
    logger: logging.Logger

    @property
    def tx(self) -> AsyncSession:
        if not self.db.sync_session.in_transaction:
            self.db.sync_session.begin()
        return self.db

    _status: bool = field(init=False)

    def __post_init__(self):
        self._status = True

    def fail(self) -> None:
        self._status = False

    async def close(self, exc: Optional[Exception]):
        status = self._status and exc is None

        try:
            if self.db.in_transaction():
                if status:
                    self.logger.debug(f"Commit transaction: {self.id}")
                    await self.db.commit()
                else:
                    self.logger.debug(f"Rollback transaction: {self.id}")
                    await self.db.rollback()
        except Exception as e:
            self.logger.warning(
                "Exception was thrown in closing transaction.", exc_info=e
            )
        finally:
            await self.db.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close(exc_value)

    @property
    def auth(self) -> FirebaseAuth:
        return (
            self.firebase
            if isinstance(self.firebase, FirebaseAuth)
            else self.firebase.auth
        )


_context = ContextVar[ResourceSession]("_context")


async def configure(
    settings: ApplicationSettings, logger: logging.Logger
) -> tuple[Resources, Callable]:
    engine = create_async_engine(
        settings.db.dsn,
        echo_pool=settings.db.echo_pool and "debug",
    )
    if settings.db.echo:
        engine.echo = True

    import app.ext.storage.local
    import app.ext.storage.s3
    import app.ext.storage.minio

    logger.info(f"Storage URL from settings: {settings.storage.url}")
    storage = Storage.of(settings.storage.url, public_url=settings.storage.public_url)
    if storage is None:
        raise ValueError(f"Invalid URL for storage: {settings.storage.url}")
    
    logger.info(f"Storage initialized: {type(storage).__name__}")

    firebase = (
        FirebaseAuth(settings.firebase)
        if isinstance(settings.firebase, FirebaseAuthSettings)
        else FirebaseAdmin(settings.firebase)
    )
    
    email_service = GmailEmailService(settings.email)
    logger.info(f"Email service initialized with host: {settings.email.host}")

    resources = Resources(
        db=engine,
        storage=storage,
        firebase=firebase,
        email=email_service,
        logger=logger,
    )

    async def call_session(
        next: Callable[[ResourceSession], Awaitable[Any]]
    ) -> Callable[[ResourceSession], Awaitable[Any]]:
        session = resources.open()
        token = _context.set(session)
        async with session:
            try:
                return await next(session)
            except:
                session.fail()
                raise
            finally:
                _context.reset(token)

    return resources, call_session


class ContextualResources:
    @classmethod
    def of(
        cls, resources: Resources, event_loop: Optional[asyncio.AbstractEventLoop]
    ) -> "ContextualResources":
        return ContextualResources(_context, resources, event_loop)

    def __init__(
        self,
        cxt: ContextVar[ResourceSession],
        resources: Resources,
        event_loop: Optional[asyncio.AbstractEventLoop],
    ) -> None:
        self.cxt = cxt
        self.resources = resources
        self.event_loop = event_loop
        self.token: Optional[Token] = None

    def __enter__(self) -> ResourceSession:
        session = self.resources.open()
        self.token = self.cxt.set(session)
        return session

    def __exit__(self, exc_type, exc_value, traceback):
        value = self.cxt.get()
        try:

            async def close():
                await value.close(exc_value)

            if self.event_loop:
                self.event_loop.run_until_complete(close())
            else:
                asyncio.run(close())
        finally:
            if self.token is not None:
                self.cxt.reset(self.token)

    async def __aenter__(self) -> ResourceSession:
        session = self.resources.open()
        self.token = self.cxt.set(session)
        return session

    async def __aexit__(self, exc_type, exc_value, traceback):
        value = self.cxt.get()
        try:
            await value.close(exc_value)
        finally:
            if self.token is not None:
                self.cxt.reset(self.token)


class ContextAccessor(Generic[T]):
    def __init__(self, cxt: ContextVar[T]) -> None:
        self.cxt = cxt

    def __getattr__(self, name):
        return getattr(self.cxt.get(), name)


class Module(ModuleType):
    """
    Module accessor.
    """

    accessor = ContextAccessor[ResourceSession](_context)

    @property
    def context(self) -> ResourceSession:
        return Module.accessor  # type: ignore


sys.modules[__name__].__class__ = Module
if TYPE_CHECKING:
    context: ResourceSession
