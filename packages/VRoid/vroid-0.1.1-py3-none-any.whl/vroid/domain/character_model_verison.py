from typing import Any, Literal, NotRequired, TypedDict


class AttachedItemCoinSerializer(TypedDict):
    coin_type: Literal["apple", "google"]
    price: int


class ModelBasisConversionStateSerializer(TypedDict):
    current_state: Literal["pending", "processing", "completed", "failed"]


class VendorSpecifiedLicenseSerializer(TypedDict):
    modification: Literal["default", "disallow", "allow"]
    redistribution: Literal["default", "disallow", "allow"]
    credit: Literal["default", "necessary", "unnecessary"]
    characterization_allowed_user: Literal["default", "author", "everyone"]
    sexual_expression: Literal["default", "disallow", "allow"]
    violent_expression: Literal["default", "disallow", "allow"]
    corporate_commercial_use: Literal["default", "disallow", "allow"]
    personal_commercial_use: Literal["default", "disallow", "profit", "nonprofit"]


class AttachedItemSerializer(TypedDict):
    item_display_name: str
    category_type: Literal[
        "skin",
        "eyebrow",
        "nose",
        "mouth",
        "ear",
        "face_shape",
        "lip",
        "eye_surrounding",
        "eyeline",
        "eyelash",
        "iris",
        "eye_white",
        "eye_highlight",
        "base_hair",
        "all_hair",
        "hair_front",
        "hair_back",
        "whole_body",
        "head",
        "neck",
        "shoulder",
        "arm",
        "hand",
        "chest",
        "torso",
        "waist",
        "leg",
        "tops",
        "bottoms",
        "onepiece",
        "shoes",
        "inner",
        "socks",
        "neck_accessory",
        "arm_accessory",
        "safety",
        "cheek",
    ]
    downloadable: bool
    take_free: bool
    id: str
    attached_item_coins: list[AttachedItemCoinSerializer]


class CharacterModelVersionSerializer(TypedDict):
    id: str
    created_at: str
    spec_version: str | None
    exporter_version: str | None
    triangle_count: int
    mesh_count: int
    mesh_primitive_count: int
    mesh_primitive_morph_count: int
    material_count: int
    texture_count: int
    joint_count: int
    is_vendor_forbidden_use_by_others: bool
    is_vendor_protected_download: bool
    is_vendor_forbidden_other_users_preview: bool
    original_file_size: int | None
    vrm_meta: Any
    original_compressed_file_size: int | None
    conversion_state: NotRequired[ModelBasisConversionStateSerializer]
    vendor_specified_license: NotRequired[VendorSpecifiedLicenseSerializer]
    attached_items: NotRequired[list[AttachedItemSerializer]]
