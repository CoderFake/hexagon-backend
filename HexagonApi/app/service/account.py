from urllib.parse import urlparse
from uuid import uuid4

from app.config import environment
from app.ext.storage.s3 import S3Storage
from sqlalchemy import and_
from sqlalchemy import (
    delete,
    func,
    insert,
    literal_column,
    not_,
    or_,
    select,
    union_all,
    update,
)
from .commons import Errors, Maybe, c, datetime, m, r, service

s3_url = environment().settings.storage.url
if s3_url.startswith("s3://"):
    parsed_url = urlparse(s3_url)
    s3_storage = S3Storage(parsed_url)


@service
async def signup(login_id: str, name: str, email: str) -> Maybe[c.Me]:
    """
    Signs up and registers user information. Does not raise an error even if already signed up.

    Args:
        login_id: Login ID.
    Returns:
        Signup user information.
    """

    account = await r.tx.scalar(
        select(m.Account).where(m.Account.login_id == login_id).with_for_update()
    )

    now = datetime.now()

    if account is None:
        account = await r.tx.scalar(
            insert(m.Account).returning(m.Account),
            dict(
                id=str(uuid4()),
                login_id=login_id,
                name=name,
                email=email,
                created_at=now,
                modified_at=now,
                last_login=now,
            ),
        )

    return await r.tx.get(c.Me, account.id)


@service
async def login(login_id: str) -> Maybe[c.Me]:
    """
    Logs in.

    Args:
        login_id: Login ID.
    Returns:
        User information.
    """
    account = await r.tx.scalar(select(m.Account).where(m.Account.login_id == login_id))
    now = datetime.now()

    if account is None:
        return Errors.UNAUTHORIZED

    await r.tx.execute(
        update(m.Account).where(m.Account.login_id == login_id).values(last_login=now)
    )

    if account.is_deleted:
        await r.tx.execute(
            update(m.Account)
            .where(m.Account.login_id == login_id)
            .values(
                created_at=now,
                modified_at=now,
                is_deleted=False,
            )
        )

    await r.tx.commit()

    return await r.tx.get(c.Me, account.id)


@service
async def withdraw(me: c.Me):
    """
    Deletes user information and related data together.

    Args:
        me: Authenticated user.
    """
    resume = await r.tx.scalar(
        select(m.ResumeItem).where(m.ResumeItem.account_id == me.id)
    )

    path = resume and resume.photo

    if path:
        try:
            s3_storage.delete(str(resume.photo))
        except Exception as e:
            r.logger.warning(f"Failed to delete resume photo at {path}", exc_info=e)

    await r.tx.execute(delete(m.ResumeItem).where(m.ResumeItem.account_id == me.id))

    await r.tx.execute(delete(m.CareerItem).where(m.CareerItem.account_id == me.id))

    await r.tx.execute(delete(m.EprintItem).where(m.EprintItem.account_id == me.id))

    now = datetime.now()
    await r.tx.execute(
        update(m.Point)
        .where(and_(m.Point.account_id == me.id, m.Point.expiration_date >= now))
        .values(modified_at=now, expiration_date=now)
    )

    await r.tx.execute(
        update(m.Account)
        .where(m.Account.id == me.id)
        .values(is_deleted=True, modified_at=now)
    )

    await r.tx.commit()
