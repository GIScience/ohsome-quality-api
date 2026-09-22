from starlette.status import HTTP_504_GATEWAY_TIMEOUT


def test_timeout(monkeypatch, client, bpolys):
    monkeypatch.setattr("ohsome_quality_api.api.api.get_config_value", lambda _: 0.1)
    endpoint = "/indicators/mapping-saturation"
    parameters = {
        "bpolys": bpolys,
        "topic": "buildings",
    }
    response = client.post(endpoint, json=parameters)
    assert response.status_code == HTTP_504_GATEWAY_TIMEOUT
    assert response.json() == {
        "error": (
            "Request timeout limit of 0.1s has been exceeded. "
            "Try simplifying the GeoJSON geometry or make it smaller, "
            "and try again."
        )
    }
