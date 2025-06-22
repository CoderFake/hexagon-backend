import app.service.account as as_
from typing import Optional
from fastapi import Form, File, UploadFile
from app.api.commons import (
    APIRouter,
    Authorized,
    Depends,
    Query,
    Body,
    Response,
    vr,
    vq,
    with_token,
    with_user,
)

router = APIRouter()

@router.post(
    "/signup",
    status_code=201,
    responses={
        201: {"description": "Signed up user information."},
    },
)
async def signup(
    auth: Authorized = Depends(with_token),
) -> vr.User:
    login_id = auth.claims.get("sub", "")
    name = auth.claims.get("name", None)
    email = auth.claims.get("email", "")
    picture_url = auth.claims.get("picture", "")
    sign_in_provider = auth.claims.get('firebase', {}).get('sign_in_provider', 'unknown')

    if name is None:
        name = email.split('@')[0]

    account = (await as_.signup(login_id, name, email, sign_in_provider, picture_url)).get()
    return vr.User.of(account)


@router.get(
    "/auth",
    status_code=200,
)
async def get_me(
    auth: Authorized = Depends(with_user),
) -> None:
    await as_.login(auth.claims.get("sub", ""))
    return None


@router.get(
    "/profile",
    responses={
        200: {"description": "User profile information."},
    },
)
async def get_profile(
    auth: Authorized = Depends(with_user),
) -> vr.UserProfile:
    profile = (await as_.get_user_profile(auth.User)).get()
    return vr.UserProfile.of(profile)


@router.put(
    "/profile",
    responses={
        200: {"description": "Updated user profile."},
    },
)
async def update_profile(
    username: Optional[str] = Form(None),
    full_name: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    profile_picture: Optional[UploadFile] = File(None),
    auth: Authorized = Depends(with_user),
) -> vr.UserProfile:
    profile = (await as_.update_user_profile(
        auth.User,
        username=username,
        full_name=full_name,
        phone_number=phone_number,
        profile_picture_file=profile_picture,
        bio=bio, 
        address=address
    )).get()
    return vr.UserProfile.of(profile)


@router.delete(
    "/withdraw",
    status_code=200,
)
async def delete_account(
    auth: Authorized = Depends(with_user)
) -> None:
    await as_.withdraw(auth.User)
    return None