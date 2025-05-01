from robocasa.environments.kitchen.kitchen import *


class StoreFruit(Kitchen):
    """
    Store Fruit: A custom multi-stage task.

    Simulates the task of storing a fruit in a cabinet.

    Steps:
        1. Open the cabinet door.
        2. Pick the fruit from the counter.
        3. Place the fruit inside the cabinet.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):
        """
        Setup the kitchen references for the task:
        The cabinet to place the fruit in and the counter to initialize it on.
        """
        super()._setup_kitchen_references()
        # self.cab = self.register_fixture_ref("cab", dict(id=FixtureType.DOOR_TOP_HINGE_SINGLE))
        # self.cab = self.register_fixture_ref("cab", dict(id=FixtureType.DOOR_TOP_HINGE_DOUBLE))
        left_cabinet_names = [name for name in self.fixtures.keys() if "cab" in name.lower() and hasattr(self.fixtures[name], "orientation") and "left" in self.fixtures[name].orientation.lower()]
        if left_cabinet_names:
            self.cab = self.fixtures[left_cabinet_names[0]]
        else:
            self.cab = self.register_fixture_ref("cab", dict(id=FixtureType.CABINET_TOP))

        self.counter = self.register_fixture_ref("counter", dict(id=FixtureType.COUNTER, ref=self.cab))
        self.init_robot_base_pos = self.cab

    def get_ep_meta(self):
        """
        Get the episode metadata for the task.
        This includes the language description of the task.
        """
        ep_meta = super().get_ep_meta()
        fruit_lang = self.get_obj_lang()
        ep_meta["lang"] = f"open the cabinet, then pick the {fruit_lang} from the counter and place it inside the cabinet"
        return ep_meta

    def _reset_internal(self):
        """
        Resets simulation internal configurations.
        Ensures the cabinet door starts closed.
        """
        super()._reset_internal()
        # Set the cabinet door to be closed initially
        self.cab.set_door_state(min=0.0, max=0.0, env=self, rng=self.rng)

    def _get_obj_cfgs(self):
        """
        Get the object configurations for the task.
        Places a fruit object on the counter.
        """
        cfgs = []
        cfgs.append(
            dict(
                name="obj",
                obj_groups="my_pnp",  # Sample from the 'fruit' group
                graspable=True,
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.cab,  # Place relative to the cabinet
                    ),
                    size=(0.60, 0.40),  # Area on the counter to sample from
                    pos=(0.0, -1.0),  # Place in the front part of the sampling area
                ),
            )
        )

        # Optional: Add distractors on the counter or inside the cabinet
        cfgs.append(
            dict(
                name="distr_counter",
                obj_groups="all",  # Sample any object as distractor
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.cab,
                    ),
                    size=(1.0, 0.30),  # Different area for distractor
                    pos=(0.0, 1.0),  # Place in the back part
                    offset=(0.0, -0.05),
                ),
            )
        )
        cfgs.append(
            dict(
                name="distr_cab",
                obj_groups="all",
                placement=dict(
                    fixture=self.cab,
                    size=(1.0, 0.20),
                    pos=(0.0, 1.0),
                    offset=(0.0, 0.0),
                ),
            )
        )

        return cfgs

    def _check_success(self):
        """
        Check if the task is successful.
        Checks if the fruit is inside the cabinet and the gripper is far from the fruit.
        Implicitly requires the door to have been opened to place the fruit inside.
        """
        fruit_inside_cab = OU.obj_inside_of(self, "obj", self.cab)
        gripper_obj_far = OU.gripper_obj_far(self)

        # Optional: Check if the door is open enough
        door_state = self.cab.get_door_state(env=self)
        door_open = True
        for joint_p in door_state.values():
            if joint_p < 0.5:
                door_open = False
                break
        return fruit_inside_cab and gripper_obj_far and door_open

        return fruit_inside_cab and gripper_obj_far
