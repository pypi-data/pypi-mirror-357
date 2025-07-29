from sitl.simulator import L2F
from sitl.gamepad import Gamepad
import asyncio
import os
import time
import argparse


async def main():
    args = argparse.ArgumentParser(description="Run the L2F simulator with a gamepad.")
    args.add_argument("gamepad_mapping", type=str, help="Path to the gamepad mapping JSON file.")
    args = args.parse_args()
    time.sleep(1)
    simulator = L2F()
    gamepad = Gamepad(args.gamepad_mapping, simulator.set_rc_channels)

    await asyncio.gather(simulator.run(), gamepad.run())
def sync_main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())


if __name__ == "__main__":
    sync_main()