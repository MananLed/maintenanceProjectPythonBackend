from locust import HttpUser, task, between

class HealthTest(HttpUser):
    wait_time = between(1,3)

    @task
    def get_health_status(self):
        self.client.get("/health")