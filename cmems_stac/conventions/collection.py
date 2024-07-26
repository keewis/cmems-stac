import re
from dataclasses import dataclass

mfc_id = re.compile(
    r"""
    (?P<geographic_area>[A-Z]+)
    _(?P<product_type>[A-Z]+)
    _(?P<thematic>[A-Z]+)
    (?:_(?P<complementary_info>[A-Z]+))?
    _(?P<center_ranking>[0-9]{3})
    _(?P<center_id>[0-9]{3})
    """,
    flags=re.VERBOSE,
)
tac_id = re.compile(
    r"""
    (?P<observation_type>[A-Z]+)
    _(?P<geographic_area>[A-Z]+)
    _(?P<thematic>[A-Z]+)
    (?:_(?P<complementary_info>[A-Z]+))??
    _(?P<kind_product>[A-Z0-9]+)
    _(?P<product_type>[A-Z]+)
    _(?P<center_ranking>[0-9]{3})
    _(?P<center_id>[0-9]{3})
    """,
    flags=re.VERBOSE,
)
old_tac_id = re.compile(
    r"""
    (?P<observation_type>[A-Z]+)
    _(?P<geographic_area>[A-Z]+)
    _(?P=observation_type)
    _(?P<kind_product>[A-Z0-9]+)
    _(?P<product_type>[A-Z]+)
    _(?P<complementary_info>[A-Z]+)
    _(?P<center_ranking>[0-9]{3})
    _(?P<center_id>[0-9]{3})
    """,
    flags=re.VERBOSE,
)
omi_id = re.compile(
    r"""
    (?P<product_type>OMI)
    _(?P<omi_family>CLIMATE|HEALTH|CIRCULATION|VAR_EXTREME)
    _(?P<omi_subfamily>[a-z]+)
    _(?P<geographic_area>[A-Z]+)
    _(?P<indicator_type>[a-z_]+)
    """,
    flags=re.VERBOSE,
)

thematics = {
    "PHY": ["physical"],
    "BGC": ["biogeochemistry"],
    "PHYBGC": ["physical", "biogeochemistry"],
    "PHYBGCWAV": ["physical", "biogeochemistry", "waves"],
}


@dataclass(frozen=True)
class MFCCollectionId:
    geographic_area: str
    product_type: str
    thematic: str
    complementary_info: str | None
    center_ranking: str
    center_id: str

    @classmethod
    def from_string(cls, string):
        match = mfc_id.fullmatch(string)
        if match is None:
            raise ValueError(f"invalid model and forecasting center ID: {string}")

        return cls(**match.groupdict())

    def to_stac(self):
        geographical_areas = {
            "ARCTIC": "arctic sea",
            "BALTICSEA": "baltic sea",
            "BLKSEA": "black sea",
            "GLOBAL": "global",
            "IBI": "iberia biscay ireland",
            "MEDSEA": "mediterranean sea",
            "NWSHELF": "northwest shelf",
        }
        try:
            return {
                "cmems:geographical_area": geographical_areas[self.geographical_area],
                "cmems:thematic": thematics[self.thematic],
                "cmems:product_type": self.product_type.lower(),
            }
        except KeyError as e:
            raise ValueError(f"could not format collection id {self}") from e


