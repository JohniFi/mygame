r"""
Evennia settings file.

The available options are found in the default settings file found
here:

https://www.evennia.com/docs/latest/Setup/Settings-Default.html

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "mygame"

# Controls whether new account registration is available.
# Set to False to lock down the registration page and the create account command.
#NEW_ACCOUNT_REGISTRATION_ENABLED = False

# Activate telnet service
TELNET_ENABLED = False


######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")


######################################################################
# Django web features
######################################################################

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
LANGUAGE_CODE = 'de'

# Where to find locales (no need to change this, most likely)
# prio translation files from game over evennia core
LOCALE_PATHS = [os.path.join(GAME_DIR, "locale/"), os.path.join(EVENNIA_DIR, "locale/")]

######################################################################
# Help system
######################################################################

# The help category of a command if not specified.
COMMAND_DEFAULT_HELP_CATEGORY = "allgemein"
