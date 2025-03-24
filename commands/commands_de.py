"""
General Character commands usually available to all characters
"""

from typing import Dict, Optional
from evennia.commands.default import (
    general,
    help,
)
from evennia.utils import utils
from evennia.utils.ansi import ANSIString
from evennia.utils.utils import dedent, format_grid, pad


# ----- GENERAL -----
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
            for key, desc, _ in utils.group_objects_by_key_and_desc(
                items, caller=self.caller
            ):
                table.add_row(
                    f"{key}",
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
            return
        else:
            obj_name = moved[0].get_numbered_name(
                len(moved), caller, return_string=True, case="accusative"
            )

        # enumerate objects in same location as caller
        contents = caller.location.contents
        exclude = utils.make_iter(caller)
        contents = [obj for obj in contents if obj not in exclude]

        for receiver in contents:
            receiver.msg(f"{caller} nimmt sich {obj_name}.")

        caller.msg(f"Du nimmst dir {obj_name}.")


class CmdDrop(general.CmdDrop):
    """
    etwas ablegen

    Benutzung:
      drop <obj>

    Lässt dich ein Objekt aus deinem Inventar an deinem Standort ablegen.
    """

    key = "drop"
    aliases = [
        "lege ab",
        "leg ab",
        "ablegen",
        "fallenlassen",
        "lasse fallen",
        "lass fallen",
        "lege hin",
        "leg hin",
        "hinlegen",
        "wirf ab",
        "abwerfen",
        "loswerden",
    ]
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        """Implement command"""

        caller = self.caller
        if not self.args:
            caller.msg("Was ablegen?")
            return

        # Because the DROP command by definition looks for items
        # in inventory, call the search function using location = caller
        objs = caller.search(
            self.args,
            location=caller,
            nofound_string=f"Du hast '{self.args}' nicht in deinem Inventar.",
            # multimatch_string=f"Du trägst mehr als ein {self.args}:",
            stacked=self.number,
        )
        if not objs:
            return
        # the 'stacked' search sometimes returns a list, sometimes not, so we make it always a list
        # NOTE: this behavior may be a bug, see issue #3432
        objs = utils.make_iter(objs)

        # if any objects fail the drop permission check, cancel the drop
        for obj in objs:
            # Call the object's at_pre_drop() method.
            if not obj.at_pre_drop(caller):
                self.msg(f"Das kannst du nicht ablegen: {obj.get_display_name(caller)}")
                return

        # do the actual dropping
        moved = []
        for obj in objs:
            if obj.move_to(caller.location, quiet=True, move_type="drop"):
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

        for receiver in contents:
            receiver.msg(f"{caller} legt {obj_name} ab.")

        caller.msg(f"Du legst {obj_name} ab.")


class CmdGive(general.CmdGive):
    """
    übergebe jemandem etwas

    Benutzung:
      gib <inventar-obj> an <ziel>
      schenke <inventar-obj> = <ziel>
      übergebe/eigentum <obj> an <ziel>

    Switch:
      eigentum - überträgt die Eigentümerschaft des Objektes statt das Objekt selbst.

    Überträgt ein Item aus deinem Inventar in das Inventar eines Anderen.
    Oder überträgt die Eigentümerschaft eines Objektes in deiner Umgebung auf jemanden.
    """

    key = "gib"
    aliases = [
        "geben",
        "schenke",
        "schenken",
        "überreiche",
        "überreiche",
        "übergebe",
        "übergeben",
        "überlasse",
        "überlassen",
        "übertrage",
        "übertragen",
    ]
    switch_options = ("eigentum",)

    rhs_split = ("=", " zu ", " an ")  # Prefer = delimiter, but allow " to " usage.
    locks = "cmd:all()"
    arg_regex = r"^[ /]|\n|$"

    def func(self):
        """Implement give"""

        caller = self.caller
        if not self.args or not self.rhs:
            caller.msg("Benutzung: gib <inventar-obj> an <ziel>")
            return

        # With SWITCH '/eigentum'
        if "eigentum" in self.switches:
            # find object
            obj = caller.search(
                self.lhs, nofound_string=f"Kann '{self.lhs}' nicht finden."
            )
            if not obj:
                return

            # find target (new owner)
            target = caller.search(
                self.rhs,
                global_search=True,
                nofound_string=f"Kann {self.rhs} nicht finden.",
            )
            if not target:
                return

            # check if obj can set_owner()
            if not hasattr(obj, "set_owner"):
                caller.msg(
                    f"Kann Eigentümerschaft von {obj.get_display_name(caller)} nicht übertragen."
                )
                return

            # check access lock
            if not obj.access(caller, "set_owner"):
                # supports custom error messages on individual containers
                if obj.db.put_err_msg:
                    self.msg(obj.db.put_err_msg)
                else:
                    self.msg(
                        f"Du kannst die Eigentümerschaft von {obj.get_display_name(caller)} nicht übertragen."
                    )
                return

            # net new owner
            obj.set_owner(caller, target)
            caller.msg(
                f"Eigentümerschaft von {obj.get_display_name(caller)} auf {target.get_display_name(caller)} übertragen."
            )
            return

        # Without SWITCH

        # find the thing(s) to give away
        to_give = caller.search(
            self.lhs,
            location=caller,
            nofound_string=f"Du hast '{self.lhs}' nicht in deinem Inventar.",
            # multimatch_string=f"You carry more than one {self.lhs}:",
            stacked=self.number,
        )
        if not to_give:
            return
        # find the target to give to
        target = caller.search(self.rhs)
        if not target:
            return

        # the 'stacked' search sometimes returns a list, sometimes not, so we make it always a list
        # NOTE: this behavior may be a bug, see issue #3432
        to_give = utils.make_iter(to_give)

        obj_name = to_give[0].get_numbered_name(
            len(to_give), caller, return_string=True, case="accusative"
        )
        if target == caller:
            caller.msg(f"Du behältst {obj_name} für dich.")
            return

        # if any of the objects aren't allowed to be given, cancel the give
        for obj in to_give:
            # calling at_pre_give hook method
            if not obj.at_pre_give(caller, target):
                return

        # do the actual moving
        moved = []
        for obj in to_give:
            if obj.move_to(target, quiet=True, move_type="give"):
                moved.append(obj)
                # Call the object's at_give() method.
                obj.at_give(caller, target)

        if not moved:
            caller.msg(f"Das kannst du nicht {target.get_display_name(caller)} geben.")
        else:
            obj_name = to_give[0].get_numbered_name(
                len(moved), caller, return_string=True, case="accusative"
            )
            caller.msg(f"Du übergibst {obj_name} an {target.get_display_name(caller)}.")
            target.msg(f"{caller.get_display_name(target)} gibt dir {obj_name}.")


class CmdSetDesc(general.CmdSetDesc):
    """
    beschreibe dich selbst

    Benutzung:
      setdesc <beschreibung>

    Fügt eine Beschreibung zu dir hinzu.
    Diese ist für andere sichtbar, wenn sie dich ansehen.
    """

    key = "setdesc"
    aliases = [
        "beschreibe",
        "beschreiben",
        "beschreibung",
    ]
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        """add the description"""

        if not self.args:
            self.msg("Du musst eine Beschreibung hinzufügen.")
            return

        self.caller.db.desc = self.args.strip()
        self.msg("Du hast deine Beschreibung hinzugefügt.")


class CmdSay(general.CmdSay):
    """
    sprich als dein Charakter

    Benutzung:
      sag <nachricht>

    Sprich zu allen in deiner Umgebung.
    """

    key = "sag"
    aliases = [
        '"',
        "'",
        "sage",
        "sagen",
        "sprich",
        "sprechen",
        "erzähl",
        "erzähle",
        "erzählen",
    ]
    locks = "cmd:all()"

    # don't require a space after `say/'/"`
    arg_regex = None

    def func(self):
        """Run the say command"""

        caller = self.caller

        if not self.args:
            caller.msg("Sage was?")
            return

        speech = self.args

        # Calling the at_pre_say hook on the character
        speech = caller.at_pre_say(speech)

        # If speech is empty, stop here
        if not speech:
            return

        # Call the at_post_say hook on the character
        caller.at_say(speech, msg_self=True)


class CmdWhisper(general.CmdWhisper):
    """
    Sprich vertaulich als dein Charakter zu jemandem

    Benutzung:
      wisper <charakter> = <nachricht>
      wisper <char1>, <char2> = <nachricht>

    Sprich vertaulich zu einem oder mehreren Charakteren in deiner Umgebung, ohne dass Andere im
    Raum informiert werden.
    """

    key = "wisper"
    aliases = [
        "wispern",
        "flüster",
        "flüstere",
        "flüstern",
        "zuflüstern",
        "raune",
        "raunen",
        "zuraunen",
    ]
    locks = "cmd:all()"

    def func(self):
        """Run the whisper command"""

        caller = self.caller

        if not self.lhs or not self.rhs:
            caller.msg("Benutzung: wisper <charakter> = <nachricht>")
            return

        receivers = [recv.strip() for recv in self.lhs.split(",")]

        receivers = [caller.search(receiver) for receiver in set(receivers)]
        receivers = [recv for recv in receivers if recv]

        speech = self.rhs
        # If the speech is empty, abort the command
        if not speech or not receivers:
            return

        # Call a hook to change the speech before whispering
        speech = caller.at_pre_say(speech, whisper=True, receivers=receivers)

        # no need for self-message if we are whispering to ourselves (for some reason)
        msg_self = None if caller in receivers else True
        caller.at_say(speech, msg_self=msg_self, receivers=receivers, whisper=True)


class CmdPose(general.CmdPose):
    """
    eine Pose einnehmen

    Benutzung:
      pose <pose text>

    Beispiel:
      pose steht an der Wand und lächelt.
       -> andere werden sehen:
      Tom steht an der Wand und lächelt.

    Beschreibe eine Aktion. Der Pose-Text wird automatisch
    mit deinem Namen beginnen.
    """


# ----- HELP -----
class CmdHelp(help.CmdHelp):
    """
    Hilfe erhalten.

    Benutzung:
      hilfe
      hilfe <thema, befehl oder kategorie>
      hilfe <thema>/<subthema>
      hilfe <thema>/<unterthema>/<unterunterthema> ...

    Benutze den 'hilfe'-Befehl allein um eine Auflistung aller hilfethemen,
    sortiert nach Kategorie zu erhalten.
    Einige größere Themen haben möglicherweise noch Unterthemen.

    """

    key = "hilfe"
    aliases = ["?", "hilf", "help"]

    # ...

    def format_help_entry(
        self,
        topic="",
        help_text="",
        aliases=None,
        suggested=None,
        subtopics=None,
        click_topics=True,
    ):
        """This visually formats the help entry.
        This method can be overridden to customize the way a help
        entry is displayed.

        Args:
            title (str, optional): The title of the help entry.
            help_text (str, optional): Text of the help entry.
            aliases (list, optional): List of help-aliases (displayed in header).
            suggested (list, optional): Strings suggested reading (based on title).
            subtopics (list, optional): A list of strings - the subcategories available
                for this entry.
            click_topics (bool, optional): Should help topics be clickable. Default is True.

        Returns:
            help_message (str): Help entry formated for console.

        """
        separator = "|C" + "-" * self.client_width() + "|n"
        start = f"{separator}\n"

        title = f"|CHilfe für |w{topic}|n" if topic else "|rKeine Hilfe gefunden|n"

        if aliases:
            aliases = " |C(aliases: {}|C)|n".format(
                "|C,|n ".join(f"|w{ali}|n" for ali in aliases)
            )
        else:
            aliases = ""

        help_text = "\n" + dedent(help_text.strip("\n")) if help_text else ""

        if subtopics:
            if click_topics:
                subtopics = [
                    f"|lchilfe {topic}/{subtop}|lt|w{topic}/{subtop}|n|le"
                    for subtop in subtopics
                ]
            else:
                subtopics = [f"|w{topic}/{subtop}|n" for subtop in subtopics]
            subtopics = "\n|CUnterthemen:|n\n  {}".format(
                "\n  ".join(
                    format_grid(
                        subtopics,
                        width=self.client_width(),
                        line_prefix=self.index_topic_clr,
                    )
                )
            )
        else:
            subtopics = ""

        if suggested:
            suggested = sorted(suggested)
            if click_topics:
                suggested = [f"|lchilfe {sug}|lt|w{sug}|n|le" for sug in suggested]
            else:
                suggested = [f"|w{sug}|n" for sug in suggested]
            suggested = "\n|CAndere Themen-Vorschläge:|n\n{}".format(
                "\n  ".join(
                    format_grid(
                        suggested,
                        width=self.client_width(),
                        line_prefix=self.index_topic_clr,
                    )
                )
            )
        else:
            suggested = ""

        end = start

        partorder = (start, title + aliases, help_text, subtopics, suggested, end)

        return "\n".join(part.rstrip() for part in partorder if part)

    # ...

    def format_help_index(
        self,
        cmd_help_dict: Optional[Dict] = None,
        db_help_dict: Optional[Dict] = None,
        title_lone_category=False,
        click_topics=True,
    ):
        """Output a category-ordered g for displaying the main help, grouped by
        category.

        Args:
            cmd_help_dict (dict): A dict `{"category": [topic, topic, ...]}` for
                command-based help.
            db_help_dict (dict): A dict `{"category": [topic, topic], ...]}` for
                database-based help.
            title_lone_category (bool, optional): If a lone category should
                be titled with the category name or not. While pointless in a
                general index, the title should probably show when explicitly
                listing the category itself.
            click_topics (bool, optional): If help-topics are clickable or not
                (for webclient or telnet clients with MXP support).
        Returns:
            str: The help index organized into a grid.

        Notes:
            The input are the pre-loaded help files for commands and database-helpfiles
            respectively. You can override this method to return a custom display of the list of
            commands and topics.

        """

        def _group_by_category(help_dict):
            grid = []
            verbatim_elements = []

            if len(help_dict) == 1 and not title_lone_category:
                # don't list categories if there is only one
                for category in help_dict:
                    # gather and sort the entries from the help dictionary
                    entries = sorted(set(help_dict.get(category, [])))

                    # make the help topics clickable
                    if click_topics:
                        entries = [
                            f"|lchilfe {entry}|lt{entry}|le" for entry in entries
                        ]

                    # add the entries to the grid
                    grid.extend(entries)
            else:
                # list the categories
                for category in sorted(set(list(help_dict.keys()))):
                    category_str = f"-- {category.title()} "
                    grid.append(
                        ANSIString(
                            self.index_category_clr
                            + category_str
                            + "-" * (width - len(category_str))
                            + self.index_topic_clr
                        )
                    )
                    verbatim_elements.append(len(grid) - 1)

                    # gather and sort the entries from the help dictionary
                    entries = sorted(set(help_dict.get(category, [])))

                    # make the help topics clickable
                    if click_topics:
                        entries = [
                            f"|lchilfe {entry}|lt{entry}|le" for entry in entries
                        ]

                    # add the entries to the grid
                    grid.extend(entries)

            return grid, verbatim_elements

        help_index = ""
        width = self.client_width()
        grid = []
        verbatim_elements = []
        cmd_grid, db_grid = "", ""
        sep1, sep2 = "", ""

        if cmd_help_dict and any(cmd_help_dict.values()):
            # get the command-help entries by-category
            sep1 = (
                self.index_type_separator_clr
                + pad("Befehle", width=width, fillchar="-")
                + self.index_topic_clr
            )
            grid, verbatim_elements = _group_by_category(cmd_help_dict)
            gridrows = format_grid(
                grid,
                width,
                sep="  ",
                verbatim_elements=verbatim_elements,
                line_prefix=self.index_topic_clr,
            )
            cmd_grid = ANSIString("\n").join(gridrows) if gridrows else ""

        if db_help_dict and any(db_help_dict.values()):
            # get db-based help entries by-category
            sep2 = (
                self.index_type_separator_clr
                + pad("Game & World", width=width, fillchar="-")
                + self.index_topic_clr
            )
            grid, verbatim_elements = _group_by_category(db_help_dict)
            gridrows = format_grid(
                grid,
                width,
                sep="  ",
                verbatim_elements=verbatim_elements,
                line_prefix=self.index_topic_clr,
            )
            db_grid = ANSIString("\n").join(gridrows) if gridrows else ""

        # only show the main separators if there are actually both cmd and db-based help
        if cmd_grid and db_grid:
            help_index = f"{sep1}\n{cmd_grid}\n{sep2}\n{db_grid}"
        else:
            help_index = f"{cmd_grid}{db_grid}"

        return help_index
