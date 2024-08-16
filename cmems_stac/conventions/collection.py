import re
from dataclasses import dataclass


class ParserError(ValueError):
    pass


class FormatError(ValueError):
    pass


mfc_id = re.compile(
    r"""
    (?P<geographical_area>[A-Z]+)
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
    _(?P<geographical_area>[A-Z]+)
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
    _(?P<geographical_area>[A-Z]+)
    _(?P=observation_type)
    _(?P<kind_product>[A-Z0-9]+)
    _(?P<product_type>[A-Z]+)
    _(?P<complementary_info>[A-Z]+)
    _(?P<center_ranking>[0-9]{3})
    _(?P<center_id>[0-9]{3})
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
    geographical_area: str
    product_type: str
    thematic: str
    complementary_info: str | None
    center_ranking: str
    center_id: str

    @classmethod
    def from_string(cls, string):
        match = mfc_id.fullmatch(string)
        if match is None:
            raise ParserError(f"invalid model and forecasting center ID: {string}")

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
            raise FormatError("could not format collection id {self}") from e


@dataclass(frozen=True)
class TACCollectionId:
    observation_type: str
    geographical_area: str
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
            raise ParserError(f"invalid thematic assembly center ID: {string}")

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

        try:
            return {
                "cmems:geographical_area": geographical_areas[self.geographical_area],
                "cmems:thematic": thematics[self.thematic],
                "cmems:observation_type": observation_types[self.observation_type],
                "cmems:product_type": product_types[self.product_type],
            }
        except KeyError as e:
            raise FormatError(f"could not format collection id {self}") from e


def parse_collection_id(string):
    for cls in [MFCCollectionId, TACCollectionId]:
        try:
            return cls.from_string(string)
        except ParserError:
            pass

    raise ParserError(f"unknown collection id format: {string}")
