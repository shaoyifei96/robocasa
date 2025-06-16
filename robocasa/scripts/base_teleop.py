"""
A simple script for keyboard-based base movement control.
"""

import argparse
import time
from robosuite.controllers import load_composite_controller_config
from robosuite.wrappers import VisualizationWrapper
import robosuite
from robosuite.devices import Keyboard
import robocasa.macros as macros


def collect_base_movement(env, device, render=True, max_fr=None):
    """
    Use keyboard to control base movement.
    """
    env.reset()

    if render:
        env.render()

    device.start_control()

    while True:
        start = time.time()

        # Get the newest action
        input_ac_dict = device.input2action(mirror_actions=True)

        # If action is none, then this is a reset so we should break
        if input_ac_dict is None:
            break

        # Create action vector for base movement
        action = env.robots[0].create_action_vector(input_ac_dict)

        # Run environment step
        obs, _, _, _ = env.step(action)

        if render:
            env.render()

        # limit frame rate if necessary
        if max_fr is not None:
            elapsed = time.time() - start
            diff = 1 / max_fr - elapsed
            if diff > 0:
                time.sleep(diff)


if __name__ == "__main__":
    # Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--robot", type=str, default="PandaOmron", help="Which robot to use"
    )
    parser.add_argument(
        "--renderer", type=str, default="mjviewer", choices=["mjviewer", "mujoco"]
    )
    parser.add_argument(
        "--max_fr", default=30, type=int, help="If specified, limit the frame rate"
    )
    args = parser.parse_args()

    # Create argument configuration
    config = {
        "env_name": "Kitchen",  # Using Kitchen as base environment
        "robots": args.robot,
        "controller_configs": load_composite_controller_config(robot=args.robot),
        "translucent_robot": True,
    }

    print("Initializing environment...")
    env = robosuite.make(
        **config,
        has_renderer=True,
        has_offscreen_renderer=False,
        render_camera="robot0_frontview",
        ignore_done=True,
        use_camera_obs=False,
        control_freq=20,
        renderer=args.renderer,
    )

    # Wrap this with visualization wrapper
    env = VisualizationWrapper(env)

    # Initialize keyboard device
    device = Keyboard(
        env=env,
        pos_sensitivity=4.0,
        rot_sensitivity=4.0,
    )

    # Collect base movements
    while True:
        collect_base_movement(
            env,
            device,
            render=(args.renderer != "mjviewer"),
            max_fr=args.max_fr,
        )
        print("\nPress Enter to continue or Ctrl+C to exit...")
        try:
            input()
        except KeyboardInterrupt:
            break
