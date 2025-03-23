from collections import defaultdict
from evennia.typeclasses.attributes import AttributeProperty
from evennia.utils.utils import iter_to_str
from commands.ownable import CmdSetOwnable
from .objects import Object


class Container(Object):
    """
    (based on ContribContainer)
    A type of Object which can be used as a container.

    It implements a very basic "size" limitation that is just a flat number of objects.
    """

    # This defines how many objects the container can hold.
    capacity = AttributeProperty(default=20)

    def at_object_creation(self):
        """
        Extends the base object `at_object_creation` method by setting the "get_from" lock to "true",
        allowing other objects to be put inside and removed from this object.

        By default, a lock type not being explicitly set will fail access checks, so objects without
        the new "get_from" access lock will fail the access checks and continue behaving as
        non-container objects.
        Edit: Two way: "get_from" and "put_in"
        """
        super().at_object_creation()
        self.locks.add("get_from:true()")
        self.locks.add("put_in:true()")

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
        if len(self.contents) >= self.capacity:
            singular, _ = self.get_numbered_name(
                1, putter, definite_article=True, case="accusative"
            )
            putter.msg(f"Es passt nichts mehr in {singular}.")
            return False

        return True


class OwnedContainer(Container):

    # This defines how many objects the container can hold.
    owner = AttributeProperty(default=None)

    def at_object_creation(self):
        super().at_object_creation()

        self.cmdset.add_default(CmdSetOwnable)

    def get_display_things(self, looker, **kwargs):
        """
        Get the 'things' component of the object description. Called by `return_appearance`.

        Args:
            looker (DefaultObject): Object doing the looking.
            **kwargs: Arbitrary data for use when overriding.
        Returns:
            str: The things display data.

        """
        if self.owner and looker != self.owner:
            return (
                f"Das gehört {self.owner.get_display_name(looker)}. Du kannst nicht hineinsehen."
            )

        # return (
        #     _("|wDu siehst:|n {thing_names}").format(
        #         thing_names=thing_names
        #     )  # TODO: Pull-Request for i18n
        #     if thing_names
        #     else ""
        # )

        # sort and handle same-named things
        things = self.filter_visible(self.contents_get(content_type="object"), looker, **kwargs)

        grouped_things = defaultdict(list)
        for thing in things:
            grouped_things[thing.get_display_name(looker, **kwargs)].append(thing)

        thing_names = []
        for thingname, thinglist in sorted(grouped_things.items()):
            nthings = len(thinglist)
            thing = thinglist[0]
            singular, plural = thing.get_numbered_name(nthings, looker, case="accusative")
            thing_names.append(singular if nthings == 1 else plural)
        thing_names = iter_to_str(
            thing_names, endsep="und"
        )  # TODO: Pull-Request for `endsep` i18n
        return (
            "|wDu siehst:|n {thing_names}".format(
                thing_names=thing_names
            )  # TODO: Pull-Request for i18n
            if thing_names
            else ""
        )

    def at_pre_get_from(self, getter, target, **kwargs):
        if self.owner and getter != self.owner:
            return False
        else:
            return super().at_pre_get_from(getter, target, **kwargs)

    def at_pre_put_in(self, putter, target, **kwargs):
        if self.owner and putter != self.owner:
            return False
        else:
            return super().at_pre_put_in(putter, target, **kwargs)
