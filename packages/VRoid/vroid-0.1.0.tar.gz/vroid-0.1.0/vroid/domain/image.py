from typing import TypedDict


class ImageSerializer(TypedDict):
    url: str
    url2x: str | None
    width: int
    height: int


class PortraitImageSerializer(TypedDict):
    id_default_image: bool
    original: ImageSerializer
    w600: ImageSerializer
    w300: ImageSerializer
    sq600: ImageSerializer
    sq300: ImageSerializer
    sq150: ImageSerializer


class FullBodyImageSerializer(TypedDict):
    is_default_image: bool
    original: ImageSerializer
    w600: ImageSerializer
    w300: ImageSerializer
