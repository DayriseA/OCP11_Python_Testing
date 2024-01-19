import pytest
import html
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


def test_showSummary_with_unregistered_email(client):
    data = {"email": "unregistered@test.com"}
    response = client.post("/showSummary", data=data)
    assert response.status_code == 302

    # Also check that redirected to the right page
    response = client.post("/showSummary", data=data, follow_redirects=True)
    flash_message = html.escape("Sorry, that email was not found.")
    assert response.status_code == 200
    assert flash_message in response.data.decode()


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
    response = client.get("/book/invalid_competition/invalid_club")
    assert response.status_code == 404
    assert b"Something went wrong" in response.data
    assert b"Welcome" in response.data


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
    assert response.status_code == 200
    assert b"Sorry, you don&#39;t have enough points" in response.data
    assert b"How many places" in response.data


def test_purchase_with_places_not_an_int(client, competitions_list, clubs_list):
    competition = competitions_list[0]["name"]
    club = clubs_list[0]["name"]
    places = "two"
    data = {"competition": competition, "club": club, "places": places}
    with pytest.raises(ValueError):
        client.post("/purchasePlaces", data=data)


def test_purchasePlaces_everything_ok(client, competitions_list, clubs_list):
    # define number of places and points for the test purpose
    competitions_list[0]["numberOfPlaces"] = 20
    clubs_list[0]["points"] = 10

    competition = competitions_list[0]["name"]
    club = clubs_list[0]["name"]
    places = 6
    data = {"competition": competition, "club": club, "places": places}
    response = client.post("/purchasePlaces", data=data)
    assert response.status_code == 200
    assert clubs_list[0]["points"] == 4
    assert competitions_list[0]["numberOfPlaces"] == 14
    assert b"Great - booking complete!" in response.data


def test_logout(client):
    response = client.get("/logout")
    assert response.status_code == 302

    # Also check that redirected to the right page
    response = client.get("/logout", follow_redirects=True)
    assert b"GUDLFT Registration" in response.data
    assert b"Please enter your secretary email to continue" in response.data
