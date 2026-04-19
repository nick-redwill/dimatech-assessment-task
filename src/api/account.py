from uuid import UUID

from sanic import Blueprint
from sanic.request import Request
from sanic.response import json
from sanic.exceptions import NotFound, BadRequest

from sqlalchemy.ext.asyncio import AsyncSession

from schemas.account import AccountCreate, AccountUpdate
from services import account as account_service

from utils.dependencies import require_admin, get_current_user, with_db_session
from utils.errors import handle_exceptions

account_bp = Blueprint("accounts", url_prefix="/accounts")


@account_bp.get("/my")
@handle_exceptions
@with_db_session
async def get_my_accounts(request: Request, db_session: AsyncSession):
    payload = get_current_user(request)
    accounts = await account_service.get_user_accounts(
        db_session, int(payload["sub"])
    )
    return json([a.model_dump(mode="json") for a in accounts])


@account_bp.get("/all")
@handle_exceptions
@with_db_session
async def list_accounts(request: Request, db_session: AsyncSession):
    require_admin(request)

    offset = int(request.args.get("offset", 0))
    limit = int(request.args.get("limit", 100))

    accounts = await account_service.get_all_accounts(
        db_session, offset=offset, limit=limit
    )
    return json([a.model_dump(mode="json") for a in accounts])


@account_bp.post("/create")
@handle_exceptions
@with_db_session
async def create_account(request: Request, db_session: AsyncSession):
    require_admin(request)

    account_in = AccountCreate.model_validate(request.json)
    account = await account_service.create_account(db_session, account_in)
    return json(account.model_dump(mode="json"), status=201)


@account_bp.get("/<account_id:uuid>")
@handle_exceptions
@with_db_session
async def get_account(
    request: Request, account_id: UUID, db_session: AsyncSession
):
    require_admin(request)
    account = await account_service.get_account(db_session, account_id)
    return json(account.model_dump(mode="json"))


@account_bp.patch("/<account_id:uuid>")
@handle_exceptions
@with_db_session
async def update_account(
    request: Request, account_id: UUID, db_session: AsyncSession
):
    require_admin(request)

    account_in = AccountUpdate.model_validate(request.json)
    account = await account_service.update_account(
        db_session, account_id, account_in
    )
    return json(account.model_dump(mode="json"))


@account_bp.delete("/<account_id:uuid>")
@handle_exceptions
@with_db_session
async def delete_account(
    request: Request, account_id: UUID, db_session: AsyncSession
):
    require_admin(request)

    deleted = await account_service.delete_account(db_session, account_id)
    if not deleted:
        raise NotFound(f"Account {account_id} not found")

    return json({"deleted": True})
