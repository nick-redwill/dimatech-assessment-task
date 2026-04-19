from utils.signature import verify_signature

VALID_BODY = {
    "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
    "user_id": 1,
    "account_id": 1,
    "amount": 100,
    "signature": "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8",
}
SECRET = "gfdmhghif38yrf9ew0jkf32"


def test_valid_signature():
    assert verify_signature(VALID_BODY, SECRET) is True


def test_invalid_signature():
    body = {**VALID_BODY, "signature": "invalidsignature"}
    assert verify_signature(body, SECRET) is False


def test_wrong_secret():
    assert verify_signature(VALID_BODY, "wrongsecret") is False


def test_tampered_amount():
    body = {**VALID_BODY, "amount": 999}
    assert verify_signature(body, SECRET) is False


def test_tampered_user_id():
    body = {**VALID_BODY, "user_id": 2}
    assert verify_signature(body, SECRET) is False


def test_missing_signature():
    body = {k: v for k, v in VALID_BODY.items() if k != "signature"}
    assert verify_signature(body, SECRET) is False
