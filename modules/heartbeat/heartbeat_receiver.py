"""
Heartbeat receiving logic.
"""

from pymavlink import mavutil
from utilities.workers import queue_proxy_wrapper

from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class HeartbeatReceiver:
    """
    HeartbeatReceiver class to receive heartbeats
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
        disconnect_threshold: int,
        queue: queue_proxy_wrapper.QueueProxyWrapper,
    ) -> tuple[bool, "HeartbeatReceiver"]:
        """
        Falliable create (instantiation) method to create a HeartbeatReceiver object.
        """
        if connection is None:
            return (False, None)
        instance = cls(cls.__private_key, connection, local_logger, disconnect_threshold, queue)
        local_logger.info("HeartbeatReceiver instance created", True)
        return (True, instance)

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
        heartbeat_limit: int = 5,
        queue: queue_proxy_wrapper.QueueProxyWrapper = None,
    ) -> None:
        assert key is HeartbeatReceiver.__private_key, "Use create() method"
        self._master = connection
        self._local_logger = local_logger
        self._connection_status = True  # Assume connection is good at start
        self._missed_heartbeats = 0
        self._missed_heartbeats_limit = heartbeat_limit
        self._queue = queue
        if self._local_logger is not None:
            self._local_logger.info("HeartbeatReceiver initialized", True)

    def run(self) -> None:
        """
        Attempt to recieve a heartbeat message.
        If disconnected for over a threshold number of periods,
        the connection is considered disconnected.
        """
        msg = self._master.recv_match(type="HEARTBEAT", blocking=False)
        if not msg:
            self._missed_heartbeats += 1
            if self._queue is not None:
                self._queue.queue.put(f"Missed heartbeat #{self._missed_heartbeats}")
            if self._missed_heartbeats == self._missed_heartbeats_limit:
                self._connection_status = False
                if self._queue is not None:
                    self._queue.queue.put(
                        f"Connection lost due to {self._missed_heartbeats} missed heartbeats"
                    )
        else:
            if not self._connection_status:
                if self._queue is not None:
                    self._queue.queue.put("Connection re-established after being lost")
            self._connection_status = True
            self._missed_heartbeats = 0
            if self._queue is not None:
                self._queue.queue.put("Heartbeat received and connection is good")


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
