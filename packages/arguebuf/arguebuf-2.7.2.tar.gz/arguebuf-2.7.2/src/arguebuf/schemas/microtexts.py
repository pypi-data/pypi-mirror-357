from enum import Enum


class EdgeType(str, Enum):
    SEGMENTATION = "seg"
    SUPPORT_DEFAULT = "sup"
    SUPPORT_EXAMPLE = "exa"
    ADDITIONAL_SOURCE = "add"
    ATTACK_ATOM = "reb"
    ATTACK_SCHEME = "und"
