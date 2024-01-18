import pytest
from server import loadClubs, loadCompetitions

REGISTERED_MAIL = "john@simplylift.co"


def test_loadClubs():
    clubs = loadClubs()
    assert isinstance(clubs, list)
    assert len(clubs) > 0
    for club in clubs:
        assert "name" in club
        assert "email" in club
        assert "points" in club


def test_loadCompetitions():
    competitions = loadCompetitions()
    assert isinstance(competitions, list)
    assert len(competitions) > 0
    for competition in competitions:
        assert "name" in competition
        assert "numberOfPlaces" in competition


def test_index_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to the GUDLFT Registration Portal" in response.data


def test_showSummary_with_registered_email(client, registered_mail):
    response = client.post("/showSummary", data={"email": registered_mail})
    assert response.status_code == 200
    assert b"Welcome" in response.data
    assert b"Book Places" in response.data


# This passes currently but we don't want it like this in a TDD approach
def test_showSummary_with_unregistered_email(client):
    with pytest.raises(IndexError):
        client.post("/showSummary", data={"email": "unregistered@test.com"})


# This is the TDD approach
# def test_showSummary_with_unregistered_email(client):
#     response = client.post("/showSummary", data={"email": "unregistered@test.com"})
#     assert response.status_code == 403


def test_get_method_not_allowed_on_showSummary(client):
    response = client.get("/showSummary")
    assert response.status_code == 405


def test_book_with_valid_parameters(client, competitions_list, clubs_list):
    competition = competitions_list[0]["name"]
    club = clubs_list[0]["name"]
    response = client.get(f"/book/{competition}/{club}")
    assert response.status_code == 200
    assert b"Places available" in response.data
    assert competition in response.data.decode()


# def test_book_with_valid_parameters_but_user_not_logged_in(client):
#     """If user not logged in, redirect to index"""
#     pass


def test_book_with_invalid_parameters(client):
    with pytest.raises(IndexError):
        client.get("/book/invalid_competition/invalid_club")


# TDD approach / wanted behaviour
# def test_book_with_invalid_parameters(client):
#     response = client.get("/book/invalid_competition/invalid_club")
#     assert response.status_code == 302
#     assert b"Something went wrong" in response.data
#     assert b"Welcome" in response.data


def test_get_method_not_allowed_on_purchasePlaces(client):
    response = client.get("/purchasePlaces")
    assert response.status_code == 405


def test_purchase_more_than_12_places(client, competitions_list, clubs_list):
    competition = competitions_list[0]["name"]
    club = clubs_list[0]["name"]
    places = 13
    data = {"competition": competition, "club": club, "places": places}
    response = client.post("/purchasePlaces", data=data)
    assert response.status_code == 400


def test_purchase_more_places_than_available(client, competitions_list, clubs_list):
    competition = competitions_list[0]["name"]
    club = clubs_list[0]["name"]
    places = int(competitions_list[0]["numberOfPlaces"]) + 1
    data = {"competition": competition, "club": club, "places": places}
    response = client.post("/purchasePlaces", data=data)
    assert response.status_code == 400


def test_purchase_with_not_enough_points(client, competitions_list, clubs_list):
    competition = competitions_list[0]["name"]
    club = clubs_list[0]["name"]
    # we have a ratio of 1 point per place
    places = int(clubs_list[0]["points"]) + 1
    data = {"competition": competition, "club": club, "places": places}
    response = client.post("/purchasePlaces", data=data)
    assert response.status_code == 400


def test_purchase_with_places_not_an_int(client, competitions_list, clubs_list):
    competition = competitions_list[0]["name"]
    club = clubs_list[0]["name"]
    places = "two"
    data = {"competition": competition, "club": club, "places": places}
    with pytest.raises(ValueError):
        client.post("/purchasePlaces", data=data)


def test_logout(client):
    response = client.get("/logout")
    assert response.status_code == 302

    # Also check that redirected to the right page
    response = client.get("/logout", follow_redirects=True)
    assert b"GUDLFT Registration" in response.data
    assert b"Please enter your secretary email to continue" in response.data