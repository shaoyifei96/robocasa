from robocasa.environments.kitchen.kitchen import *


class ManipulateDoor(Kitchen):
    """
    Class encapsulating the atomic manipulate door tasks.

    Args:
        behavior (str): "open" or "close". Used to define the desired
            door manipulation behavior for the task.

        door_id (str): The door fixture id to manipulate.
    """

    def __init__(self, behavior="open", door_id=FixtureType.DOOR_TOP_HINGE, *args, **kwargs):
        self.door_id = door_id
        assert behavior in ["open", "close"]
        self.behavior = behavior
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):
        """
        Setup the kitchen references for the door tasks.
        """
        super()._setup_kitchen_references()
        # self.door_fxtr = self.register_fixture_ref("door_fxtr", dict(id=self.door_id))
        left_cabinet_names = [name for name in self.fixtures.keys() if "cab" in name.lower() and hasattr(self.fixtures[name], "orientation") and "left" in self.fixtures[name].orientation.lower()]
        if left_cabinet_names:
            self.door_fxtr = self.fixtures[left_cabinet_names[0]]
        else:
            raise ValueError("No left cabinet found in the kitchen fixtures.")
        self.init_robot_base_pos = self.door_fxtr

    def get_ep_meta(self):
        """
        Get the episode metadata for the door tasks.
        This includes the language description of the task.

        Returns:
            dict: Episode metadata.
        """
        ep_meta = super().get_ep_meta()
        if isinstance(self.door_fxtr, Microwave):
            door_fxtr_name = "microwave"
            door_name = "door"
        elif isinstance(self.door_fxtr, SingleCabinet):
            door_fxtr_name = "cabinet"
            door_name = "door"
        elif isinstance(self.door_fxtr, HingeCabinet):
            door_fxtr_name = "cabinet"
            door_name = "doors"
        elif isinstance(self.door_fxtr, Drawer):
            door_fxtr_name = "drawer"
            door_name = "doors"
        ep_meta["lang"] = f"{self.behavior} the {door_fxtr_name} {door_name}"
        return ep_meta

    def _reset_internal(self):
        """
        Reset the environment internal state for the door tasks.
        This includes setting the door state based on the behavior.
        """
        if self.behavior == "open":
            self.door_fxtr.set_door_state(min=0.0, max=0.0, env=self, rng=self.rng)
        elif self.behavior == "close":
            self.door_fxtr.set_door_state(min=0.90, max=1.0, env=self, rng=self.rng)
        # set the door state then place the objects otherwise objects initialized in opened drawer will fall down before the drawer is opened
        super()._reset_internal()

    def _setup_references(self):
        """
        Sets up references to important components. A reference is typically an
        index or a list of indices that point to the corresponding elements
        in a flatten array, which is how MuJoCo stores physical simulation data.
        """
        super()._setup_references()

        # Get the address for the door hinge joint
        self.hinge_qpos_addr = self.sim.model.get_joint_qpos_addr(self.door_fxtr.joints[0])
        self.gripper_qpos_joint1_addr = self.sim.model.get_joint_qpos_addr(self.robots[0].gripper_joints["right"][0])
        self.gripper_qpos_joint2_addr = self.sim.model.get_joint_qpos_addr(self.robots[0].gripper_joints["right"][1])

    # def _setup_observables(self):
    #     """
    #     Sets up observables to be used for this environment. Add door angle to the observables

    #     Returns:
    #         OrderedDict: Dictionary mapping observable names to its corresponding Observable object
    #     """
    #     observables = super()._setup_observables()

    #     @sensor(modality="object")
    #     def cabinet_pos_quat(obs_cache):
    #         # Get cabinet position and orientation
    #         cab_body = f"{self.door_fxtr.name}_{self.door_fxtr._bodies[0]}"
    #         cab_pos = self.sim.data.get_body_xpos(cab_body)
    #         cab_quat = self.sim.data.get_body_xquat(cab_body)
    #         cab_quat = T.convert_quat(cab_quat)
    #         return np.array(cab_pos.tolist() + cab_quat.tolist())

    #     observables["cabinet_pos_quat"] = Observable(
    #         name="cabinet_pos_quat",
    #         sensor=cabinet_pos_quat,
    #         sampling_rate=self.control_freq,
    #         active=True,
    #     )

    #     @sensor(modality="object")
    #     def bottom_pos_quat(obs_cache):
    #         # Return cabinet bottom surface position and orientation
    #         bottom_geom_name = self.door_fxtr.visual_geoms[1]
    #         bottom_pos = self.sim.data.get_geom_xpos(bottom_geom_name)
    #         bottom_mat = self.sim.data.get_geom_xmat(bottom_geom_name)
    #         bottom_quat = T.mat2quat(bottom_mat.reshape(3, 3))
    #         return np.array(bottom_pos.tolist() + bottom_quat.tolist())

    #     observables["bottom_pos_quat"] = Observable(
    #         name="bottom_pos_quat",
    #         sensor=bottom_pos_quat,
    #         sampling_rate=self.control_freq,
    #         active=True,
    #     )

    #     # @sensor(modality="object")
    #     # def door_pos_quat(obs_cache):
    #     #     # Get door position and orientation
    #     #     door_body = f"{self.door_fxtr.name}_{self.door_fxtr._bodies[1]}"
    #     #     door_pos = self.sim.data.get_body_xpos(door_body)
    #     #     door_quat = self.sim.data.get_body_xquat(door_body)
    #     #     door_quat = T.convert_quat(door_quat)
    #     #     return np.array(door_pos.tolist() + door_quat.tolist())

    #     # observables["door_pos_quat"] = Observable(
    #     #     name="door_pos_quat",
    #     #     sensor=door_pos_quat,
    #     #     sampling_rate=self.control_freq,
    #     #     active=True,
    #     # )

    #     @sensor(modality="object")
    #     def handle_pos_quat(obs_cache):
    #         # Return handle position and orientation
    #         if (
    #             isinstance(self.door_fxtr, SingleCabinet)
    #             or isinstance(self.door_fxtr, Drawer)
    #             or isinstance(self.door_fxtr, Microwave)
    #         ):
    #             handle_name = self.door_fxtr.handle_name
    #         elif isinstance(self.door_fxtr, HingeCabinet):
    #             # For double doors, you might need to choose which handle
    #             handle_name = self.door_fxtr.left_handle_name
    #         else:
    #             # For other fixture types, try to find a handle site
    #             handle_name = f"{self.door_fxtr.name}_door_handle_handle"
    #         handle_geom_id = self.sim.model.geom_name2id(handle_name)
    #         handle_pos = self.sim.data.geom_xpos[handle_geom_id]
    #         handle_quat = self.sim.data.geom_xmat[handle_geom_id].reshape(3, 3)
    #         handle_quat = T.mat2quat(handle_quat)
    #         return np.array(handle_pos.tolist() + handle_quat.tolist())

    #     observables["handle_pos_quat"] = Observable(
    #         name="handle_pos_quat",
    #         sensor=handle_pos_quat,
    #         sampling_rate=self.control_freq,
    #         active=True,
    #     )

    #     return observables

    def _check_success(self):
        """
        Check if the door manipulation task is successful.

        Returns:
            bool: True if the task is successful, False otherwise.
        """
        door_state = self.door_fxtr.get_door_state(env=self)

        success = True
        for joint_p in door_state.values():
            if self.behavior == "open":
                if joint_p < 0.90:
                    success = False
                    break
            elif self.behavior == "close":
                if joint_p > 0.05:
                    success = False
                    break

        return success

    def _get_obj_cfgs(self):
        """
        Get the object configurations for the door tasks. This includes the object placement configurations.
        Place one object inside the door fixture and 1-4 distractors on the counter.
        """
        cfgs = []

        cfgs.append(
            dict(
                name="door",
                obj_groups="all",
                graspable=True,
                microwavable=(True if isinstance(self.door_fxtr, Microwave) else None),
                placement=dict(
                    fixture=self.door_fxtr,
                    size=(0.30, 0.30),
                    pos=(None, -1.0),
                ),
            )
        )

        # distractors
        num_distr = self.rng.integers(1, 4)
        for i in range(num_distr):
            cfgs.append(
                dict(
                    name=f"distr_counter_{i+1}",
                    obj_groups="all",
                    placement=dict(
                        fixture=self.get_fixture(FixtureType.COUNTER, ref=self.door_fxtr),
                        sample_region_kwargs=dict(
                            ref=self.door_fxtr,
                        ),
                        size=(1.0, 0.50),
                        pos=(None, -1.0),
                        offset=(0.0, 0.10),
                    ),
                )
            )

        return cfgs


class OpenDoor(ManipulateDoor):
    def __init__(self, *args, **kwargs):
        super().__init__(behavior="open", *args, **kwargs)


class OpenSingleDoor(OpenDoor):
    def __init__(self, door_id=FixtureType.DOOR_TOP_HINGE_SINGLE, *args, **kwargs):
        super().__init__(door_id=door_id, *args, **kwargs)


class OpenDoubleDoor(OpenDoor):
    def __init__(self, door_id=FixtureType.DOOR_TOP_HINGE_DOUBLE, *args, **kwargs):
        super().__init__(door_id=door_id, *args, **kwargs)


class CloseDoor(ManipulateDoor):
    def __init__(self, behavior=None, *args, **kwargs):
        super().__init__(behavior="close", *args, **kwargs)


class CloseSingleDoor(CloseDoor):
    def __init__(self, door_id=FixtureType.DOOR_TOP_HINGE_SINGLE, *args, **kwargs):
        super().__init__(door_id=door_id, *args, **kwargs)


class CloseDoubleDoor(CloseDoor):
    def __init__(self, door_id=FixtureType.DOOR_TOP_HINGE_DOUBLE, *args, **kwargs):
        super().__init__(door_id=door_id, *args, **kwargs)
