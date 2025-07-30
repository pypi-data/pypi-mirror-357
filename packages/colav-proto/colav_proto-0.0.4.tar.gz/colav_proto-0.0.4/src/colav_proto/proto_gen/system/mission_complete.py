from colav_proto.generated.python.colav.system.mission_complete_pb2 import MissionComplete
from colav_proto.constants._mission_complete_status_enum import MissionStatusEnum
from colav_proto.types import Stamp

def gen_mission_completion_msg(
    mission_tag: str,
    success: bool,
    status: MissionStatusEnum,
    error: bool,
    message: str,
    stamp: Stamp,
):
    """
    Generate a MissionRequest protobuf message for a mission request.

    Constructs and returns a MissionRequest message containing the mission tag, timestamp, and a list of goal waypoints,
    each with position and orientation information. Raises an exception if message construction fails.

    Args:
        mission_tag (str): Unique identifier for the mission.
        stamp (Stamp): Timestamp for the mission request.
        goal_waypoints (List[Waypoint]): List of goal waypoints, each with position and orientation.

    Returns:
        MissionRequest: The constructed MissionRequest protobuf message.

    Raises:
        Exception: If message construction fails.
    """
    try: 
        msg = MissionComplete()
        msg.mission_tag = mission_tag

        msg.success = success
        msg.status = status.value
        msg.error = error
        msg.message = message
        msg.stamp.sec = stamp.sec
        msg.stamp.nanosec = stamp.nanosec
        return msg
    except Exception as e:
        raise