import pytest

from app import create_app
from app.extensions import db
from app.models.staff import Staff
from app.security.security_utils import hash_password


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        staff = Staff(
            username="testadmin",
            email="test@example.com",
            first_name="Test",
            last_name="Admin",
            role="Administrator",
            password_hash=hash_password("TestPass123"),
        )
        auditor = Staff(
            username="auditor",
            email="auditor@example.com",
            first_name="Test",
            last_name="Auditor",
            role="Auditor",
            password_hash=hash_password("TestPass123"),
        )
        db.session.add_all([staff, auditor])
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin_session(client):
    client.post("/login", data={"username": "testadmin", "password": "TestPass123"})
    return client


@pytest.fixture
def auditor_session(client):
    client.post("/login", data={"username": "auditor", "password": "TestPass123"})
    return client
