import pytest
import html
import server


class TestServer:
    """Tests for the different routes in the server."""

    @classmethod
    def setup_class(cls):
        """Setup the server for testing with predetermined data."""
        server.clubs.clear()
        server.clubs.extend(
            [
                {"name": "Simply Test", "email": "test@simplylift.co", "points": "13"},
                {"name": "Iron Test", "email": "test@irontemple.com", "points": "4"},
                {"name": "She Test", "email": "test@shelifts.co.uk", "points": "12"},
            ]
        )
        server.competitions.clear()
        server.competitions.extend(
            [
                {
                    "name": "Spring Festival",
                    "date": "2024-03-27 10:00:00",
                    "numberOfPlaces": "25",
                },
                {
                    "name": "Fall Classic",
                    "date": "2024-10-22 13:30:00",
                    "numberOfPlaces": "5",
                },
                {
                    "name": "Winter Past Date",
                    "date": "2020-12-22 13:30:00",
                    "numberOfPlaces": "15",
                },
            ]
        )

    def test_index_route(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert b"Welcome to the GUDLFT Registration Portal" in response.data

    def test_showSummary_with_registered_email(self, client):
        registered_mail = server.clubs[0]["email"]
        response = client.post("/showSummary", data={"email": registered_mail})
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

    def test_book_with_valid_parameters(self, client):
        competition = server.competitions[0]["name"]
        club = server.clubs[0]["name"]
        response = client.get(f"/book/{competition}/{club}")
        assert response.status_code == 200
        assert b"Places available" in response.data
        assert competition in response.data.decode()

    def test_book_with_invalid_parameters(self, client):
        response = client.get("/book/invalid_competition/invalid_club")
        assert response.status_code == 404
        assert b"Something went wrong" in response.data
        assert b"Welcome" in response.data

    def test_book_with_past_competition(self, client):
        competition = server.competitions[2]["name"]
        club = server.clubs[0]["name"]
        response = client.get(f"/book/{competition}/{club}")
        assert response.status_code == 200
        assert b"past competition" in response.data
        assert b"Welcome" in response.data

    def test_get_method_not_allowed_on_purchasePlaces(self, client):
        response = client.get("/purchasePlaces")
        assert response.status_code == 405

    def test_purchase_more_than_12_places(self, client):
        competition = server.competitions[0]["name"]
        club = server.clubs[0]["name"]
        places = 13
        data = {"competition": competition, "club": club, "places": places}
        response = client.post("/purchasePlaces", data=data)
        assert response.status_code == 200
        assert b"book more than 12 places" in response.data
        assert b"How many places" in response.data

    def test_purchase_more_places_than_available(self, client):
        competition = server.competitions[1]["name"]
        club = server.clubs[0]["name"]
        data = {"competition": competition, "club": club, "places": 10}
        response = client.post("/purchasePlaces", data=data)
        assert response.status_code == 200
        assert b"not enough places available" in response.data
        assert b"How many places" in response.data

    def test_purchase_with_not_enough_points(self, client):
        competition = server.competitions[0]["name"]
        club = server.clubs[1]["name"]
        # we have a ratio of 1 point per place
        places = int(server.clubs[1]["points"]) + 1
        # be sure that we have enough places available for the test
        server.competitions[0]["numberOfPlaces"] = places + 1
        data = {"competition": competition, "club": club, "places": places}
        response = client.post("/purchasePlaces", data=data)
        assert response.status_code == 200
        assert b"Sorry, you don&#39;t have enough points" in response.data
        assert b"How many places" in response.data

    def test_purchase_with_places_not_an_int(self, client):
        competition = server.competitions[0]["name"]
        club = server.clubs[0]["name"]
        places = "two"
        data = {"competition": competition, "club": club, "places": places}
        with pytest.raises(ValueError):
            client.post("/purchasePlaces", data=data)

    def test_purchasePlaces_everything_ok(self, client):
        competition = server.competitions[0]["name"]
        club = server.clubs[0]["name"]
        places = 6
        expected_points = int(server.clubs[0]["points"]) - places
        expected_places = int(server.competitions[0]["numberOfPlaces"]) - places
        data = {"competition": competition, "club": club, "places": places}
        response = client.post("/purchasePlaces", data=data)
        assert response.status_code == 200
        assert int(server.clubs[0]["points"]) == expected_points
        assert int(server.competitions[0]["numberOfPlaces"]) == expected_places
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
        assert response.status_code == 200
        assert b"Public list of all clubs and their current points" in response.data


class TestUtilities:
    """Unit tests for utility functions."""

    def test_loadClubs(self):
        clubs = server.loadClubs()
        assert isinstance(clubs, list)
        assert len(clubs) > 0
        for club in clubs:
            assert "name" in club
            assert "email" in club
            assert "points" in club

    def test_loadCompetitions(self):
        competitions = server.loadCompetitions()
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
            assert server.is_date_str_in_past(date_str) == expected
        else:
            with expected:
                server.is_date_str_in_past(date_str)
