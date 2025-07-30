
from colav_proto.generated.python.colav.system import (
    MapMetaData,
    MissionRequest,
    MissionResponse,
    MissionComplete
)
from colav_proto.generated.python.colav.automaton.dynamics import (
    Dynamics
)
from colav_proto.generated.python.colav.automaton.states import (
    AgentState,
    DynamicObstacleRiskState,
    DynamicObstacleState,
    StaticObstacleRiskState,
    StaticObstacleState,
    ObstaclesState,
    ObstaclesRiskState,
    UnsafeSetState
)
from colav_proto.generated.python.colav.automaton import (
    AutomatonOutput
)
from enum import Enum
import math
from typing import Union
import logging
from colav_proto._internal import ProtoTypeEnum
from colav_proto._internal.proto_type_class_map import PROTO_CLASS_MAP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from colav_proto.generated.python.colav import WrapperMessage

def deserialize_protobuf(protobuf: bytes) -> Union[
    MissionRequest, 
    MissionResponse, 
    AgentState, 
    ObstaclesRiskState, 
    ObstaclesState, 
    DynamicObstacleState, 
    StaticObstacleState, 
    StaticObstacleRiskState, 
    DynamicObstacleRiskState, 
    UnsafeSetState,
    MapMetaData,
    MissionComplete
]:
    try: 
        msg = WrapperMessage()
        msg.ParseFromString(protobuf)
        proto_enum = ProtoTypeEnum(msg.type)
        message_class = PROTO_CLASS_MAP[proto_enum]
        message_instance = message_class()
        message_instance.ParseFromString(msg.payload)
        return message_instance
    except Exception as e: 
        raise e