from .characters import Character


class NPC(Character):
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
        self.msg(
            "Dein Geist fährt in den Körper von {name}.".format(name=self.get_display_name(self))
        )
        self.msg((self.at_look(self.location), {"type": "look"}), options=None)

        def message(obj, from_obj):
            obj.msg(
                "Der Geist von {puppeteer} fährt in den Körper von {name}.".format(
                    name=self.get_display_name(obj), puppeteer=self.account.get_display_name(obj)
                ),
                from_obj=from_obj,
            )

        self.location.for_contents(message, exclude=[self], from_obj=self)

    def at_post_unpuppet(self, account=None, session=None, **kwargs):
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
        account.msg(
            "Du verlässt den Körper von {name}.\n".format(name=self.get_display_name(self))
        )
        self.msg((self.at_look(self.location), {"type": "look"}), options=None)

        def message(obj, from_obj):
            obj.msg(
                "Der Geist von {puppeteer} verlässt den Körper von {name}.".format(
                    name=self.get_display_name(obj), puppeteer=account.get_display_name(obj)
                ),
                from_obj=from_obj,
            )

        self.location.for_contents(message, exclude=[self], from_obj=self)
