def test_auditor_cannot_create_customer(auditor_session):
    rv = auditor_session.get("/customers/create", follow_redirects=True)
    assert rv.status_code == 403


def test_auditor_can_view_customers(auditor_session):
    rv = auditor_session.get("/customers/")
    assert rv.status_code == 200


def test_unauthenticated_redirect(client):
    rv = client.get("/dashboard", follow_redirects=True)
    assert b"login" in rv.data.lower() or b"Sign In" in rv.data
