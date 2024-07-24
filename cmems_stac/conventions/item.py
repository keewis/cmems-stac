import re

id_ = re.compile(
    r"""
    (?P<origin>[a-z0-9]+)
    _(?P<group>[a-z]+)
    (?:-(?P<pc>[a-z]+))?
    _(?P<area>[a-z]+)
    _(?P<thematic>[a-z]+)
    (?:-(?P<var>[-a-z0-9]+))?
    (?:_(?P<type>[a-z]+))
    (?:_(?P<complementary_info>[^_]+))
    _(?P<temporal_resolution>[A-Z0-9a-z.]{3,})
    (?:-(?P<typology>[im]))?
    """,
    flags=re.VERBOSE,
)
