from ohsome_quality_api.indicators.building_comparison import stac_client


def test_stac_client_get_area():
    area = stac_client.get_area()
    assert area > 0
