from typing import override
from evennia.commands.cmdset import CmdSet
from evennia.commands.default.general import NumberedTargetCommand
from evennia.utils import utils
from .commands_de import CmdGet, CmdLook, CmdDrop


class ContainerCmdSet(CmdSet):
    """
    Extends the basic `look` and `get` commands to support containers,
    and adds an additional `put` command.
    """

    key = "Container CmdSet"

    @override
    def at_cmdset_creation(self):
        super().at_cmdset_creation()

        self.add(CmdContainerLook)
        self.add(CmdContainerGet)
        self.add(CmdPut)


class CmdContainerLook(CmdLook):

    rhs_split = (" in ",)

    @override
    def func(self):
        """
        Handle the looking.
        """
        caller = self.caller
        # by default, we don't look in anything
        container = None

        if not self.args:
            target = caller.location
            if not target:
                caller.msg("Du hast keinen Aufenthaltsort, den du anschauen könntest!")
                return
        else:
            if self.rhs:
                # we are looking in something, find that first
                container = caller.search(self.rhs)
                if not container:
                    return
                # check access lock
                if not container.access(caller, "look_into"):
                    # supports custom error messages on individual containers
                    if container.db.look_into_err_msg:
                        self.msg(container.db.look_into_err_msg)
                    else:
                        self.msg("Du kannst da nicht hineinsehen.")
                    return

            target = caller.search(self.lhs, location=container)
            if not target:
                return

        desc = caller.at_look(target)
        # add the type=look to the outputfunc to make it
        # easy to separate this output in client.
        self.msg(text=(desc, {"type": "look"}), options=None)


class CmdContainerGet(CmdGet):
    """
    hebe etwas auf

    Benutzung:
      nimm <obj>
      nimm <obj> aus <container>

    Nimmt ein Object von deinem Standort oder aus einem Container und fügt es deinem Inventar hinzu.
    """

    rhs_split = (" aus ",)

    @override
    def func(self):
        caller = self.caller
        # by default, we get from the caller's location
        location = caller.location

        if not self.args:
            self.msg("Nimm was?")
            return

        # check for a container as the location to get from
        if self.rhs:
            location = caller.search(self.rhs)
            if not location:
                return
            # check access lock
            if not location.access(caller, "get_from"):
                # supports custom error messages on individual containers
                if location.db.get_from_err_msg:
                    self.msg(location.db.get_from_err_msg)
                else:
                    self.msg("Du kannst da nichts herausnehmen.")
                return

        objs = caller.search(self.lhs, location=location, stacked=self.number)
        if not objs:
            return
        # the 'stacked' search sometimes returns a list, sometimes not, so we make it always a list
        # NOTE: this behavior may be a bug, see issue #3432
        objs = utils.make_iter(objs)

        if len(objs) == 1 and caller == objs[0]:
            self.msg("Du kannst dich nicht selbst aufheben.")
            return

        # if we aren't allowed to get any of the objects, cancel the get
        for obj in objs:
            # check the locks
            if not obj.access(caller, "get"):
                if obj.db.get_err_msg:
                    self.msg(obj.db.get_err_msg)
                else:
                    self.msg("Das kannst du nicht bekommen.")
                return

            # calling possible at_pre_get_from hook on location
            if hasattr(location, "at_pre_get_from") and not location.at_pre_get_from(caller, obj):
                self.msg("Das kannst du nicht da raus bekommen.")
                return

            # calling at_pre_get hook method
            if not obj.at_pre_get(caller):
                return

        moved = []
        # attempt to move all of the objects
        for obj in objs:
            if obj.move_to(caller, quiet=True, move_type="get"):
                moved.append(obj)
                # calling at_get hook method
                obj.at_get(caller)

        if not moved:
            # none of the objects were successfully moved
            self.msg("Das kann nicht aufgehoben werden.")
            return
        else:
            obj_name = moved[0].get_numbered_name(
                len(moved), caller, return_string=True, case="accusative"
            )

        # enumerate objects in same location as caller (exclue caller itself)
        contents = caller.location.contents
        exclude = utils.make_iter(caller)
        contents = [obj for obj in contents if obj not in exclude]

        container_name, _ = location.get_numbered_name(
            1, caller, case="dative", definite_article=True
        )

        for receiver in contents:
            caller_name = caller.get_display_name(receiver)
            if location == caller.location:
                receiver.msg(f"{caller_name} nimmt sich {obj_name}.")
            else:
                receiver.msg(f"{caller_name} nimmt sich {obj_name} aus {container_name}.")

        if location == caller.location:
            caller.msg(f"Du nimmst dir {obj_name}.")
        else:
            caller.msg(f"Du nimmst dir {obj_name} aus {container_name}.")


class CmdPut(NumberedTargetCommand):
    """
    Lege/stelle/stecke ein Object in ein anderes (z.B. Container)

    Benutzung:
      lege <obj> in <container>

    Lässt dich ein Objekt aus deinem inventar in/auf ein anderes Objekt
    in deiner Umgebung legen/stellen/stecken.
    """

    key = "lege"
    aliases = [
        "leg",
        "stecke",
        "steck",
        "stelle",
        "stell",
    ]
    rhs_split = ("=", " in ", " auf ")
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    @override
    def func(self):

        caller = self.caller
        if not self.args:
            self.msg("Tue was worein?")
            return

        if not self.rhs:
            return

        container = caller.search(self.rhs)
        if not container:
            return

        # Because the PUT command by definition looks for items
        # in inventory, call the search function using location = caller
        objs = caller.search(
            self.lhs,
            location=caller,
            nofound_string=f"Du hast '{self.lhs}' nicht in deinem Inventar.",
            # multimatch_string=f"Du trägst mehr als ein {self.args}:",
            stacked=self.number,
        )
        if not objs:
            return
        # the 'stacked' search sometimes returns a list, sometimes not, so we make it always a list
        # NOTE: this behavior may be a bug, see issue #3432
        objs = utils.make_iter(objs)

        # check access lock
        if not container.access(caller, "put_in"):
            # supports custom error messages on individual containers
            if container.db.put_err_msg:
                self.msg(container.db.put_err_msg)
            else:
                self.msg("Du kannst da nichts reintun.")
            return

        # if any objects fail the drop permission check, cancel the drop
        for obj in objs:
            # Call the object's at_pre_drop() method.
            if not obj.at_pre_drop(caller):
                self.msg(f"Das kannst du nicht ablegen: {obj.get_display_name(caller)}")
                return
            # Call the container's possible at_pre_put_in method.
            if hasattr(container, "at_pre_put_in") and not container.at_pre_put_in(caller, obj):
                self.msg("Das kannst du nicht da rein tun.")
                return

        # do the actual putting
        moved = []
        for obj in objs:
            if obj.move_to(container, quiet=True, move_type="drop"):
                moved.append(obj)
                # Call the object's at_drop() method.
                obj.at_drop(caller)

        if not moved:
            # none of the objects were successfully moved
            self.msg("Es konnte nichts abgelegt werden.")
            return
        else:
            obj_name = moved[0].get_numbered_name(
                len(moved), caller, return_string=True, case="accusative"
            )

        # enumerate objects in same location as caller
        contents = caller.location.contents
        exclude = utils.make_iter(caller)
        contents = [obj for obj in contents if obj not in exclude]

        container_name, _ = container.get_numbered_name(
            1, caller, case="accusative", definite_article=True
        )

        for receiver in contents:
            caller_name = caller.get_display_name(receiver)
            receiver.msg(f"{caller_name} tut {obj_name} in {container_name}.")

        caller.msg(f"Du tust {obj_name} in {container_name}.")
