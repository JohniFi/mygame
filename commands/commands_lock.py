from evennia.commands.default import (
    account,
    general,
)


# ----- GENERAL -----
class CmdNick(general.CmdNick):
    locks = "cmd:perm(Builder)"


class CmdAccess(general.CmdAccess):
    locks = "cmd:perm(Builder)"


# ----- ACCOUNT -----
class CmdCharCreate(account.CmdCharCreate):
    locks = "cmd:perm(Admin)"


class CmdCharDelete(account.CmdCharDelete):
    locks = "cmd:perm(Admin)"


class CmdIC(account.CmdIC):
    locks = "cmd:perm(Builder)"


class CmdOOC(account.CmdOOC):
    locks = "cmd:perm(Builder)"


class CmdSessions(account.CmdSessions):
    locks = "cmd:perm(Builder)"


class CmdOption(account.CmdOption):
    locks = "cmd:perm(Builder)"


class CmdColorTest(account.CmdColorTest):
    locks = "cmd:perm(Builder)"


class CmdQuell(account.CmdQuell):
    locks = "cmd:perm(Builder)"


class CmdStyle(account.CmdStyle):
    locks = "cmd:perm(Builder)"
