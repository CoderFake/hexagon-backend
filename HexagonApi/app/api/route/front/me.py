import app.service.account as as_
from app.api.commons import (
    APIRouter,
    Authorized,
    Depends,
    Query,
    vr,
    with_token,
    with_user,
)

router = APIRouter()


@router.post(
    "",
    status_code=201,
    responses={
        201: {"description": "Signed up user information."},
    },
)
async def signup(
    auth: Authorized = Depends(with_token),
) -> vr.Me:
    """
    Perform signup.
    """
    login_id = auth.claims.get("sub", "")
    name = auth.claims.get("name", "")
    email = auth.claims.get("email", "")
    account = (await as_.signup(login_id, name, email)).get()
    return vr.Me.of(account)


@router.get(
    "",
    responses={
        200: {"description": "User information."},
    },
)
async def login(
    auth: Authorized = Depends(with_user),
) -> vr.Me:
    """
    Perform login.
    """
    login_id = auth.claims.get("sub", "")
    account = (await as_.login(login_id)).get()

    return vr.Me.of(account)


@router.delete(
    "",
    status_code=204,
    responses={
        204: {"description": "Processing successful."},
    },
)
async def withdraw(
    auth: Authorized = Depends(with_user),
):
    """
    Withdraw from the service.

    Along with account information, all existing data and files will be deleted.
    """
    await as_.withdraw(auth.me)


@router.get(
    "/total-point",
    responses={
        200: {"description": "User information."},
    },
)
async def total_point(
    auth: Authorized = Depends(with_user),
):
    login_id = auth.claims.get("sub", "")

    return await as_.total_points(login_id)


@router.get(
    "/point-detail",
    status_code=200,
    responses={
        200: {"description": "User point history information."},
    },
)
async def point_history(
    auth: Authorized = Depends(with_user),
    page: int = Query(default=1, ge=1, description="Page number, starting from 1"),
    size: int = Query(default=30, ge=1, le=100, description="Number of items per page"),
):
    login_id = auth.claims.get("sub", "")
    if page < 1:
        page = 1
    return await as_.point_history(login_id, page, size)
