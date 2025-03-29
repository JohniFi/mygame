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
from world.health_bar import display_meter
from .objects import ObjectParent


class CharacterParent(ObjectParent):
    """
    Mixin for all characters (player and non-player)
    """

    hp = AttributeProperty(default=1)
    hp_max = AttributeProperty(default=1)
    # see: heal(), damage()

    gold = AttributeProperty(default=0)
    # TODO: gold_add(), gold_sub(), gold_set()

    # used in get_display_name()
    color_code = AttributeProperty(default="|c")

    @override
    def at_object_creation(self):
        super().at_object_creation()
        # call all AttributeProperty to initialize in database
        # not needed anymore after pull request https://github.com/evennia/evennia/pull/3753
        self.hp
        self.hp_max
        self.gold

    @override
    def get_display_things(self, looker, **kwargs):
        # should not see inventory by looking at character
        return ""
        # TODO: add lock for peeking in inventar of others (maybe special skill?)

    def get_prompt(self):
        health_bar = display_meter(self.hp, self.hp_max)
        return f"{self.name} | {health_bar} | 🪙: {self.gold}"

    def update_prompt(self):
        self.msg(prompt=self.get_prompt())

    def heal(self, healing, healer=None):
        """
        Heal by a certain amount of HP.

        """
        hp = cast(int, self.hp)
        hp_max = cast(int, self.hp_max)

        damage = hp_max - hp
        healed = min(damage, healing)
        self.hp += healed  # type: ignore

        if healer is self:
            self.msg(f"|gDu heilst dich um {healed} HP.|n")
        elif healer:
            self.msg(f"|g{healer.name} heilt dich um {healed} HP.|n")
        else:
            self.msg(f"|gDu heilst um {healed} HP.")
        # update health-bar
        self.update_prompt()

    def damage(self, damage, attacker=None):
        """
        Get damaged by a certain amount of HP.

        """
        hp = cast(int, self.hp)

        damage = min(damage, hp)
        self.hp -= damage  # type: ignore

        if attacker is self:
            self.msg(f"|rDu verletz dich selbst und verlierst {damage} HP.|n")
        elif attacker:
            self.msg(f"|rDu verlierst {damage} HP durch {attacker.name}.|n")
        else:
            self.msg(f"|rDu verlierst {damage} HP.")
        # update health-bar
        self.update_prompt()


class Character(CharacterParent, DefaultCharacter):
    """
    Typeclass for character objects linked to an account

    The Character just re-implements some of the Object's methods and hooks
    to represent a Character entity in-game.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Object child classes like this.

    """

    level = AttributeProperty(default=1)
    xp = AttributeProperty(default=0)
    reputation = AttributeProperty(default=0)

    # @override
    # def at_object_creation(self):
    #     super().at_object_creation()

    @override
    def at_post_puppet(self, **kwargs):
        # show health bar
        super().at_post_puppet(**kwargs)
        self.update_prompt()

    @override
    def get_prompt(self):
        health_bar = display_meter(self.hp, self.hp_max)
        return f"{health_bar} | 🪙: {self.gold} | 🤝: {self.reputation} | Level: {self.level} ({self.xp} EP)"


class NPC(CharacterParent, DefaultCharacter):
    """
    Base Typeclass for all non player characters (NPCs, mobs, merchants, quest-givers etc.)
    """

    # @override
    # def at_object_creation(self):
    #     super().at_object_creation()

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
            "Dein Geist fährt in den Körper von {name}. Test gold: {gold}".format(
                name=self.get_display_name(self), gold=self.gold
            )
        )

        def message(obj: DefaultObject, from_obj):
            if self.has_account:
                obj.msg(
                    "Der Geist von {puppeteer} fährt in den Körper von {name}.".format(
                        name=self.get_display_name(obj), puppeteer=self.account.get_display_name(obj)  # type: ignore
                    ),
                    from_obj=from_obj,
                )

        self_location.for_contents(message, exclude=[self], from_obj=self)

        # look around
        self.msg((self.at_look(self_location), {"type": "look"}), options=None)
        # show health bar
        self.update_prompt()

    @override
    def at_post_unpuppet(self, account: Optional[DefaultAccount] = None, session=None, **kwargs):
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
        self.msg("Du verlässt den Körper von {name}.\n".format(name=self.get_display_name(self)))
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
