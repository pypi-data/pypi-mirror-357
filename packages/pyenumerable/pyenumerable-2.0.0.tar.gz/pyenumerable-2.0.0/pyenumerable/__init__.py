"""
Implementation of .NET's IEnumerable interface in python W/ support for generics.
"""  # noqa: E501

from pyenumerable.constructors import pp_enumerable
from pyenumerable.implementations import PurePythonEnumerable
from pyenumerable.protocol import Enumerable

__all__ = ["Enumerable", "PurePythonEnumerable", "pp_enumerable"]
__author__ = "AmirHossein Ahmadi"
__license__ = "WTFPL"
__version__ = "2.0.0"
__maintainer__ = "AmirHossein Ahmadi"
__email__ = "amirthehossein@gmail.com"
__documentation__ = "https://github.com/amirongit/PyEnumerable/blob/master/documentation.md"
