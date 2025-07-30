from xuserauth.hashing import password_hash, verify_password


def test_password_hashing_and_verification():
    raw = "mysecret"
    hashed = password_hash(raw)
    assert hashed != raw
    assert verify_password(raw, hashed)
