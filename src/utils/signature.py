import hashlib


def verify_signature(body: dict, secret: str) -> bool:
    signature = body.get("signature")
    payload = {k: v for k, v in body.items() if k != "signature"}
    concat = "".join(str(payload[k]) for k in sorted(payload.keys())) + secret
    expected = hashlib.sha256(concat.encode()).hexdigest()
    return signature == expected
