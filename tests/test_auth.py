from app.security.security_utils import hash_password, validate_password_strength, verify_password


def test_password_hashing():
    hashed = hash_password("TestPass123")
    assert verify_password("TestPass123", hashed)
    assert not verify_password("wrong", hashed)


def test_password_validation():
    valid, _ = validate_password_strength("TestPass123")
    assert valid
    valid, msg = validate_password_strength("short")
    assert not valid


def test_login_logout(client):
    rv = client.post("/login", data={"username": "testadmin", "password": "TestPass123"}, follow_redirects=True)
    assert rv.status_code == 200
    rv = client.get("/dashboard", follow_redirects=True)
    assert rv.status_code == 200
    rv = client.get("/logout", follow_redirects=True)
    assert b"Sign In" in rv.data or b"login" in rv.data.lower()


def test_invalid_login(client):
    rv = client.post("/login", data={"username": "testadmin", "password": "wrong"}, follow_redirects=True)
    assert b"Invalid" in rv.data
