"""
Telemetry gathering logic.
"""

import time

from pymavlink import mavutil

from ..common.modules.logger import logger


class TelemetryData:  # pylint: disable=too-many-instance-attributes
    """
    Python struct to represent Telemtry Data. Contains the most recent attitude and position reading.
    """

    def __init__(
        self,
        time_since_boot: int | None = None,  # ms
        x: float | None = None,  # m
        y: float | None = None,  # m
        z: float | None = None,  # m
        x_velocity: float | None = None,  # m/s
        y_velocity: float | None = None,  # m/s
        z_velocity: float | None = None,  # m/s
        roll: float | None = None,  # rad
        pitch: float | None = None,  # rad
        yaw: float | None = None,  # rad
        roll_speed: float | None = None,  # rad/s
        pitch_speed: float | None = None,  # rad/s
        yaw_speed: float | None = None,  # rad/s
    ) -> None:
        self.time_since_boot = time_since_boot
        self.x = x
        self.y = y
        self.z = z
        self.x_velocity = x_velocity
        self.y_velocity = y_velocity
        self.z_velocity = z_velocity
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw
        self.roll_speed = roll_speed
        self.pitch_speed = pitch_speed
        self.yaw_speed = yaw_speed

    def __str__(self) -> str:
        return f"""{{
            time_since_boot: {self.time_since_boot},
            x: {self.x},
            y: {self.y},
            z: {self.z},
            x_velocity: {self.x_velocity},
            y_velocity: {self.y_velocity},
            z_velocity: {self.z_velocity},
            roll: {self.roll},
            pitch: {self.pitch},
            yaw: {self.yaw},
            roll_speed: {self.roll_speed},
            pitch_speed: {self.pitch_speed},
            yaw_speed: {self.yaw_speed}
        }}"""


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class Telemetry:
    """
    Telemetry class to read position and attitude (orientation).
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
    ) -> tuple[bool, "Telemetry"]:
        """
        Falliable create (instantiation) method to create a Telemetry object.
        """
        try:
            if connection is None:
                return (False, None)
            instance = cls(cls.__private_key, connection, local_logger)
            local_logger.info("Telemetry instance created", True)
            return (True, instance)
        except Exception as e:
            local_logger.error("Failed to create Telemetry instance", True)
            local_logger.error(str(e), True)
            return (False, None)

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
    ) -> None:
        assert key is Telemetry.__private_key, "Use create() method"
        self._master = connection
        self._logger = local_logger
        self._last_position_ned = None
        self._last_altitude = None
        if self._logger is not None:
            self._logger.info("Telemetry initialized", True)

    def run(self) -> TelemetryData | None:
        """
        Receive LOCAL_POSITION_NED and ATTITUDE messages from the drone,
        combining them together to form a single TelemetryData object.
        """
        msg = self._master.recv_match(type=["LOCAL_POSITION_NED", "ALTITUDE"], blocking=False)
        if msg:
            # Determine the message type
            if msg.get_type() == "LOCAL_POSITION_NED":
                self._last_position_ned = msg
            elif msg.get_type() == "ALTITUDE":
                self._last_altitude = msg
            else:
                self._logger.error(f"Received unexpected message type: {msg.get_type()}", True)
        if self._last_position_ned and self._last_altitude:
            telemetry_data = TelemetryData(
                time_since_boot=self._last_position_ned.time_boot_ms,
                x=self._last_position_ned.x,
                y=self._last_position_ned.y,
                z=self._last_position_ned.z,
                x_velocity=self._last_position_ned.vx,
                y_velocity=self._last_position_ned.vy,
                z_velocity=self._last_position_ned.vz,
                yaw=self._last_position_ned.yaw,
                roll=self._last_position_ned.roll,
                pitch=self._last_position_ned.pitch,
                roll_speed=self._last_position_ned.rollspeed,
                pitch_speed=self._last_position_ned.pitchspeed,
                yaw_speed=self._last_position_ned.yawspeed,
            )
            return telemetry_data
        return None


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
