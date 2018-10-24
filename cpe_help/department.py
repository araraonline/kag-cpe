
"""
This is the main file for dealing with departments

Probably will become the main file of the project.
"""

from importlib import import_module

from cpe_help.util.path import DATA_DIR


class Department(object):
    """
    Represents a police department

    All department related functionality will be here.
    """

    @property
    def dir(self):
        """
        Return the directory containing the department data

        Returns
        -------
        Path
            A pathlib.Path object representing the directory.
        """
        return DATA_DIR / 'departments' / self.name

    def __new__(cls, name):
        """
        Create a new department object

        This method makes the Department constructor return a specific
        subclass, based on the name.

        Parameters
        ----------
        name : str
            Represents the department name, e.g. '37-00027' for Austin.

        Returns
        -------
        Department object
        """
        # avoid direct instantiation of subclasses
        assert cls == Department

        name = name.replace('-', '')
        module_name = f"cpe_help.departments.dept{name}"
        class_name = f"Department{name}"

        try:
            # instantiate specific subclass
            mod = import_module(module_name)
            klass = getattr(mod, class_name)
            return super().__new__(klass)
        except ModuleNotFoundError:
            # no specific subclass
            # use generic version Department
            return super().__new__(cls)

    def __init__(self, name):
        """
        Initialize a new department object

        Parameters
        ----------
        name : str
            Represents the department name, e.g. '37-00027' for Austin.
        """
        self.name = name

    def __repr__(self):
        return "{klass}({name!r})".format(
            klass=type(self).__name__,
            name=self.name,
        )


def list_departments():
    """
    Returns a list with all available Department's
    """
    return [Department(x.name) for x in (DATA_DIR / 'departments').iterdir()]
