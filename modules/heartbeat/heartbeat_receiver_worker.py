"""
Heartbeat worker that sends heartbeats periodically.
"""

import os
import pathlib
import time

from pymavlink import mavutil

from utilities.workers import queue_proxy_wrapper
from utilities.workers import worker_controller
from . import heartbeat_receiver
from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
def heartbeat_receiver_worker(
    connection: mavutil.mavfile,
    controller: worker_controller.WorkerController,
    queue: queue_proxy_wrapper.QueueProxyWrapper,
    disconnect_threshold: int = 5
) -> None:
    """
    Worker process.

    args... describe what the arguments are
    """
    # =============================================================================================
    #                          ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
    # =============================================================================================

    # Instantiate logger
    worker_name = pathlib.Path(__file__).stem
    process_id = os.getpid()
    _, local_logger = logger.Logger.create(f"{worker_name}_{process_id}", True)
    # Get Pylance to stop complaining
    assert local_logger is not None

    local_logger.info("Logger initialized for Heartbeat Receiver", True)

    # =============================================================================================
    #                          ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
    # =============================================================================================
    # Instantiate class object (heartbeat_receiver.HeartbeatReceiver)
    local_logger.info("Creating HeartbeatReceiver instance", True)
    result, heartbeat_receiver_instance = heartbeat_receiver.HeartbeatReceiver.create(connection, local_logger, disconnect_threshold, queue)
    if heartbeat_receiver_instance is None:
        local_logger.error("Failed to create HeartbeatReceiver instance")
        return
    while not controller.is_exit_requested():
        controller.check_pause()
        heartbeat_receiver_instance.run()
        # Sleep for a bit to avoid busy waiting. Adjust as necessary.
        time.sleep(1)
# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
