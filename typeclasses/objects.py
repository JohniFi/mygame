"""
Object

The Object is the class for general items in the game world.

Use the ObjectParent class to implement common features for *all* entities
with a location in the game world (like Characters, Rooms, Exits).

"""

from collections import defaultdict
from typing import Iterable, Optional, Self, cast, override
from django.utils.translation import gettext as _
from evennia.objects.models import ObjectDB
from evennia.objects.objects import DefaultObject
from evennia.typeclasses.attributes import AttributeProperty
from evennia.typeclasses.models import AttributeHandler
from evennia.typeclasses.tags import AliasHandler, TagHandler
from evennia.utils.utils import iter_to_str, make_iter
from world.enums import ObjectType


class ObjectParent(DefaultObject):
    """
    This is a mixin that can be used to override *all* entities inheriting at
    some distance from DefaultObject (Objects, Exits, Characters and Rooms).

    Just add any method that exists on `DefaultObject` to this class. If one
    of the derived classes has itself defined that same hook already, that will
    take precedence.

    """

    # Used by get_display_desc when self.db.desc is None
    default_description = _("Du siehst nichts Besonderes")

    # used in get_display_name()
    color_code = AttributeProperty(default="|w")

    # TODO: evaluate LANGUAGE_CODE and only overwrite methods if German (DE)
    # TODO: i18n of Strings from "mygame". Possibly add pullrequest to mark Strings here with _("...") so you don't need to overwrite get_display_things

    @override
    def get_display_name(self, looker=None, **kwargs):
        """
        Displays the name of the object in a viewer-aware manner.

        Args:
            looker (DefaultObject): The object or account that is looking at or getting information
                for this object.

        Returns:
            str: A name to display for this object. By default this returns the `.name` of the object.

        Notes:
            This function can be extended to change how object names appear to users in character,
            but it does not change an object's keys or aliases when searching.

        """
        name = kwargs.get("key", self.name)
        return f"{self.color_code}{name}|n"

    @override
    def get_search_direct_match(self, searchdata, **kwargs):
        """
        This method is called by the search method to allow for direct
        replacements, such as 'me' always being an alias for this object.

        Args:
            searchdata (str): The search string to replace.
            **kwargs (any): These are the same as passed to the `search` method.

        Returns:
            tuple: A tuple `(should_return, str or Obj)`, where `should_return` is a boolean
            indicating the `.search` method should return the result immediately without further
            processing. If `should_return` is `True`, the second element of the tuple is the result
            that is returned.

        """
        if isinstance(searchdata, str):
            candidates = kwargs.get("candidates") or []
            global_search = kwargs.get("global_search", False)
            match searchdata.lower():
                case "me" | "self" | "mich" | "mir" | "selbst":
                    return global_search or self in candidates, self
                case "here" | "hier":
                    return global_search or self.location in candidates, self.location
        return False, searchdata

    @override
    def get_numbered_name(self, count, looker, **kwargs):
        """
        Returns the object's name with correct pluralization and article.

        looks up object tag "gender" and attributes "plural", and "case"
        tag_category: "gender"; tags: ("m", "f", "n")
        "plural": <plural name of object>
        at the moment only case supportet: "accusative": <accusative singular name of object>
        default case "nominative" is just the key

        definite_article=True for definite article. Else default indefinite article
        """

        # TODO: add object tag "unique" that always leads to definit article

        key = kwargs.get("key", self.name)
        article_type = "def" if kwargs.get("definite_article") else "indef"
        case = kwargs.get("case", "nominative")

        self_tags = cast(TagHandler, self.tags)
        gender = (self_tags.get(category="gender") or ["n"])[0]

        # Retrieve custom attribute "plural"
        self_attributes = cast(AttributeHandler, self.attributes)
        plural = self_attributes.get("plural", default=key)

        if self_attributes.has(case):
            if case == "accusative" and count == 1:
                # use accusative for singular
                key = self_attributes.get(case)
        # TODO: handle plural cases for "dative" and "genitive" (accusative plural = nominative plural)

        if kwargs.get("no_article") and count == 1:
            key = self.get_display_name(looker, key=key)
            plural = self.get_display_name(looker, key=plural)
            if kwargs.get("return_string"):
                return key if count == 1 else plural
            return key, plural

        articles = {
            "nominative": {
                "m": {"indef": "ein", "def": "der"},
                "f": {"indef": "eine", "def": "die"},
                "n": {"indef": "ein", "def": "das"},
                "pl": {"indef": "", "def": "die "},
            },
            "accusative": {
                "m": {"indef": "einen", "def": "den"},
                "f": {"indef": "eine", "def": "die"},
                "n": {"indef": "ein", "def": "das"},
                "pl": {"indef": "", "def": "die "},
            },
            "dative": {
                "m": {"indef": "einem", "def": "dem"},
                "f": {"indef": "einer", "def": "der"},
                "n": {"indef": "einem", "def": "dem"},
                "pl": {"indef": "", "def": "den "},
            },
            "genitive": {
                "m": {"indef": "eines", "def": "des"},
                "f": {"indef": "einer", "def": "der"},
                "n": {"indef": "eines", "def": "des"},
                "pl": {"indef": "", "def": "der "},
            },
        }

        case_dict = articles.get(case, articles["nominative"])
        article_singular = case_dict.get(gender, case_dict["n"]).get(article_type, "ein")

        num = ""
        # if count == 0:
        #     article_plural = "k" + articles.get(case, "nominative").get(gender, "n").get("indef")
        #     # ein -> kein, eine -> keine TODO: not working because it adds plural noun
        if count == 1:
            article_plural = article_singular
        else:
            match count:
                case count if count in range(2, 12 + 1):
                    num = {
                        2: "zwei",
                        3: "drei",
                        4: "vier",
                        5: "fünf",
                        6: "sechs",
                        7: "sieben",
                        8: "acht",
                        9: "neun",
                        10: "zehn",
                        11: "elf",
                        12: "zwölf",
                    }.get(count)
                case _:
                    num = count

            article_plural = "{}{}".format(case_dict["pl"].get(article_type, "die"), num)

        # update aliases
        # plural (without article)
        self_aliases = cast(AliasHandler, self.aliases)
        self_aliases.add(plural, category=self.plural_category)
        # self.aliases.add(plural, category=self.plural_category)
        # singular (with article)
        self_aliases.add(f"{article_singular} {key}", category=self.plural_category)
        # self.aliases.add(f"{article_singular} {key}", category=self.plural_category)

        # format strings with color formatting of the noun via get_display_name
        singular = f"{article_singular} {self.get_display_name(looker, key=key)}"
        plural = f"{article_plural} {self.get_display_name(looker, key=plural)}"

        if kwargs.get("return_string"):
            return singular if count == 1 else plural

        return singular, plural

    @override
    def get_display_exits(self, looker, **kwargs):
        """
        Get the 'exits' component of the object description. Called by `return_appearance`.

        Args:
            looker (DefaultObject): Object doing the looking.
            **kwargs: Arbitrary data for use when overriding.

        Keyword Args:
            exit_order (iterable of str): The order in which exits should be listed, with
                unspecified exits appearing at the end, alphabetically.

        Returns:
            str: The exits display data.

        Examples:
        ::

            For a room with exits in the order 'portal', 'south', 'north', and 'out':
                obj.get_display_name(looker, exit_order=('north', 'south'))
                    -> "Exits: north, south, out, and portal."  (markup not shown here)
        """

        def _sort_exit_names(names):
            exit_order = kwargs.get("exit_order")
            if not exit_order:
                return names
            sort_index = {name: key for key, name in enumerate(exit_order)}
            names = sorted(names)
            end_pos = len(sort_index)
            names.sort(key=lambda name: sort_index.get(name, end_pos))
            return names

        exits = self.filter_visible(self.contents_get(content_type="exit"), looker, **kwargs)
        exit_names = (exi.get_display_name(looker, **kwargs) for exi in exits)
        exit_names = iter_to_str(
            _sort_exit_names(exit_names), endsep=_("und")
        )  # TODO: Pull-Request for i18n

        return (
            _("|wAusgänge:|n {e}").format(e=exit_names) if exit_names else ""
        )  # TODO: Pull-Request for i18

    @override
    def get_display_characters(self, looker, **kwargs):
        """
        Get the 'characters' component of the object description. Called by `return_appearance`.

        Args:
            looker (DefaultObject): Object doing the looking.
            **kwargs: Arbitrary data for use when overriding.
        Returns:
            str: The character display data.

        """
        characters = self.filter_visible(
            self.contents_get(content_type="character"), looker, **kwargs
        )
        character_names = iter_to_str(
            (char.get_display_name(looker, **kwargs) for char in characters),
            endsep=_("und"),  # TODO: Pull-Request for i18
        )

        return (
            _("|wCharaktere:|n {c}").format(c=character_names) if character_names else ""
        )  # TODO: Pull-Request for i18

    @override
    def get_display_things(self, looker, **kwargs):
        """
        Get the 'things' component of the object description. Called by `return_appearance`.

        Args:
            looker (DefaultObject): Object doing the looking.
            **kwargs: Arbitrary data for use when overriding.
        Returns:
            str: The things display data.

        """
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
            thing_names, endsep=_("und")
        )  # TODO: Pull-Request for `endsep` i18n
        return (
            _("|wDu siehst:|n {thing_names}").format(
                thing_names=thing_names
            )  # TODO: Pull-Request for i18n
            if thing_names
            else ""
        )

    @override
    def announce_move_from(self, destination, msg=None, mapping=None, move_type="move", **kwargs):
        """
        Called if the move is to be announced. This is
        called while we are still standing in the old
        location.

        Args:
            destination (DefaultObject): The place we are going to.
            msg (str, optional): a replacement message.
            mapping (dict, optional): additional mapping objects.
            move_type (str): The type of move. "give", "traverse", etc.
                This is an arbitrary string provided to obj.move_to().
                Useful for altering messages or altering logic depending
                on the kind of movement.
            **kwargs: Arbitrary, optional arguments for users
                overriding the call (unused by default).

        Notes:

            You can override this method and call its parent with a
            message to simply change the default message.  In the string,
            you can use the following as mappings:

            - `{object}`: the object which is moving.
            - `{exit}`: the exit from which the object is moving (if found).
            - `{origin}`: the location of the object before the move.
            - `{destination}`: the location of the object after moving.

        """
        if not self.location:
            return
        if msg:
            string = msg
        else:
            string = _(
                "{object} verlässt {origin} in Richtung {destination}."
            )  # TODO: Pull-Request for i18

        location = self.location
        exits = [
            o for o in location.contents if o.location is location and o.destination is destination
        ]
        if not mapping:
            mapping = {}

        mapping.update(
            {
                "object": self,
                "exit": exits[0] if exits else "irgendwo",  # TODO: Pull-Request for i18
                "origin": location or "nirgendwo",  # TODO: Pull-Request for i18
                "destination": destination or "nirgendwo",  # TODO: Pull-Request for i18
            }
        )

        location.msg_contents(
            (string, {"type": move_type}),
            exclude=(self,),
            from_obj=self,
            mapping=mapping,
        )

    @override
    def at_say(
        self,
        message,
        msg_self=None,
        msg_location=None,
        receivers: Optional[Iterable] = None,
        msg_receivers=None,
        **kwargs,
    ):
        """
        Display the actual say (or whisper) of self.

        This hook should display the actual say/whisper of the object in its
        location.  It should both alert the object (self) and its
        location that some text is spoken.  The overriding of messages or
        `mapping` allows for simple customization of the hook without
        re-writing it completely.

        Args:
            message (str): The message to convey.
            msg_self (bool or str, optional): If boolean True, echo `message` to self. If a string,
                return that message. If False or unset, don't echo to self.
            msg_location (str, optional): The message to echo to self's location.
            receivers (DefaultObject or iterable, optional): An eventual receiver or receivers of the
                message (by default only used by whispers).
            msg_receivers(str): Specific message to pass to the receiver(s). This will parsed
                with the {receiver} placeholder replaced with the given receiver.
        Keyword Args:
            whisper (bool): If this is a whisper rather than a say. Kwargs
                can be used by other verbal commands in a similar way.
            mapping (dict): Pass an additional mapping to the message.

        Notes:


            Messages can contain {} markers. These are substituted against the values
            passed in the `mapping` argument.
            ::

                msg_self = 'You say: "{speech}"'
                msg_location = '{object} says: "{speech}"'
                msg_receivers = '{object} whispers: "{speech}"'

            Supported markers by default:

            - {self}: text to self-reference with (default 'You')
            - {speech}: the text spoken/whispered by self.
            - {object}: the object speaking.
            - {receiver}: replaced with a single receiver only for strings meant for a specific
              receiver (otherwise 'None').
            - {all_receivers}: comma-separated list of all receivers,
              if more than one, otherwise same as receiver
            - {location}: the location where object is.

        """
        msg_type = "say"
        if kwargs.get("whisper", False):
            # whisper mode
            msg_type = "whisper"
            msg_self = (
                _(
                    '{self} flüsterst {all_receivers} zu: "|n{speech}|n"'
                )  # TODO: Pull-Request for i18n
                if msg_self is True
                else msg_self
            )
            msg_receivers = msg_receivers or _(
                '{object} flüstert: "|n{speech}|n"'
            )  # TODO: Pull-Request for i18n
            msg_location = None
        else:
            msg_self = (
                _('{self} sagst: "|n{speech}|n"') if msg_self is True else msg_self
            )  # TODO: Pull-Request for i18
            msg_location = msg_location or '{object} sagt, "{speech}"'
            msg_receivers = msg_receivers or message

        custom_mapping = kwargs.get("mapping", {})
        if receivers:
            receivers = cast(Iterable[Self], make_iter(receivers))
        location = cast(ObjectDB, self.location)

        if msg_self:
            self_mapping = {
                "self": _("Du"),  # TODO: Pull-Request for i18n
                "object": self.get_display_name(self),
                "location": location.get_display_name(self) if location else None,
                "receiver": None,
                "all_receivers": (
                    ", ".join(recv.get_display_name(self) for recv in receivers)
                    if receivers
                    else None
                ),
                "speech": message,
            }
            self_mapping.update(custom_mapping)
            self.msg(
                text=(msg_self.format_map(self_mapping), {"type": msg_type}),
                from_obj=self,
            )

        if receivers and msg_receivers:
            receiver_mapping = {
                "self": _("Du"),  # TODO: Pull-Request for i18n
                "object": None,
                "location": None,
                "receiver": None,
                "all_receivers": None,
                "speech": message,
            }
            for receiver in receivers:
                receiver: Object
                individual_mapping = {
                    "object": self.get_display_name(receiver),
                    "location": location.get_display_name(receiver),
                    "receiver": receiver.get_display_name(receiver),
                    "all_receivers": (
                        ", ".join(recv.get_display_name(recv) for recv in receivers)
                        if receivers
                        else None
                    ),
                }
                receiver_mapping.update(individual_mapping)
                receiver_mapping.update(custom_mapping)
                receiver.msg(
                    text=(
                        msg_receivers.format_map(receiver_mapping),
                        {"type": msg_type},
                    ),
                    from_obj=self,
                )

        if self.location and msg_location:
            location_mapping = {
                "self": _("Du"),  # TODO: Pull-Request for i18
                "object": self,
                "location": location,
                "all_receivers": (
                    ", ".join(str(recv) for recv in receivers) if receivers else None
                ),
                "receiver": None,
                "speech": message,
            }
            location_mapping.update(custom_mapping)
            exclude = []
            if msg_self:
                exclude.append(self)
            if receivers:
                exclude.extend(receivers)
            self.location.msg_contents(
                text=(msg_location, {"type": msg_type}),
                from_obj=self,
                exclude=exclude,
                mapping=location_mapping,
            )

    @override
    def at_rename(self, oldname, newname):
        """
        This Hook is called by @name on a successful rename.

        Args:
            oldname (str): The instance's original name.
            newname (str): The new name for the instance.

        """

        # Clear plural aliases set by DefaultObject.get_numbered_name
        cast(AliasHandler, self.aliases).clear(category=self.plural_category)
        # Clear plural and accusative attributes
        self_attributes = cast(AttributeHandler, self.attributes)
        self_attributes.remove("plural")
        self_attributes.remove("accusative")
        # probably same gender, so keep that for now
        # self.attributes.remove("gender")


