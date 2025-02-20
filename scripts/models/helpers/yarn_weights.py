from enum import Enum


class YarnWeights(Enum):
    FINE = frozenset({"fingering", "light-fingering", "sock", "lace"})
    LIGHT = frozenset({"sport", "baby", "dk"})
    MEDIUM = frozenset({"worsted", "aran"})
    BULKY = frozenset({"bulky"})
    SUPER_BULKY = frozenset({"super-bulky"})

    @classmethod
    def get_group(cls, value):
        for group in cls:
            if value in group.value:
                return group.name
        return None
