from typing import List, NamedTuple, Union

from shapely import Point, Polygon, STRtree

from .data import load as _load

_index, _polygons, _meta = _load()


class Options(NamedTuple):
    """Options for a location lookup"""

    raise_on_invalid: bool = True
    raise_on_not_found: bool = False


class Coordinate(NamedTuple):
    """A location defined by a latitude and longitude intersection"""

    latitude: float
    longitude: float

    def __str__(self):
        return f"({self.latitude}, {self.longitude})"


class Location(NamedTuple):
    """A location described by a country and an administrative region (e.g., a state or province)"""

    country: str
    administrative_region: str


class InvalidCoordinate(ValueError):
    """The provided coordinate does not represent a valid longitude and latitude"""

    pass


class CoordinateNotFound(ValueError):
    """The provided coordinate does not match a known location"""

    pass


def validate(coordinate: Coordinate) -> bool:
    """Check whether a provided coordinate is valid as defined by"""
    return (
        coordinate.latitude >= -90
        and coordinate.latitude <= 90
        and coordinate.longitude >= -180
        and coordinate.longitude <= 180
    )


def find_first_match_in_index(
    coordinate: Coordinate, index: STRtree, polygons: List[Polygon]
) -> Union[int, None]:
    """Find the first match for a coordinate in an index"""
    point = Point(coordinate.longitude, coordinate.latitude)
    for result in index.query(point):
        if polygons[result].contains(point):
            return result
    return None


def locate(
    coordinate: Coordinate, options: Options = Options()
) -> Union[Location, None]:
    if not validate(coordinate):
        if options.raise_on_invalid:
            raise InvalidCoordinate(f"Invalid coordinate: {coordinate}")
        else:
            return None

    index = None
    point = Point(coordinate.longitude, coordinate.latitude)
    for i in _index.query(point):
        if _polygons[i].contains(point):
            index = i
            break

    if index is None:
        if options.raise_on_not_found:
            raise CoordinateNotFound(f"Coordinate {coordinate} could not be located")
        else:
            return None

    return Location(**_meta[index])
