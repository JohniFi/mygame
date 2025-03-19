"""
General Character commands usually available to all characters
"""

from evennia.commands.default import general
from evennia.utils import utils


class CmdLook(general.CmdLook):
    """
    schaue dich an deinem Standort um oder betrachte ein Objekt

    Benutzung:
      schau
      schau <obj>
      schau *<account>

    Untersucht einen Standort oder ein Objekt in deine Umgebung.
    """

    key = "schau"
    aliases = [
        "l",
        "ls",
        "schaue",
        "schauen",
        "betrachte",
        "betrachten",
        "anschauen",
        "sieh",
        "sehen",
        "ansehen",
    ]
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        """
        Handle the looking.
        """
        caller = self.caller
        if not self.args:
            target = caller.location
            if not target:
                caller.msg("Du hast keinen Aufenthaltsort, den du anschauen könntest!")
                return
        else:
            target = caller.search(self.args)
            if not target:
                return
        desc = caller.at_look(target)
        # add the type=look to the outputfunc to make it
        # easy to separate this output in client.
        self.msg(text=(desc, {"type": "look"}), options=None)

class CmdInventory(general.CmdInventory):
    """
    zeige Inventar

    Benutzung:
      inventar
      inv

    Zeigt dein Inventar.
    """

    key = "inventar"
    aliases = ["inv", "i"]
    locks = "cmd:all()"
    arg_regex = r"$"

    def func(self):
        """check inventory"""
        items = self.caller.contents
        if not items:
            string = "Du hast nichts in deinem Inventar."
        else:
            from evennia.utils.ansi import raw as raw_ansi

            table = self.styled_table(border="header")
            for key, desc, _ in utils.group_objects_by_key_and_desc(items, caller=self.caller):
                table.add_row(
                    f"|C{key}|n",
                    "{}|n".format(utils.crop(raw_ansi(desc or ""), width=50) or ""),
                )
            string = f"|wIn deinem Inventar:\n{table}"
        self.msg(text=(string, {"type": "inventory"}))


class CmdGet(general.CmdGet):
    """
    hebe etwas auf

    Benutzung:
      nimm <obj>

    Nimmt ein Object von deinem Standort und fügt es deinem Inventar hinzu.
    """

    key = "nimm"
    aliases = [
        "nehmen",
        "heb auf",
        "hebe auf",
        "aufheben",
        "hole",
        "holen",
        "erhalte",
        "erhalten",
        "erlange",
        "erlangen",
        "ergreife",
    ]
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        """implements the command."""

        caller = self.caller

        if not self.args:
            self.msg("Nimm was?")
            return
        objs = caller.search(self.args, location=caller.location, stacked=self.number)
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
        else:
            obj_name = moved[0].get_numbered_name(
                len(moved), caller, return_string=True, case="accusative"
            )

        # enumerate objects in same location as caller
        contents = caller.location.contents
        exclude = utils.make_iter(caller)
        contents = [obj for obj in contents if obj not in exclude]

        for receiver in contents:
            receiver.msg(f"{caller} erhält {obj_name}.")

        caller.msg(f"Du erhältst {obj_name}")