@dataclass(frozen=True)
class TACCollectionId:
    observation_type: str
    geographic_area: str
    thematic: str | None
    complementary_info: str | None
    kind_product: str
    product_type: str
    center_ranking: str
    center_id: str

    @classmethod
    def from_string(cls, string):
        match = tac_id.fullmatch(string) or old_tac_id.fullmatch(string)
        if match is None:
            raise ValueError(f"invalid thematic assembly center ID: {string}")

        parts = match.groupdict()
        parts.setdefault("thematic", "PHY")
        return cls(**parts)

    def to_stac(self):
        geographical_areas = {
            "ATL": "european atlantic ocean",  # IBI + NWS
            "ARC": "arctic sea",
            "BAL": "baltic sea",
            "EUR": "european seas",  # MED + IBI + NWS + BAL + BLK
            "GLO": "global",
            "IBI": "iberia biscay ireland",
            "MED": "mediterranean sea",
            "NWS": "northwest shelf",
        }
        observation_types = {
            "INSITU": "in-situ",
            "OCEANCOLOUR": "ocean colour",
            "SEAICE": "sea ice",
            "SEALEVEL": "sea level",
            "SST": "SST",
            "WIND": "wind",
            "WAVE": "wave",
            "MULTIOBS": "multiobs",
        }
        product_types = {
            "NRT": "near-real time",
            "MY": "multiyear",
            "MYNRT": "multiyear near-real time",
            "STATIC": "static",
        }

        return {
            "cmems:geographical_area": geographical_areas[self.geographical_area],
            "cmems:thematic": thematics[self.thematic],
            "cmems:observation_type": observation_types[self.observation_type],
            "cmems:product_type": product_types[self.product_type],
        }


@dataclass
class OMICollectionId:
    product_type: str
    omi_family: str
    omi_subfamily: str
    geographic_area: str
    indicator_type: str

    @classmethod
    def from_string(cls, string):
        match = omi_id.fullmatch(string)
        if match is None:
            raise ValueError(f"invalid ocean monitoring indicator ID: {string}")

        return cls(**match.groupdict())

    def to_stac(self):
        families = {
            "CLIMATE": "climate",
            "HEALTH": "health",
            "CIRCULATION": "circulation",
            "VAR_EXTREME": "variability and extremes",
        }
        subfamilies = {
            # climate
            "sst": "sea surface temperature",
            "ohc": "ocean heat uptake",
            "ocu": "ocean carbon uptake",
            "si": "sea ice change",
            "sl": "sea level mean",
            "ofc": "ocean freshwater",
            # health
            "chl": "chlorophyll production",
            "pp": "primary production",
            "ph": "acidification",
            "oxygen": "deoxygenation",
            "eutroph": "eutrophication",
            "bloom": "blooms",
            "oligo": "oligotrophication",
            "coral": "coral health",
            # circulation
            "heattrans": "heat transport",
            "voltranss": "volume transport",
            "moc": "meridional overturning circulation",
            "gyre": "gyres",
            "upwell": "upwelling",
            "boundary": "boundary currents",
            "windcirc": "wind driven circulation",
            # variability and extremes
            "hmw": "marine heat waves",
            "coldspell": "cold spells",
            "climvar": "climate variability",
            "state": "sea state",
            "extremesl": "extreme sea level",
            "storm": "storm potential",
            "cyclone": "cyclone potential",
        }
        geographical_areas = {
            "ATLANTIC": "atlantic",
            "ARCTIC": "arctic sea",
            "BALTIC": "baltic sea",
            "BLKSEA": "black sea",
            "EUROPE": "europe",
            "GLOBAL": "global",
            "IBI": "iberia biscay ireland",
            "MEDSEA": "mediterranean sea",
            "NORTHWESTSHELF": "northwest shelf",
            "INDIAN": "indian ocean",
            "PACIFIC": "pacific",
            "SOUTHERN": "southern hemisphere",
            "NORTHERN": "northern hemisphere",
        }
        indicator_types = {
            "area_averaged_anomalies": "area averaged anomalies",
            "trend": "trend",
            "area_averaged_mean": "area averaged mean",
            "enso_nino": "el nino southern oscillation",
            "pdo": "pacific decadal oscillation",
            "mei": "multivariate enso index",
        }

        return {
            "cmems:omi_family": families[self.family],
            "cmems:omi_family_abbrev": self.family,
            "cmems:omi_subfamily": subfamilies[self.omi_subfamily],
            "cmems:omi_subfamily_abbrev": self.omi_subfamily,
            "cmems:geographical_area": geographical_areas[self.geographical_area],
            "cmems:indicator_type": indicator_types[self.indicator_type],
        }


def parse_collection_id(string):
    for cls in [MFCCollectionId, TACCollectionId, OMICollectionId]:
        try:
            return cls.from_string(string)
        except ValueError:
            pass

    raise ValueError(f"unknown collection id format: {string}")
