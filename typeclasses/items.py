from evennia.typeclasses.attributes import AttributeProperty
from . import objects


class Item(objects.Object):
    # the weight of the Item
    weight = AttributeProperty(default=0)

    # the fuel value (how long will it burn) in seconds
    fuel = AttributeProperty(default=0)

    # worth of gold
    worth = AttributeProperty(default=0)

    # TODO: enum item_type
