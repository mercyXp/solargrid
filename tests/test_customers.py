from app.models.customer import Customer


def test_create_customer(admin_session):
    rv = admin_session.post(
        "/customers/create",
        data={
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com",
            "phone": "0821112222",
            "address": "1 Test Rd",
            "customer_type": "Individual",
        },
        follow_redirects=True,
    )
    assert rv.status_code == 200
    assert Customer.query.filter_by(email="jane@example.com").first() is not None


def test_duplicate_email(admin_session, app):
    with app.app_context():
        admin_session.post(
            "/customers/create",
            data={
                "first_name": "A",
                "last_name": "B",
                "email": "dup@example.com",
                "phone": "0821112222",
                "address": "1 Test Rd",
                "customer_type": "Individual",
            },
        )
        rv = admin_session.post(
            "/customers/create",
            data={
                "first_name": "C",
                "last_name": "D",
                "email": "dup@example.com",
                "phone": "0823334444",
                "address": "2 Test Rd",
                "customer_type": "Individual",
            },
            follow_redirects=True,
        )
        assert b"already exists" in rv.data
