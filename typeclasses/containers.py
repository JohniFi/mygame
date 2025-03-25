from typing import cast, override
from evennia.commands.cmdset import CmdSet
from evennia.typeclasses.attributes import AttributeProperty
from evennia.typeclasses.models import LockHandler
from evennia.utils.utils import class_from_module
from world.enums import ObjectType
from .ownable import Ownable
from .objects import Object
from django.conf import settings

COMMAND_DEFAULT_CLASS = class_from_module(settings.COMMAND_DEFAULT_CLASS)


class Container(Ownable, Object):
    """
    (based on ContribContainer)
    A type of Object which can be used as a container.

    Implements hooks
     - at_pre_get_from()
     - at_pre_put_in()

    It implements a very basic "size" limitation that is just a flat number of objects.
    """

    obj_type = [ObjectType.CONTAINER]

    # This defines how many objects the container can hold.
    capacity = AttributeProperty(default=20)

    @override
    def at_object_creation(self):
        """
        Extends the base object `at_object_creation` method by setting the "get_from" lock to "true",
        allowing other objects to be put inside and removed from this object.

        By default, a lock type not being explicitly set will fail access checks, so objects without
        the new "get_from" access lock will fail the access checks and continue behaving as
        non-container objects.
        Edit: "look_into", "get_from" and "put_in"
        """
        super().at_object_creation()
        self_locks = cast(LockHandler, self.locks)
        self_locks.add("look_into:true()")
        self_locks.add("get_from:true()")
        self_locks.add("put_in:true()")
        self_locks.add("set_owner:perm(Builder)")  # CmdDemise

    def at_pre_get_from(self, getter, target, **kwargs):
        """
        This will be called when something attempts to get another object FROM this object,
        rather than when getting this object itself.

        Args:
            getter (Object): The actor attempting to take something from this object.
            target (Object): The thing this object contains that is being removed.

        Returns:
            boolean: Whether the object `target` should be gotten or not.

        Notes:
            If this method returns False/None, the getting is cancelled before it is even started.
        """
        return True

    def at_pre_put_in(self, putter, target, **kwargs):
        """
        This will be called when something attempts to put another object into this object.

        Args:
            putter (Object): The actor attempting to put something in this object.
            target (Object): The thing being put into this object.

        Returns:
            boolean: Whether the object `target` should be put down or not.

        Notes:
            If this method returns False/None, the putting is cancelled before it is even started.
            To add more complex capacity checks, modify this method on your child typeclass.
        """
        # check if we're already at capacity
        if len(self.contents) >= cast(int, self.capacity):
            singular, _ = self.get_numbered_name(
                1, putter, definite_article=True, case="accusative"
            )
            putter.msg(f"Es passt nichts mehr in {singular}.")
            return False

        return True

    @override
    def get_display_things(self, looker, **kwargs):
        """
        Get the 'things' component of the object description. Called by `return_appearance`.

        Overwrite: Added lock check "look_into".

        Args:
            looker (DefaultObject): Object doing the looking.
            **kwargs: Arbitrary data for use when overriding.
        Returns:
            str: The things display data.

        """

        if not self.access(looker, "look_into"):
            return f"Das gehört dir nicht. Du kannst nicht hineinsehen."
        else:
            return super().get_display_things(looker, **kwargs)

    # from class Ownable
    @override
    def set_owner(self, setter, target, **kwargs):
        self_locks = cast(LockHandler, self.locks)
        self_locks.add(f"look_into: perm(Builder) or id({target.id})")
        self_locks.add(f"get_from: perm(Admin) or id({target.id})")
        self_locks.add(f"put_in: perm(Builder) or id({target.id})")
        self_locks.add(f"set_owner: perm(Builder) or id({target.id})")
