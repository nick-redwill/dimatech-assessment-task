from decimal import Decimal
from uuid import UUID

from sanic import Blueprint
from sanic.request import Request
from sanic.response import json
from sanic.exceptions import NotFound, BadRequest

from sqlalchemy.ext.asyncio import AsyncSession

from services import transaction as transaction_service
from utils.dependencies import require_admin, get_current_user, with_db_session
from utils.signature import verify_signature
from utils.errors import handle_exceptions

from settings import WEBHOOK_SECRET

transaction_bp = Blueprint("transactions", url_prefix="/transactions")


@transaction_bp.get("/my")
@handle_exceptions
@with_db_session
async def get_my_transactions(request: Request, db_session: AsyncSession):
    payload = get_current_user(request)
    offset = int(request.args.get("offset", 0))
    limit = int(request.args.get("limit", 100))

    transactions = await transaction_service.get_user_transactions(
        db_session, int(payload["sub"]), offset=offset, limit=limit
    )

    return json([t.model_dump(mode="json") for t in transactions])


@transaction_bp.get("/all")
@handle_exceptions
@with_db_session
async def list_transactions(request: Request, db_session: AsyncSession):
    require_admin(request)

    offset = int(request.args.get("offset", 0))
    limit = int(request.args.get("limit", 100))
    transactions = await transaction_service.get_all_transactions(
        db_session, offset=offset, limit=limit
    )

    return json([t.model_dump(mode="json") for t in transactions])


@transaction_bp.get("/<transaction_id:uuid>")
@handle_exceptions
@with_db_session
async def get_transaction(
    request: Request, transaction_id: UUID, db_session: AsyncSession
):
    require_admin(request)

    transaction = await transaction_service.get_transaction(
        db_session, transaction_id
    )
    return json(transaction.model_dump(mode="json"))


@transaction_bp.post("/webhook")
@handle_exceptions
@with_db_session
async def webhook(request: Request, db_session: AsyncSession):
    body = request.json or {}

    required = {
        "transaction_id",
        "account_id",
        "user_id",
        "amount",
        "signature",
    }
    if missing := required - body.keys():
        raise BadRequest(f"Missing fields: {missing}")

    if not verify_signature(body, WEBHOOK_SECRET):
        raise BadRequest("Invalid signature")

    transaction = await transaction_service.process_webhook(
        db_session,
        transaction_id=body["transaction_id"],
        account_id=UUID(str(body["account_id"])),
        user_id=int(body["user_id"]),
        amount=Decimal(str(body["amount"])),
    )
    return json(transaction.model_dump(mode="json"), status=201)
