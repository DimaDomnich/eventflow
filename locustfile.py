from locust import HttpUser, task, between


class EventflowUser(HttpUser):
    wait_time = between(1, 2)
    token = None

    def on_start(self):
        response = self.client.post(
            "/api/auth/login",
            json={"email": "email1@g.com", "password": "pass"},
        )
        self.token = response.json()["access"]

    @task(3)
    def list_events(self):
        self.client.get(
            "/api/events", headers={"Authorization": f"Bearer {self.token}"}
        )

    @task(1)
    def get_event(self):
        self.client.get(
            "/api/events/1", headers={"Authorization": f"Bearer {self.token}"}
        )
