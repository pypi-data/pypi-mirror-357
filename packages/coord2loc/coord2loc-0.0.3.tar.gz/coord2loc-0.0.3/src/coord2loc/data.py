import zlib
from importlib.abc import Traversable
from importlib.metadata import entry_points
from typing import List, Tuple

import msgpack
from shapely import Polygon, STRtree, from_wkb


def discover() -> List[Tuple[str, Traversable, Traversable]]:
    results = []

    for entry_point in entry_points().get("coord2loc.data", []):
        print(entry_point)
        get_data = entry_point.load()
        results.append(get_data())

    return results


def load_polygons(msgpack_polygons_file: Traversable) -> List[Polygon]:
    polygons = []
    polygon_wkbs = msgpack.unpackb(
        zlib.decompress(msgpack_polygons_file.read_bytes()), raw=False
    )
    for wkb_bytes in polygon_wkbs:
        wkb_bytes = wkb_bytes.strip()
        if not wkb_bytes:
            continue
        polygons.append(from_wkb(wkb_bytes))
    return polygons


def load_meta(msgpack_meta_file: Traversable) -> List[dict]:
    return msgpack.unpackb(zlib.decompress(msgpack_meta_file.read_bytes()), raw=False)


def load() -> tuple[STRtree, List[Polygon], List[dict]]:
    packages = discover()

    polygons = []
    meta = []
    for _, msgpack_polygons_file, msgpack_meta_file in packages:
        polygons.extend(load_polygons(msgpack_polygons_file))
        meta.extend(load_meta(msgpack_meta_file))

    assert len(polygons) == len(meta)

    return STRtree(polygons), polygons, meta
