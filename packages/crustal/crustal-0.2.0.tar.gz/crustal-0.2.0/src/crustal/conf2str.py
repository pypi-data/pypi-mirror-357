"""configuration dictionary to string converter

copyright: Odysseus Galanis (ogalanis@geo.auth.gr)
license: -
"""
#TODO add license

__all__ = ["Conf2Str"]

class Conf2Str:
    """Configuration dictionary to string converter.

    The output string is formatted with indentation and newlines
    to represent the structure of the input data. Sensitive keys
    like "pwd", "pass", and "password" are masked with asterisks.

    Attributes:
        confstr (str): The generated configuration string.

    Methods:
        _add_str(self, indent, conf):
            Recursively adds the contents of the input data to
            the confstr attribute.
        __init__(self, conf):
            Initializes the Conf2Str object with the provided
            configuration data.
        get_conf_str(self):
            Returns the generated configuration string.
    """

    confstr = "\n"

    def _add_str(self, indent, conf):
        """Recursively add the contents of the input to confstr.

        Handle indentation and formatting based on the data type.

        Arguments:
            indent (int) -- The current indentation level.
            conf -- The data to be converted (dict, list, or other).
        """

        if isinstance(conf, dict):
            self.confstr += "\n"
            for key in conf:
                self.confstr += ((indent+2)*" " + f"{key}: ")
                if key in ("pwd",
                           "pass",
                           "password"):
                    self._add_str(indent+2, "**********")
                else:
                    self._add_str(indent+2, conf[key])
        elif isinstance(conf, list):
            if isinstance(conf[0], dict):
                self.confstr += "\n"
                for item in conf:
                    self._add_str(indent, item)
                    self.confstr += "\n"
            else:
                self.confstr += f"{conf}\n"
        else:
            self.confstr += f"{conf}\n"
        return

    def __init__(self, conf):
        self._add_str(-2, conf)
        return

    def get_conf_str(self):
        """Return the generated configuration string."""
        return(self.confstr)


def main():
    print(__file__)
    print(__doc__)


if __name__ == "__main__":
    main()


