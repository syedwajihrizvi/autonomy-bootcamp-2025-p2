"""
Heartbeat sending logic.
"""

from pymavlink import mavutil
from modules.common.modules.logger import logger

# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class HeartbeatSender:
    """
    HeartbeatSender class to send a heartbeat
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        logger: logger.Logger | None = None
    ) -> "tuple[True, HeartbeatSender] | tuple[False, None]":
        """
        Falliable create (instantiation) method to create a HeartbeatSender object.
        """
        try:
            if connection is None:
                return (False, None)
            instance = cls(cls.__private_key, connection, logger)
            if logger is not None:
                logger.info("HeartbeatSender instance created", True)
            return (True, instance)
        except:
            if logger is not None:
                logger.error("Failed to create HeartbeatSender instance")
            return (False, None)

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        logger: logger.Logger | None = None
    ):
        assert key is HeartbeatSender.__private_key, "Use create() method"

        # Do any intializiation here
        self._master = connection
        self._logger = logger
        if self._logger is not None:
            self._logger.info("HeartbeatSender initialized", True)

    def run(
        self
    ):
        """
        Attempt to send a heartbeat message.
        """
        self._master.mav.heartbeat_send(
            mavutil.mavlink.MAV_TYPE_GCS,
            mavutil.mavlink.MAV_AUTOPILOT_INVALID,
            0, 0, mavutil.mavlink.MAV_STATE_ACTIVE
        )
        if self._logger is not None:
            self._logger.info("Heartbeat sent", True)

# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
