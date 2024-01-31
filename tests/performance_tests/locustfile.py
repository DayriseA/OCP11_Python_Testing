from locust import HttpUser, task, between


class TestServerRoutes(HttpUser):
    wait_time = between(0, 1)

    @task
    def index(self):
        self.client.get("/")

    @task
    def clubsPoints(self):
        self.client.get("/clubsPoints")

    @task
    def showSummary(self):
        self.client.post("/showSummary", data={"email": "john@simplylift.co"})

    @task
    def book(self):
        self.client.get("/book/Spring Festival/Simply Lift")

    @task
    def purchasePlaces(self):
        data = {"competition": "Spring Festival", "club": "Simply Lift", "places": 1}
        self.client.post("/purchasePlaces", data=data)

    @task
    def logout(self):
        self.client.get("/logout")
