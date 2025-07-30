import sys
from pprint import pprint
from typing import Any, Union

def dier(*args: Any, exit: Union[bool, int] = False) -> None:
    for msg in args:
        pprint(msg)
    if exit is False or exit == 0:
        return
    sys.exit(exit if isinstance(exit, int) else 1)