class Object(ObjectParent, DefaultObject):
    """
    This is the root Object typeclass, representing all entities that
    have an actual presence in-game. DefaultObjects generally have a
    location. They can also be manipulated and looked at. Game
    entities you define should inherit from DefaultObject at some distance.

    It is recommended to create children of this class using the
    `evennia.create_object()` function rather than to initialize the class
    directly - this will both set things up and efficiently save the object
    without `obj.save()` having to be called explicitly.

    Note: Check the autodocs for complete class members, this may not always
    be up-to date.

    * Base properties defined/available on all Objects

     key (string) - name of object
     name (string)- same as key
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     date_created (string) - time stamp of object creation

     account (Account) - controlling account (if any, only set together with
                       sessid below)
     sessid (int, read-only) - session id (if any, only set together with
                       account above). Use `sessions` handler to get the
                       Sessions directly.
     location (Object) - current location. Is None if this is a room
     home (Object) - safety start-location
     has_account (bool, read-only)- will only return *connected* accounts
     contents (list, read only) - returns all objects inside this object
     exits (list of Objects, read-only) - returns all exits from this
                       object, if any
     destination (Object) - only set if this object is an exit.
     is_superuser (bool, read-only) - True/False if this user is a superuser
     is_connected (bool, read-only) - True if this object is associated with
                            an Account with any connected sessions.
     has_account (bool, read-only) - True is this object has an associated account.
     is_superuser (bool, read-only): True if this object has an account and that
                        account is a superuser.

    * Handlers available

     aliases - alias-handler: use aliases.add/remove/get() to use.
     permissions - permission-handler: use permissions.add/remove() to
                   add/remove new perms.
     locks - lock-handler: use locks.add() to add new lock strings
     scripts - script-handler. Add new scripts to object with scripts.add()
     cmdset - cmdset-handler. Use cmdset.add() to add new cmdsets to object
     nicks - nick-handler. New nicks with nicks.add().
     sessions - sessions-handler. Get Sessions connected to this
                object with sessions.get()
     attributes - attribute-handler. Use attributes.add/remove/get.
     db - attribute-handler: Shortcut for attribute-handler. Store/retrieve
            database attributes using self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not create
            a database entry when storing data

    * Helper methods (see src.objects.objects.py for full headers)

     get_search_query_replacement(searchdata, **kwargs)
     get_search_direct_match(searchdata, **kwargs)
     get_search_candidates(searchdata, **kwargs)
     get_search_result(searchdata, attribute_name=None, typeclass=None,
                       candidates=None, exact=False, use_dbref=None, tags=None, **kwargs)
     get_stacked_result(results, **kwargs)
     handle_search_results(searchdata, results, **kwargs)
     search(searchdata, global_search=False, use_nicks=True, typeclass=None,
            location=None, attribute_name=None, quiet=False, exact=False,
            candidates=None, use_locks=True, nofound_string=None,
            multimatch_string=None, use_dbref=None, tags=None, stacked=0)
     search_account(searchdata, quiet=False)
     execute_cmd(raw_string, session=None, **kwargs))
     msg(text=None, from_obj=None, session=None, options=None, **kwargs)
     for_contents(func, exclude=None, **kwargs)
     msg_contents(message, exclude=None, from_obj=None, mapping=None,
                  raise_funcparse_errors=False, **kwargs)
     move_to(destination, quiet=False, emit_to_obj=None, use_destination=True)
     clear_contents()
     create(key, account, caller, method, **kwargs)
     copy(new_key=None)
     at_object_post_copy(new_obj, **kwargs)
     delete()
     is_typeclass(typeclass, exact=False)
     swap_typeclass(new_typeclass, clean_attributes=False, no_default=True)
     access(accessing_obj, access_type='read', default=False,
            no_superuser_bypass=False, **kwargs)
     filter_visible(obj_list, looker, **kwargs)
     get_default_lockstring()
     get_cmdsets(caller, current, **kwargs)
     check_permstring(permstring)
     get_cmdset_providers()
     get_display_name(looker=None, **kwargs)
     get_extra_display_name_info(looker=None, **kwargs)
     get_numbered_name(count, looker, **kwargs)
     get_display_header(looker, **kwargs)
     get_display_desc(looker, **kwargs)
     get_display_exits(looker, **kwargs)
     get_display_characters(looker, **kwargs)
     get_display_things(looker, **kwargs)
     get_display_footer(looker, **kwargs)
     format_appearance(appearance, looker, **kwargs)
     return_apperance(looker, **kwargs)

    * Hooks (these are class methods, so args should start with self):

     basetype_setup()     - only called once, used for behind-the-scenes
                            setup. Normally not modified.
     basetype_posthook_setup() - customization in basetype, after the object
                            has been created; Normally not modified.

     at_object_creation() - only called once, when object is first created.
                            Object customizations go here.
     at_object_delete() - called just before deleting an object. If returning
                            False, deletion is aborted. Note that all objects
                            inside a deleted object are automatically moved
                            to their <home>, they don't need to be removed here.

     at_init()            - called whenever typeclass is cached from memory,
                            at least once every server restart/reload
     at_first_save()
     at_cmdset_get(**kwargs) - this is called just before the command handler
                            requests a cmdset from this object. The kwargs are
                            not normally used unless the cmdset is created
                            dynamically (see e.g. Exits).
     at_pre_puppet(account)- (account-controlled objects only) called just
                            before puppeting
     at_post_puppet()     - (account-controlled objects only) called just
                            after completing connection account<->object
     at_pre_unpuppet()    - (account-controlled objects only) called just
                            before un-puppeting
     at_post_unpuppet(account) - (account-controlled objects only) called just
                            after disconnecting account<->object link
     at_server_reload()   - called before server is reloaded
     at_server_shutdown() - called just before server is fully shut down

     at_access(result, accessing_obj, access_type) - called with the result
                            of a lock access check on this object. Return value
                            does not affect check result.

     at_pre_move(destination)             - called just before moving object
                        to the destination. If returns False, move is cancelled.
     announce_move_from(destination)         - called in old location, just
                        before move, if obj.move_to() has quiet=False
     announce_move_to(source_location)       - called in new location, just
                        after move, if obj.move_to() has quiet=False
     at_post_move(source_location)          - always called after a move has
                        been successfully performed.
     at_pre_object_leave(leaving_object, destination, **kwargs)
     at_object_leave(obj, target_location, move_type="move", **kwargs)
     at_object_leave(obj, target_location)   - called when an object leaves
                        this object in any fashion
     at_pre_object_receive(obj, source_location)
     at_object_receive(obj, source_location, move_type="move", **kwargs) - called when this object receives
                        another object
     at_post_move(source_location, move_type="move", **kwargs)

     at_traverse(traversing_object, target_location, **kwargs) - (exit-objects only)
                              handles all moving across the exit, including
                              calling the other exit hooks. Use super() to retain
                              the default functionality.
     at_post_traverse(traversing_object, source_location) - (exit-objects only)
                              called just after a traversal has happened.
     at_failed_traverse(traversing_object)      - (exit-objects only) called if
                       traversal fails and property err_traverse is not defined.

     at_msg_receive(self, msg, from_obj=None, **kwargs) - called when a message
                             (via self.msg()) is sent to this obj.
                             If returns false, aborts send.
     at_msg_send(self, msg, to_obj=None, **kwargs) - called when this objects
                             sends a message to someone via self.msg().

     return_appearance(looker) - describes this object. Used by "look"
                                 command by default
     at_desc(looker=None)      - called by 'look' whenever the
                                 appearance is requested.
     at_pre_get(getter, **kwargs)
     at_get(getter)            - called after object has been picked up.
                                 Does not stop pickup.
     at_pre_give(giver, getter, **kwargs)
     at_give(giver, getter, **kwargs)
     at_pre_drop(dropper, **kwargs)
     at_drop(dropper, **kwargs)          - called when this object has been dropped.
     at_pre_say(speaker, message, **kwargs)
     at_say(message, msg_self=None, msg_location=None, receivers=None, msg_receivers=None, **kwargs)

     at_look(target, **kwargs)
     at_desc(looker=None)

    """

    obj_type: list[ObjectType] = []

    @override
    def at_object_creation(self):
        super().at_object_creation()
        for obj_type in self.obj_type:
            cast(TagHandler, self.tags).add(obj_type.value, category="obj_type")
