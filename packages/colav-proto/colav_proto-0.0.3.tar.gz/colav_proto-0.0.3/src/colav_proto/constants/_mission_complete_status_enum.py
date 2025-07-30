from enum import Enum

class MissionCompleteStatus(Enum): 
    UNKNOWN = 0
    SUCCEEDED = 1
    CANCELED = 2
    ABORTED = 3