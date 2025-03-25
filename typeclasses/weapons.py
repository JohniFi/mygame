from evennia.typeclasses.attributes import AttributeProperty
from .items import Item
from world.enums import ObjectType


class Weapon(Item):

    obj_type = [
        ObjectType.ITEM,
        ObjectType.WEAPON,
    ]
