from .objects import Object

class Ownable(Object):
    """
    An Objec with a set_owner() method that can for example set locks on an object. 
    Gets called from the CmdGive with special switch `/eigentum`
    """

    def set_owner(self, setter, target, **kwargs):
        pass
