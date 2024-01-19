import json
from flask import Flask, render_template, request, redirect, flash, url_for, Response


def loadClubs():
    with open("clubs.json") as c:
        listOfClubs = json.load(c)["clubs"]
        return listOfClubs


def loadCompetitions():
    with open("competitions.json") as comps:
        listOfCompetitions = json.load(comps)["competitions"]
        return listOfCompetitions


app = Flask(__name__)
app.secret_key = "something_special"

competitions = loadCompetitions()
clubs = loadClubs()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/showSummary", methods=["POST"])
def showSummary():
    try:
        club = [club for club in clubs if club["email"] == request.form["email"]][0]
        return render_template("welcome.html", club=club, competitions=competitions)
    except IndexError:
        flash("Sorry, that email was not found.")
        return redirect(url_for("index"))


@app.route("/book/<competition>/<club>")
def book(competition, club):
    try:
        foundClub = [c for c in clubs if c["name"] == club][0]
        foundCompetition = [c for c in competitions if c["name"] == competition][0]
    except IndexError:
        flash("Something went wrong, please try again")
        return Response(
            render_template("welcome.html", club=club, competitions=competitions),
            status=404,
        )
    if foundClub and foundCompetition:
        return render_template(
            "booking.html", club=foundClub, competition=foundCompetition
        )


@app.route("/purchasePlaces", methods=["POST"])
def purchasePlaces():
    """
    Purchase places in a competition for a club. A club can't buy more than 12 places.
    """
    competition = [c for c in competitions if c["name"] == request.form["competition"]][
        0
    ]
    club = [c for c in clubs if c["name"] == request.form["club"]][0]
    current_club_points = int(club["points"])
    placesRequired = int(request.form["places"])
    if placesRequired > current_club_points:
        msg = (
            f"Sorry, you don't have enough points "
            f"({current_club_points} / {placesRequired} asked)."
        )
        flash(msg)
        return render_template("booking.html", club=club, competition=competition)

    elif placesRequired > 12:
        flash("Sorry, you can't book more than 12 places.")
        return render_template("booking.html", club=club, competition=competition)

    else:
        competition["numberOfPlaces"] = (
            int(competition["numberOfPlaces"]) - placesRequired
        )
        club["points"] = current_club_points - placesRequired
        flash("Great - booking complete!")
        return render_template("welcome.html", club=club, competitions=competitions)


# TODO: Add route for points display


@app.route("/logout")
def logout():
    return redirect(url_for("index"))
