import re
from dataclasses import dataclass

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
            raise ValueError(f"invalid model and forecasting center ID: {string}")

        return cls(**match.groupdict())


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
            raise ValueError(f"invalid thematic assembly center ID: {string}")

        parts = match.groupdict()
        parts.setdefault("thematic", "PHY")
        return cls(**parts)


def parse_collection_id(string):
    for cls in [MFCCollectionId, TACCollectionId]:
        try:
            return cls.from_string(string)
        except ValueError:
            pass

    raise ValueError(f"unknown collection id format: {string}")
