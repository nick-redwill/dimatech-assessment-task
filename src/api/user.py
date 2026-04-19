from sanic import Blueprint
from sanic.request import Request
from sanic.response import json
from sanic.exceptions import NotFound, Unauthorized, BadRequest

from sqlalchemy.ext.asyncio import AsyncSession

from schemas.user import UserCreate, UserUpdate
from services import user as user_service
from utils.dependencies import require_admin, get_current_user, with_db_session
from utils.errors import handle_exceptions

user_bp = Blueprint("users", url_prefix="/users")


@user_bp.post("/login")
@handle_exceptions
@with_db_session
async def login(request: Request, db_session: AsyncSession):
    body = request.json or {}
    email = body.get("email")
    password = body.get("password")

    if not email or not password:
        raise BadRequest("email and password are required")

    token = await user_service.authenticate_user(db_session, email, password)

    return json({"access_token": token, "token_type": "bearer"})


@user_bp.get("/me")
@handle_exceptions
@with_db_session
async def get_me(request: Request, db_session: AsyncSession):
    payload = get_current_user(request)

    user = await user_service.get_user(db_session, int(payload["sub"]))
    return json(user.model_dump(mode="json"))


@user_bp.get("/all")
@handle_exceptions
@with_db_session
async def list_users(request: Request, db_session: AsyncSession):
    require_admin(request)

    offset = int(request.args.get("offset", 0))
    limit = int(request.args.get("limit", 100))

    users = await user_service.get_all_users(
        db_session, offset=offset, limit=limit
    )
    return json([u.model_dump(mode="json") for u in users])


@user_bp.post("/create")
@handle_exceptions
@with_db_session
async def create_user(request: Request, db_session: AsyncSession):
    require_admin(request)

    try:
        user_in = UserCreate.model_validate(request.json)
    except Exception as e:
        raise BadRequest(str(e))

    user = await user_service.create_user_with_default_account(
        db_session, user_in
    )
    return json(user.model_dump(mode="json"), status=201)


@user_bp.get("/<user_id:int>")
@handle_exceptions
@with_db_session
async def get_user(request: Request, user_id: int, db_session: AsyncSession):
    require_admin(request)

    user = await user_service.get_user(db_session, user_id)
    return json(user.model_dump(mode="json"))


@user_bp.patch("/<user_id:int>")
@handle_exceptions
@with_db_session
async def update_user(
    request: Request, user_id: int, db_session: AsyncSession
):
    require_admin(request)

    user_in = UserUpdate.model_validate(request.json)
    user = await user_service.update_user(db_session, user_id, user_in)
    return json(user.model_dump(mode="json"))


@user_bp.delete("/<user_id:int>")
@handle_exceptions
@with_db_session
async def delete_user(
    request: Request, user_id: int, db_session: AsyncSession
):
    require_admin(request)

    deleted = await user_service.delete_user(db_session, user_id)
    if not deleted:
        raise NotFound(f"User {user_id} not found")

    return json({"deleted": True})
