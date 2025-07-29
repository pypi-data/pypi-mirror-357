try:
    from ._fastlap_rs import solve_lap
except ImportError:
    from _fastlap_rs import solve_lap

from typing import List
def supported_algos() -> List[str]:
    return ["lapjv", "hungarian", "lapmod"]

__all__ = ['solve_lap', 'supported_algos']