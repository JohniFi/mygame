"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from typing import Optional, cast, override
from evennia.accounts.accounts import DefaultAccount
from evennia.objects.objects import DefaultCharacter, DefaultObject
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

    @override
    def get_display_name(self, looker=None, **kwargs):
        return f"|c{self.name}|n"


class NPC(ObjectParent, DefaultCharacter):
    """
    Base Class for all non player characters (NPCs, mobs, merchants, quest-givers etc.)
    """

    hp = AttributeProperty(default=1)
    hp_max = AttributeProperty(default=1)

    gold = AttributeProperty(default=0)

    @override
    def at_post_puppet(self, **kwargs):
        """
        Called just after puppeting has been completed and all
        Account<->Object links have been established.

        Args:
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the call (unused by default).
        Notes:

            You can use `self.account` and `self.sessions.get()` to get
            account and sessions at this point; the last entry in the
            list from `self.sessions.get()` is the latest Session
            puppeting this Object.

        """
        self_location = cast(DefaultObject, self.location)

        self.msg(
            "Dein Geist fährt in den Körper von {name}.".format(
                name=self.get_display_name(self)
            )
        )
        self.msg((self.at_look(self_location), {"type": "look"}), options=None)

        def message(obj: DefaultObject, from_obj):
            if self.has_account:
                obj.msg(
                    "Der Geist von {puppeteer} fährt in den Körper von {name}.".format(
                        name=self.get_display_name(obj), puppeteer=self.account.get_display_name(obj)  # type: ignore
                    ),
                    from_obj=from_obj,
                )

        self_location.for_contents(message, exclude=[self], from_obj=self)

    @override
    def at_post_unpuppet(
        self, account: Optional[DefaultAccount] = None, session=None, **kwargs
    ):
        """
        We stove away the character when the account goes ooc/logs off,
        otherwise the character object will remain in the room also
        after the account logged off ("headless", so to say).

        Args:
            account (DefaultAccount): The account object that just disconnected
                from this object.
            session (Session): Session controlling the connection that
                just disconnected.
        Keyword Args:
            reason (str): If given, adds a reason for the unpuppet. This
                is set when the user is auto-unpuppeted due to being link-dead.
            **kwargs: Arbitrary, optional arguments for users
                overriding the call (unused by default).

        """
        self_location = cast(DefaultObject, self.location)
        self.msg(
            "Du verlässt den Körper von {name}.\n".format(
                name=self.get_display_name(self)
            )
        )
        self.msg((self.at_look(self_location), {"type": "look"}), options=None)

        def message(obj: DefaultObject, from_obj):
            if account:
                obj.msg(
                    "Der Geist von {puppeteer} verlässt den Körper von {name}.".format(
                        name=self.get_display_name(obj),
                        puppeteer=account.get_display_name(obj),
                    ),
                    from_obj=from_obj,
                )

        self_location.for_contents(message, exclude=[self], from_obj=self)

    @override
    def get_display_name(self, looker=None, **kwargs):
        return f"|c{self.name}|n"
