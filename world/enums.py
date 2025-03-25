from enum import Enum


class ObjectType(Enum):
    ITEM = "item"
    WEAPON = "weapon"
    ARMOR = "armor"
    SHIELD = "shield"
    CLOTHING = "clothing"
    CONSUMABLE = "consumable"
    THROWABLE = "throwable"
    MAGIC = "magic"
    QUEST = "quest"
    TREASURE = "treasure"
    ANIMAL = "animal"
    CONTAINER = "container"

    @classmethod
    def reverse_map(cls):
        return {member.value: member for member in cls}


OBJECT_TYPE_REVERSE_MAP = ObjectType.reverse_map()


class Gender(Enum):
    FEMININE = "f"
    MASCULINE = "m"
    NEUTER = "n"

    @classmethod
    def reverse_map(cls):
        return {member.value: member for member in cls}


GENDER_REVERSE_MAP = Gender.reverse_map()


class CraftingCategory(Enum):
    MATERIAL = "crafting_material"
    TOOL = "crafting_tool"

    @classmethod
    def reverse_map(cls):
        return {member.value: member for member in cls}


CRAFTING_REVERSE_MAP = CraftingCategory.reverse_map()


class Crafting(Enum):
    # TODO: add crafting tags
    # WOOD = "wood"

    @classmethod
    def reverse_map(cls):
        return {member.value: member for member in cls}


CRAFTING_REVERSE_MAP = Crafting.reverse_map()
