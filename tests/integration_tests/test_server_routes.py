from server import loadClubs, loadCompetitions


def test_booking_process(client):
    """
    Test that will check that the methods and routes involved in the booking process
    are working well together.
    """

    # The same functions used by the server to load the clubs and competitions
    clubs = loadClubs()
    assert isinstance(clubs, list)
    assert len(clubs) > 0
    competitions = loadCompetitions()
    assert isinstance(competitions, list)
    assert len(competitions) > 0

    # get a registered email and use it to 'login'
    email = clubs[0]["email"]
    response = client.post("/showSummary", data={"email": email})
    assert response.status_code == 200
    assert b"Welcome" in response.data

    # get a competition and a club to book places (same club as the one used to 'login')
    competition = competitions[0]["name"]
    club = clubs[0]["name"]
    response = client.get(f"/book/{competition}/{club}")
    assert response.status_code == 200
    assert b"Places available" in response.data
    assert competition in response.data.decode()

    # book 1 place
    club_points = int(clubs[0]["points"])
    competition_places_available = int(competitions[0]["numberOfPlaces"])
    data = {"competition": competition, "club": club, "places": 1}
    response = client.post("/purchasePlaces", data=data)
    # check the places and points are updated in the response since we have no access
    # to the server variables here
    club_points_str_in_response = f"Points available: {club_points - 1}"
    competition_places_str_in_response = (
        f"Number of Places: {competition_places_available - 1}"
    )
    assert response.status_code == 200
    assert b"Great - booking complete" in response.data
    assert club_points_str_in_response in response.data.decode()
    assert competition_places_str_in_response in response.data.decode()
