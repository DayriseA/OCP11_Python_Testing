import pytest

from server import app, clubs, competitions


@pytest.fixture
def client():
    app.config.update({"TESTING": True})
    with app.test_client() as client:
        yield client


@pytest.fixture
def clubs_list():
    return clubs


@pytest.fixture
def competitions_list():
    return competitions


@pytest.fixture
def registered_mail():
    email = clubs[0]["email"]
    return email
