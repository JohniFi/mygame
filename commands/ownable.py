from django.conf import settings
from evennia import Command, CmdSet
import evennia
from evennia.utils import utils
from evennia.utils.search import search_object

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)

class CmdSetOwner(COMMAND_DEFAULT_CLASS):
    """
    Bestimme Besitzer

    Benutzung:
        zuweisen <charakter>

    Weist einem Objekt einen Besitzer zu bzw.
    überträgt die Eigentümerschaft auf jemanden.
    """

    key = "zuweisen"
    aliases = [
        "übertragen",
    ]
    locks = "perm(Builder)"
    # TODO: allow owner to assign new owner 

    def func(self):

        if not self.args:
            self.caller.msg("an wen?")
            return

        new_owner = self.caller.search(self.args, global_search=True)

        if not new_owner:
            self.caller.msg(f"Kann {self.args} nicht finden.")
            return

        self.obj.db.owner = new_owner
        self.caller.msg(
            f"Eigentümerschaft von {self.obj.get_display_name(self.caller)} auf {new_owner.get_display_name(self.caller)} übertragen."
        )


class CmdSetOwnable(CmdSet):
    priority = 1

    def at_cmdset_creation(self):
        self.add(CmdSetOwner)
