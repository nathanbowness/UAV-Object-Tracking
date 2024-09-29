from enum import Enum

class RunType(Enum):
    """
    Enumeration of the different run modes for the program.

    This Enum class defines the modes in which the program can be executed, based on how data is processed and stored.

    Attributes
    ----------
    LIVE : int
        The program processes data in real-time without recording it.
    RERUN : ints
        The program reads and processes data from a pre-recorded sample file. Requires an existing `DataFormat` for reading the data.
    """
    LIVE = 1
    RERUN = 2