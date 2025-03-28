"""
Command sets

All commands in the game must be grouped in a cmdset.  A given command
can be part of any number of cmdsets and cmdsets can be added/removed
and merged onto entities at runtime.

To create new commands to populate the cmdset, see
`commands/command.py`.

This module wraps the default command sets of Evennia; overloads them
to add/remove commands from the default lineup. You can create your
own cmdsets by inheriting from them or directly from `evennia.CmdSet`.

"""

from typing import override
from evennia import default_cmds
from evennia.commands.default import (
    general,
)
from commands import commands_de
from commands import commands_lock
from .containers import ContainerCmdSet


class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    The `CharacterCmdSet` contains general in-game commands like `look`,
    `get`, etc available on in-game Character objects. It is merged with
    the `AccountCmdSet` when an Account puppets a Character.
    """

    key = "DefaultCharacter"

    @override
    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        self.add(commands_de.CmdLook())

        self.add(commands_lock.CmdNick)

        self.add(commands_de.CmdInventory())

        self.remove(general.CmdGet())
        self.add(commands_de.CmdGet())

        self.add(commands_de.CmdDrop())

        self.remove(general.CmdGive())
        self.add(commands_de.CmdGive())

        self.add(commands_de.CmdSetDesc())

        self.add(commands_de.CmdSay())

        self.remove(general.CmdWhisper())
        self.add(commands_de.CmdWhisper())

        self.add(commands_de.CmdPose())

        self.add(commands_lock.CmdAccess())

        self.add(commands_de.CmdHelp())

        # Container commands
        self.add(ContainerCmdSet)


class AccountCmdSet(default_cmds.AccountCmdSet):
    """
    This is the cmdset available to the Account at all times. It is
    combined with the `CharacterCmdSet` when the Account puppets a
    Character. It holds game-account-specific commands, channel
    commands, etc.
    """

    key = "DefaultAccount"

    @override
    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        
        # hide some commands from normal players
        self.add(commands_lock.CmdCharCreate())
        self.add(commands_lock.CmdCharDelete())
        self.add(commands_lock.CmdIC())
        self.add(commands_lock.CmdOOC())
        self.add(commands_lock.CmdSessions())
        self.add(commands_lock.CmdOption())
        self.add(commands_lock.CmdColorTest())
        self.add(commands_lock.CmdQuell())
        self.add(commands_lock.CmdStyle())


class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    """
    Command set available to the Session before being logged in.  This
    holds commands like creating a new account, logging in, etc.
    """

    key = "DefaultUnloggedin"

    @override
    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class SessionCmdSet(default_cmds.SessionCmdSet):
    """
    This cmdset is made available on Session level once logged in. It
    is empty by default.
    """

    key = "DefaultSession"

    @override
    def at_cmdset_creation(self):
        """
        This is the only method defined in a cmdset, called during
        its creation. It should populate the set with command instances.

        As and example we just add the empty base `Command` object.
        It prints some info.
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
