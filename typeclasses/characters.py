"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter
from evennia.typeclasses.attributes import AttributeProperty

from .objects import ObjectParent


class Character(ObjectParent, DefaultCharacter):
    """
    The Character just re-implements some of the Object's methods and hooks
    to represent a Character entity in-game.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Object child classes like this.

    """

    hp = AttributeProperty(default=1)
    hp_max = AttributeProperty(default=1)

    gold = AttributeProperty(default=0)

    def get_display_name(self, looker=None, **kwargs):
        """
        Displays the name of the object in a viewer-aware manner.

        Args:
            looker (DefaultObject): The object or account that is looking at or getting information
                for this object.

        Returns:
            str: A name to display for this object. By default this returns the `.name` of the object.

        Notes:
            This function can be extended to change how object names appear to users in character,
            but it does not change an object's keys or aliases when searching.

        """
        return f"|c{self.name}|n"
