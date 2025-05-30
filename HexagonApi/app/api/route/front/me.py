import app.service.account as as_
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
    login_method = auth.claims.get('firebase', {}).get('sign_in_provider', 'unknown')

    if name is None:
        name = email.split('@')[0]

    account = (await as_.signup(login_id, name, email, login_method, picture_url)).get()
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
    profile = (await as_.get_user_profile(auth.user)).get()
    return vr.UserProfile.of(profile)


@router.put(
    "/profile",
    responses={
        200: {"description": "Updated user profile."},
    },
)
async def update_profile(
    request: vq.UpdateProfileRequest = Body(...),
    auth: Authorized = Depends(with_user),
) -> vr.UserProfile:
    profile = (await as_.update_user_profile(
        auth.user, 
        bio=request.bio, 
        address=request.address
    )).get()
    return vr.UserProfile.of(profile)


@router.delete(
    "/withdraw",
    status_code=200,
)
async def delete_account(
    auth: Authorized = Depends(with_user)
) -> None:
    await as_.withdraw(auth.user)
    return None