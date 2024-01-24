import pytest

from server import app, clubs, competitions

clubs_test_list = [
    {"name": "Simply Test", "email": "test@simplylift.co", "points": "13"},
    {"name": "Iron Test", "email": "test@irontemple.com", "points": "4"},
    {"name": "She Test", "email": "test@shelifts.co.uk", "points": "12"},
]

competitions_test_list = [
    {"name": "Spring Festival", "date": "2024-03-27 10:00:00", "numberOfPlaces": "25"},
    {"name": "Fall Classic", "date": "2024-10-22 13:30:00", "numberOfPlaces": "13"},
    {"name": "Winter Classic", "date": "2020-12-22 13:30:00", "numberOfPlaces": "15"},
]


@pytest.fixture
def client(mocker):
    # Mocking loadClubs and loadCompetitions for a controlled test environment
    # does not seem to work right now
    mocker.patch("server.loadClubs", return_value=clubs_test_list)
    mocker.patch("server.loadCompetitions", return_value=competitions_test_list)

    app.config.update({"TESTING": True})
    with app.test_client() as client:
        yield client


@pytest.fixture
def clubs_list(mocker):
    mocker.patch("server.loadClubs", return_value=clubs_test_list)
    return clubs


@pytest.fixture
def competitions_list(mocker):
    mocker.patch("server.loadCompetitions", return_value=competitions_test_list)
    return competitions


@pytest.fixture
def registered_mail(mocker):
    mocker.patch("server.loadClubs", return_value=clubs_test_list)
    email = clubs[0]["email"]
    return email
