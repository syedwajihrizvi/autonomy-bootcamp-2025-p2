"""
Decision-making logic.
"""

import math

from pymavlink import mavutil

from ..common.modules.logger import logger
from ..telemetry import telemetry


class Position:
    """
    3D vector struct.
    """

    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class Command:  # pylint: disable=too-many-instance-attributes
    """
    Command class to make a decision based on recieved telemetry,
    and send out commands based upon the data.
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
        target: Position,
        height_threshold: int,
        yaw_threshold: int,
        z_speed: int,
        turning_speed: float,
    ) -> tuple[bool, "Command"]:
        """
        Falliable create (instantiation) method to create a Command object.
        """
        if connection is None:
            return (False, None)
        instance = cls(
            cls.__private_key,
            connection,
            local_logger,
            target,
            height_threshold,
            yaw_threshold,
            z_speed,
            turning_speed,
        )
        local_logger.info("Command instance created", True)
        return (True, instance)

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
        target: Position,
        height_threshold: int,
        yaw_threshold: int,
        z_speed: int,
        turning_speed: float,
    ) -> None:
        assert key is Command.__private_key, "Use create() method"
        self._master = connection
        self._logger = local_logger
        self._target = target
        self._height_threshold = height_threshold
        self._yaw_threshold = yaw_threshold
        self._z_speed = z_speed
        self._turning_speed = turning_speed
        self._telemetry_count = 0
        self._cumulative_speed = 0.0
        if self._logger is not None:
            self._logger.info("Command initialized", True)

    def run(self, data: telemetry.TelemetryData) -> tuple[str, str]:
        """
        Make a decision based on received telemetry data.
        """

        target_yaw = math.atan2(self._target.y, self._target.x)
        angle_threshold_rad = self._yaw_threshold * math.pi / 180  # Convert to radians
        # Log average velocity for this trip so far
        current_speed = math.sqrt(data.x_velocity**2 + data.y_velocity**2 + data.z_velocity**2)
        self._telemetry_count += 1
        self._cumulative_speed += current_speed
        average_speed = self._cumulative_speed / self._telemetry_count
        self._logger.info(f"Current Average Velocity: {average_speed:.2f} m/s")
        # Use COMMAND_LONG (76) message, assume the target_system=1 and target_componenet=0
        # The appropriate commands to use are instructed below

        # Adjust height using the comand MAV_CMD_CONDITION_CHANGE_ALT (113)
        # String to return to main: "CHANGE_ALTITUDE: {amount you changed it by, delta height in meters}"
        alt_str, yaw_str = "", ""
        if data.z is not None and self._target.z is not None:
            delta_altitude = self._target.z - data.z
            if abs(delta_altitude) > self._height_threshold:
                absolute_target_meters = float(self._target.z)
                self._master.mav.command_long_send(
                    1,
                    0,
                    mavutil.mavlink.MAV_CMD_CONDITION_CHANGE_ALT,
                    0,
                    self._z_speed,
                    0,
                    0,
                    0,
                    0,
                    0,
                    absolute_target_meters,
                )
                alt_str = f"CHANGE_ALTITUDE: {delta_altitude:.2f} meters. "
        current_yaw = data.yaw
        delta_yaw_rad = target_yaw - current_yaw
        if abs(delta_yaw_rad) > angle_threshold_rad:
            # Adjust the yaw using MAV_CMD_CONDITION_YAW (115). Must use relative angle to current state
            delta_yaw_deg = math.degrees(delta_yaw_rad)
            delta_yaw_deg = (delta_yaw_deg + 180) % 360 - 180  # Wrap to [-180, 180]
            direction = 1 if delta_yaw_deg > 0 else -1
            self._master.mav.command_long_send(
                1,
                0,
                mavutil.mavlink.MAV_CMD_CONDITION_YAW,
                0,
                abs(delta_yaw_deg),
                self._turning_speed,
                direction,
                1,
                0,
                0,
                0,
            )
            yaw_str = f"CHANGING_YAW: {delta_yaw_deg:.2f} degrees. "
        return alt_str, yaw_str
        # String to return to main: "CHANGING_YAW: {degree you changed it by in range [-180, 180]}"
        # Positive angle is counter-clockwise as in a right handed system


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
