"""
Heartbeat worker that sends heartbeats periodically.
"""

import os
import pathlib
import time

from pymavlink import mavutil

from utilities.workers import worker_controller
from . import heartbeat_sender
from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
def heartbeat_sender_worker(
    connection: mavutil.mavfile, controller: worker_controller.WorkerController
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

    result, local_logger = logger.Logger.create(f"{worker_name}_{process_id}", True)
    # Get Pylance to stop complaining
    assert local_logger is not None

    local_logger.info("Logger initialized", True)
    if not result:
        print("ERROR: Worker failed to create logger")
        return

    # =============================================================================================
    #                          ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
    # =============================================================================================
    # Instantiate class object (heartbeat_sender.HeartbeatSender)
    local_logger.info("Creating HeartbeatSender instance", True)
    _, heartbeat_sender_instance = heartbeat_sender.HeartbeatSender.create(connection, local_logger)
    if heartbeat_sender_instance is None:
        local_logger.error("Failed to create HeartbeatSender instance")
        return
    # Main loop: do work.
    while not controller.is_exit_requested():
        controller.check_pause()
        heartbeat_sender_instance.run()
        time.sleep(1)


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
