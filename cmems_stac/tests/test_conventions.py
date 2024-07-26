import pytest

from cmems_stac import conventions


@pytest.mark.parametrize(
    ["collection_id", "expected"],
    (
        # pytest.param(id="standard_mfc"),
        # pytest.param(id="standard_tac"),
        # pytest.param(id="standard_omi"),
        pytest.param(
            "GLOBAL_OMI_OHC_area_averaged_anomalies_0_300",
            conventions.collection.OMICollectionId(
                product_type="OMI",
                omi_family="CLIMATE",
                omi_subfamily="OHC",
                indicator_type="area_averaged_anomalies",
                geographic_area="GLOBAL",
                observation_type=None,
            ),
            id="old_omi1",
        ),
        pytest.param(
            "GLOBAL_OMI_HEALTH_carbon_ph_area_averaged",
            conventions.collection.OMICollectionId(
                product_type="OMI",
                omi_family="HEALTH",
                omi_subfamily="PH",
                indicator_type="area_averaged",
                geographic_area="GLOBAL",
                observation_type=None,
            ),
            id="old_omi2",
        ),
        pytest.param(
            "MEDSEA_OMI_SEASTATE_extreme_var_swh_mean_and_anomaly",
            conventions.collection.OMICollectionId(
                product_type="OMI",
                omi_family="VAR_EXTREME",
                omi_subfamily="SEASTATE",
                indicator_type="mean_and_anomaly",
                geographic_area="MEDSEA",
                observation_type="swh",
            ),
            id="old_omi3",
        ),
    ),
)
def test_parse_collection_id(collection_id, expected):
    actual = conventions.parse_collection_id(collection_id)

    assert actual == expected
