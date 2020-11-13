from __future__ import annotations

from collections import namedtuple
from dataclasses import dataclass, field

import logging
from itertools import chain, product
from typing import Optional, Union, Iterator, List, Any, Dict

logger = logging.getLogger(__file__)

TileImageType = Union[None, str]
MapCoordinates = namedtuple("MapCoordinates", ["x", "y", "layer"])


@dataclass
class Point:
    x: int
    y: int


@dataclass
class Text:
    fontfamily: str
    pixelsize: int
    wrap: bool
    color: str
    bold: bool
    italic: bool
    underline: bool
    strikeout: bool
    kerning: bool
    halign: str
    valign: str


@dataclass
class Animation:
    frames: List[AnimationFrame]


@dataclass
class AnimationFrame:
    tile: Tile
    duration: int


# this is a reserved python word, renaming to circle
@dataclass
class Circle:
    pass


@dataclass
class Tile:
    id: int = None
    gid: str = None
    type: str = None
    terrain: str = None
    image: TileImageType = None
    properties: dict = None
    animation: Animation = None


@dataclass
class Image:
    source: str
    width: int
    height: int
    trans: str


@dataclass
class TileLayer:
    name: str
    opacity: float
    visible: bool
    tintcolor: str
    offsetx: int
    offsety: int
    data: list

    def tiles(self):
        for y, row in enumerate(self.data):
            for x, gid in enumerate(row):
                if gid:
                    yield x, y, gid


@dataclass
class ObjectGroup:
    name: str
    color: str
    opacity: float
    visible: bool
    tintcolor: str
    offsetx: int
    offsety: int
    draworder: int
    # mason
    objects: List = field(default_factory=list)

    def __iter__(self):
        return iter(self.objects)


@dataclass
class Group:
    name: str
    opacity: float
    visible: bool
    tintcolor: str
    offsetx: int
    offsety: int
    # mason
    layers: List = field(default_factory=list)


@dataclass
class Tileset:
    firstgid: int
    source: str
    name: str
    tilewidth: int
    tileheight: int
    spacing: int
    margin: int
    tilecount: int
    columns: int
    objectalignment: str
    # mason
    orientation: str = None
    images: List = field(default_factory=list)
    tiles: List = field(default_factory=list)


@dataclass
class Polygon:
    points: List


@dataclass
class Polyline:
    points: List


@dataclass
class Object:
    name: str
    type: str
    x: float
    y: float
    width: float
    height: float
    rotation: float
    gid: int
    visible: bool
    # mason
    image: Image = None
    shapes: list = field(default_factory=list)


@dataclass
class Property:
    name: str
    type: str
    value: str


@dataclass
class ImageLayer:
    name: str
    visible: bool
    image: Image


@dataclass
class Map:
    # defaults from the spec
    version: str = None
    tiledversion: str = None
    orientation: str = None
    renderorder: str = None
    compressionlevel: str = None
    width: int = None
    height: int = None
    tilewidth: int = None
    tileheight: int = None
    hexsidelength: str = None
    staggeraxis: str = None
    staggerindex: str = None
    background_color: str = None
    nextlayerid: str = None
    nextobjectid: str = None
    infinite: str = None
    # mason
    filename: str = None
    layers: List = field(default_factory=list)
    tilesets: List = field(default_factory=list)
    images: List = field(default_factory=list)
    properties: Dict = field(default_factory=dict)

    # The easy API
    def get_tile_image(self, x: int, y: int, layer: int) -> TileImageType:
        """Return the tile image for this location"""
        gid = self.get_tile_gid(x, y, layer)
        return self.get_tile_image_by_gid(gid)

    def get_tile_image_by_gid(self, gid: int) -> TileImageType:
        """Return the tile image for this location"""
        try:
            return self.images[gid]
        except TypeError:
            raise TypeError(f"GIDs must be expressed as a number.  Got: {gid}")
        except IndexError:
            raise ValueError(f"GID not found: {gid}")

    def get_tile_gid(self, x, y, layer) -> int:
        """Return the tile image GID for this location"""
        try:
            assert x >= 0 and y >= 0 and layer >= 0
        except (AssertionError, ValueError, TypeError):
            raise ValueError(
                f"Tile coordinates and layers must be non-negative, were ({x}, {y}), layer={layer}"
            )
        try:
            layer = self.layers[layer]
        except IndexError:
            raise ValueError(f"Layer not found: {layer}")
        try:
            return layer.data[y][x]
        except IndexError:
            raise ValueError(f"Tile coordinates ({x},{y}) in layer {layer} are invalid")

    def get_tile_locations_by_gid(self, gid: int) -> Iterator[MapCoordinates]:
        """Search map for tile locations by the GID

        Note: Not a fast operation.  Cache results if used often.
        """
        for l in self.visible_tile_layers:
            for x, y, _gid in [i for i in self.layers[l].iter_data() if i[2] == gid]:
                yield MapCoordinates(x, y, l)

    def add_layer(self, layer):
        """Add a layer"""
        self.layers.append(layer)

    def add_tileset(self, tileset: Tileset):
        """Add a tileset to the map"""
        assert isinstance(tileset, Tileset)
        # sort
        self.tilesets.append(tileset)

    def get_layer_by_name(self, name):
        """Return a layer by name

        :param name: Name of layer.  Case-sensitive.
        :rtype: Layer object if found, otherwise ValueError
        """
        try:
            return self.layernames[name]
        except KeyError:
            raise ValueError(f'Layer "{name}" not found')

    def get_object_by_name(self, name):
        """Find an object

        :param name: Name of object.  Case-sensitive.
        :rtype: Object if found, otherwise ValueError
        """
        for obj in self.objects:
            if obj.name == name:
                return obj
        raise ValueError(f'Object "{name}" not found')

    def get_tileset_from_gid(self, gid: int) -> Tileset:
        """Return tileset that owns the gid

        Note: this is a slow operation, so if you are expecting to do this
              often, it would be worthwhile to cache the results of this.
        """
        try:
            tiled_gid = self.tiledgidmap[gid]
        except KeyError:
            raise ValueError("Tile GID not found")

        for tileset in sorted(self.tilesets, key=attrgetter("firstgid"), reverse=True):
            if tiled_gid >= tileset.firstgid:
                return tileset

        raise ValueError("Tileset not found")

    @property
    def objectgroups(self):
        """Return iterator of all object groups

        :rtype: Iterator
        """
        return (layer for layer in self.layers if isinstance(layer, ObjectGroup))

    @property
    def objects(self):
        """Return iterator of all the objects associated with this map

        :rtype: Iterator
        """
        return chain(*self.objectgroups)

    @property
    def visible_layers(self):
        """Return iterator of Layer objects that are set 'visible'

        :rtype: Iterator
        """
        return (l for l in self.layers if l.visible)

    @property
    def visible_tile_layers(self):
        """Return iterator of layer indexes that are set 'visible'

        :rtype: Iterator
        """
        return (
            i
            for (i, l) in enumerate(self.layers)
            if l.visible and isinstance(l, TiledTileLayer)
        )

    @property
    def visible_object_groups(self):
        """Return iterator of object group indexes that are set 'visible'

        :rtype: Iterator
        """
        return (
            i
            for (i, l) in enumerate(self.layers)
            if l.visible and isinstance(l, TiledObjectGroup)
        )

    @property
    def tile_layers(self):
        return (i for i in self.layers if isinstance(i, TileLayer))

    def tile_properties(self):
        for layer in self.tile_layers:
            for tile in layer.tiles:
                if tile.properties:
                    yield tile, tile.properties