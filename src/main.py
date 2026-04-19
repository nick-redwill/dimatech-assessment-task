from sanic import Sanic

from api.user import user_bp
from api.account import account_bp
from api.transaction import transaction_bp

app = Sanic("app")
for bp in [user_bp, account_bp, transaction_bp]:
    app.blueprint(bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, dev=True)
