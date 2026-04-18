from schemas.user import UserRead
from schemas.account import AccountRead
from schemas.transaction import TransactionRead


class AccountRel(AccountRead):
    user: UserRead | None = None


class UserRel(UserRead):
    accounts: list[AccountRead] = []


class TransactionRel(TransactionRead):
    account: AccountRead | None = None
