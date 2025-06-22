from typing import Optional

import httpx
from urllib.parse import urlparse
from uuid import uuid4
from app.config import environment
from app.ext.storage.base import Storage
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
from .types import LoginMethod
from .utils.account import download_and_save_profile_picture


@service
async def signup(
    login_id: str,
    name: str,
    email: str,
    login_method: str,
    picture_url:  Optional[str]=None
) -> Maybe[c.User]:

    user = await r.tx.scalar(
        select(m.User).where(
            or_(m.User.firebase_id == login_id)
        ).with_for_update()
    )
    
    now = datetime.now()
    
    if user is None:
        if name:
            username = name.lower()

        existing_username = await r.tx.scalar(
            select(m.User).where(m.User.username == username)
        )
        if existing_username:
            username = f"{username}_{str(uuid4())[:8]}"
        
        user = await r.tx.scalar(
            insert(m.User).returning(m.User),
            dict(
                id=str(uuid4()),
                username=username,
                email=email,
                full_name=name,
                firebase_id=login_id,
                login_method=login_method,
                is_active=True,
                date_joined=now,
                last_login=now,
            ),
        )

        if user.login_method == LoginMethod.GOOGLE.value:
            picture_url = await download_and_save_profile_picture(picture_url, user.id)
        
        await r.tx.scalar(
            insert(m.UserProfile).returning(m.UserProfile),
            dict(
                id=str(uuid4()),
                user_id=user.id,
                profile_picture=picture_url,
                created_at=now,
                updated_at=now,
            ),
        )
    else:
        if not user.is_active:
            return Errors.UNAUTHORIZED

        await r.tx.execute(
            update(m.User)
            .where(m.User.id == user.id)
            .values(
                last_login=now,
            )
        )

        if picture_url and user.profile:
            if not user.profile.profile_picture or user.login_method == LoginMethod.GOOGLE.value:
                new_picture_url = await download_and_save_profile_picture(picture_url, user.id)
                await r.tx.execute(
                    update(m.UserProfile)
                    .where(m.UserProfile.user_id == user.id)
                    .values(
                        profile_picture=new_picture_url,
                        updated_at=now
                    )
                )
    
    await r.tx.commit()
    return await r.tx.get(c.User, user.id)


@service
async def login(login_id: str) -> Maybe[c.User]:
    if not login_id:
        return Errors.INVALID_REQUEST
    
    user = await r.tx.scalar(
        select(m.User).where(
            m.User.firebase_id == login_id
        )
    )
    
    if user is None or not user.is_active:
        return Errors.UNAUTHORIZED

    now = datetime.now()
    await r.tx.execute(
        update(m.User)
        .where(m.User.id == user.id)
        .values( last_login=now)
    )
    
    await r.tx.commit()


@service
async def get_user_profile(user: c.User) -> Maybe[c.UserProfile]:
    profile = await r.tx.scalar(
        select(m.UserProfile).where(m.UserProfile.user_id == user.id)
    )
    
    if profile is None:
        now = datetime.now()
        profile = await r.tx.scalar(
            insert(m.UserProfile).returning(m.UserProfile),
            dict(
                id=str(uuid4()),
                user_id=user.id,
                created_at=now,
                updated_at=now,
            ),
        )
        await r.tx.commit()
    
    return await r.tx.get(c.UserProfile, profile.id)


@service
async def update_user_profile(user: c.User, bio: str = None, address: str = None) -> Maybe[c.UserProfile]:
    profile = await r.tx.scalar(
        select(m.UserProfile).where(m.UserProfile.user_id == user.id)
    )
    
    now = datetime.now()
    update_data = {"updated_at": now}
    
    if bio is not None:
        update_data["bio"] = bio
    if address is not None:
        update_data["address"] = address
    
    if profile is None:
        profile = await r.tx.scalar(
            insert(m.UserProfile).returning(m.UserProfile),
            dict(
                id=str(uuid4()),
                user_id=user.id,
                bio=bio,
                address=address,
                created_at=now,
                updated_at=now,
            ),
        )
    else:
        await r.tx.execute(
            update(m.UserProfile)
            .where(m.UserProfile.user_id == user.id)
            .values(**update_data)
        )
    
    await r.tx.commit()
    return await r.tx.get(c.UserProfile, profile.id)


@service
async def withdraw(user: c.User):
    if user.profile and user.profile.profile_picture:
        try:
            picture_url = user.profile.profile_picture
            if picture_url.startswith('http'):
                storage_path = picture_url.split('/')[-1]
                storage_path = f"profile_pictures/{storage_path}"
            else:
                storage_path = user.profile.profile_picture
            
            r.storage.delete(storage_path)
        except Exception as e:
            r.logger.warning(f"Failed to delete profile picture", exc_info=e)

    await r.tx.execute(
        delete(m.UserProfile).where(m.UserProfile.user_id == user.id)
    )

    await r.tx.execute(
        delete(m.StudentCourseEnrollment).where(m.StudentCourseEnrollment.user_id == user.id)
    )

    now = datetime.now()
    await r.tx.execute(
        update(m.User)
        .where(m.User.id == user.id)
        .values(is_active=False, last_login=now)
    )
    
    await r.tx.commit()
