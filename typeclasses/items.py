from evennia.typeclasses.attributes import AttributeProperty
from .objects import Object
from world.enums import ObjectType


class Item(Object):

    obj_type = [ObjectType.ITEM]

    # the weight of the Item
    weight = AttributeProperty(default=0)

    # the fuel value (how long will it burn) in seconds
    fuel = AttributeProperty(default=0)

    # worth of gold
    worth = AttributeProperty(default=0)
