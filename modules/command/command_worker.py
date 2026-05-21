"""
Command worker to make decisions based on Telemetry Data.
"""

import os
import pathlib

from pymavlink import mavutil
import time
from utilities.workers import queue_proxy_wrapper
from utilities.workers import worker_controller
from . import command
from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
def command_worker(
    connection: mavutil.mavfile,
    target: command.Position,
    controller: worker_controller.WorkerController,
    input_queue: queue_proxy_wrapper.QueueProxyWrapper,
    output_queue: queue_proxy_wrapper.QueueProxyWrapper,
    height_threshold: int,
    yaw_threshold: int,
    z_speed: int,
    turning_speed: float,
    telemetry_period: float
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
    if not result:
        print("ERROR: Worker failed to create logger")
        return

    # Get Pylance to stop complaining
    assert local_logger is not None

    local_logger.info("Logger initialized", True)

    # =============================================================================================
    #                          ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
    # =============================================================================================
    # Instantiate class object (command.Command)
    _, command_instance = command.Command.create(
        connection, local_logger, target, height_threshold, yaw_threshold, z_speed, turning_speed
    )
    # Main loop: do work.
    while not controller.is_exit_requested():
        controller.check_pause()
        if input_queue is not None and input_queue.queue.qsize() > 0:
            data = input_queue.queue.get()
            local_logger.info(f"Received telemetry data: {data}", True)
            alt_str, yaw_str = command_instance.run(data)
            local_logger.info(f"Command run produced: alt_str: {alt_str}, yaw_str: {yaw_str}", True)
            output_queue.queue.put((alt_str, yaw_str))
            time.sleep(telemetry_period)


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
