import geojson
from locust import HttpUser, task

with open("feature-collection-germany-heidelberg.geojson") as f:
    bpolys = geojson.load(f)

topic = "building-count"


class Indicators(HttpUser):
    @task
    def post_indicator_mapping_saturation(self):
        self.client.post(
            "/indicators/mapping-saturation",
            headers={
                "accept": "application/json",
                "Content-Type": "application/json",
            },
            json={
                "bpolys": bpolys,
                "topic": topic,
            },
        )

    @task
    def post_indicator_currentness(self):
        self.client.post(
            "/indicators/currentness",
            headers={
                "accept": "application/json",
                "Content-Type": "application/json",
            },
            json={
                "bpolys": bpolys,
                "topic": topic,
            },
        )
