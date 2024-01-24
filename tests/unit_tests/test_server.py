import pytest
import html
from server import loadClubs, loadCompetitions, is_date_str_in_past


class TestServer:
    """Tests for the different routes in the server."""

    def test_index_route(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert b"Welcome to the GUDLFT Registration Portal" in response.data

    def test_showSummary_with_registered_email(self, client, registered_mail):
        response = client.post("/showSummary", data={"email": registered_mail})
        print()
        print(registered_mail)  # not the mocked one...
        assert response.status_code == 200
        assert b"Welcome" in response.data
        assert b"Book Places" in response.data

    def test_showSummary_with_unregistered_email(self, client):
        data = {"email": "unregistered@test.com"}
        response = client.post("/showSummary", data=data)
        assert response.status_code == 302

        # Also check that redirected to the right page
        response = client.post("/showSummary", data=data, follow_redirects=True)
        flash_message = html.escape("Sorry, that email was not found.")
        assert response.status_code == 200
        assert flash_message in response.data.decode()

    def test_get_method_not_allowed_on_showSummary(self, client):
        response = client.get("/showSummary")
        assert response.status_code == 405

    def test_book_with_valid_parameters(self, client, competitions_list, clubs_list):
        competition = competitions_list[0]["name"]
        club = clubs_list[0]["name"]
        print()
        print(clubs_list)  # not the mocked list...
        response = client.get(f"/book/{competition}/{club}")
        assert response.status_code == 200
        assert b"Places available" in response.data
        assert competition in response.data.decode()

    def test_book_with_invalid_parameters(self, client):
        response = client.get("/book/invalid_competition/invalid_club")
        assert response.status_code == 404
        assert b"Something went wrong" in response.data
        assert b"Welcome" in response.data

    def test_book_with_past_competition(self, client, competitions_list, clubs_list):
        competition = competitions_list[2]["name"]
        club = clubs_list[2]["name"]
        response = client.get(f"/book/{competition}/{club}")
        assert response.status_code == 200
        assert b"past competition" in response.data
        assert b"Welcome" in response.data

    def test_get_method_not_allowed_on_purchasePlaces(self, client):
        response = client.get("/purchasePlaces")
        assert response.status_code == 405

    def test_purchase_more_than_12_places(self, client, competitions_list, clubs_list):
        competition = competitions_list[0]["name"]
        club = clubs_list[0]["name"]
        places = 13
        data = {"competition": competition, "club": club, "places": places}
        response = client.post("/purchasePlaces", data=data)
        assert response.status_code == 200
        assert b"book more than 12 places" in response.data
        assert b"How many places" in response.data

    def test_purchase_more_places_than_available(
        self, client, competitions_list, clubs_list
    ):
        # define number of places available and points for the test purpose
        competitions_list[0]["numberOfPlaces"] = 8
        clubs_list[0]["points"] = 15
        competition = competitions_list[0]["name"]
        club = clubs_list[0]["name"]
        data = {"competition": competition, "club": club, "places": 10}
        response = client.post("/purchasePlaces", data=data)
        assert response.status_code == 200
        assert b"not enough places available" in response.data
        assert b"How many places" in response.data

    def test_purchase_with_not_enough_points(
        self, client, competitions_list, clubs_list
    ):
        competition = competitions_list[0]["name"]
        club = clubs_list[0]["name"]
        # we have a ratio of 1 point per place
        places = int(clubs_list[0]["points"]) + 1
        # be sure that we have enough places available for the test
        competitions_list[0]["numberOfPlaces"] = places + 1
        data = {"competition": competition, "club": club, "places": places}
        response = client.post("/purchasePlaces", data=data)
        assert response.status_code == 200
        assert b"Sorry, you don&#39;t have enough points" in response.data
        assert b"How many places" in response.data

    def test_purchase_with_places_not_an_int(
        self, client, competitions_list, clubs_list
    ):
        competition = competitions_list[0]["name"]
        club = clubs_list[0]["name"]
        places = "two"
        data = {"competition": competition, "club": club, "places": places}
        with pytest.raises(ValueError):
            client.post("/purchasePlaces", data=data)

    def test_purchasePlaces_everything_ok(self, client, competitions_list, clubs_list):
        # define number of places available and points for the test purpose
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

    def test_logout(self, client):
        response = client.get("/logout")
        assert response.status_code == 302

        # Also check that redirected to the right page
        response = client.get("/logout", follow_redirects=True)
        assert b"GUDLFT Registration" in response.data
        assert b"Please enter your secretary email to continue" in response.data

    def test_clubsPoints_display(self, client):
        response = client.get("/clubsPoints")
        print()
        print(response.data.decode())  # data displayed is not the mocked one...
        assert response.status_code == 200
        assert b"Public list of all clubs and their current points" in response.data


class TestUtilities:
    """Unit tests for utility functions."""

    def test_loadClubs(self):
        clubs = loadClubs()
        assert isinstance(clubs, list)
        assert len(clubs) > 0
        for club in clubs:
            assert "name" in club
            assert "email" in club
            assert "points" in club

    def test_loadCompetitions(self):
        competitions = loadCompetitions()
        assert isinstance(competitions, list)
        assert len(competitions) > 0
        for competition in competitions:
            assert "name" in competition
            assert "numberOfPlaces" in competition

    @pytest.mark.parametrize(
        "date_str, expected",
        [
            ("2023-03-27 10:00:00", True),
            ("2043-03-27 10:00:00", False),
            ("invalid date string", pytest.raises(ValueError)),
        ],
    )
    def test_is_date_str_in_past(self, date_str, expected):
        if isinstance(expected, bool):
            assert is_date_str_in_past(date_str) == expected
        else:
            with expected:
                is_date_str_in_past(date_str)
