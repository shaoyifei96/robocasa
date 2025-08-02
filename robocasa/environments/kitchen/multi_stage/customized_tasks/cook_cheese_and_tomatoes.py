from robocasa.environments.kitchen.kitchen import *


class CookCheeseAndTomatoes(Kitchen):
    """
    Cook Cheese and Tomatoes: A custom multi-stage task.

    Steps:
        1. Open the first cabinet and pick the tomato.
        2. Open the second cabinet and pick the cheese.
        3. Place both tomato and cheese in a pan on the stovetop and cook them.
        4. Pick the cooked items and place them onto the plate on the counter.
    """

    def __init__(self, knob_id="random", behavior="turn_on", *args, **kwargs):
        assert behavior in ["turn_on", "turn_off"]
        self.behavior = behavior
        self.knob_id = knob_id
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):
        """Setup fixtures used in this task"""
        super()._setup_kitchen_references()

        # Register two distinct cabinets
        # if "cabinet_1" in self.fixture_refs:
        #     # If episode meta already has refs (e.g., loading from dataset), reuse them
        #     self.cabinet_1 = self.fixture_refs["cabinet_1"]
        #     # self.cabinet_2 = self.fixture_refs["cabinet_2"]
        #     # self.cabinet_3 = self.fixture_refs["cabinet_3"]
        #     self.counter = self.fixture_refs["counter"]
        #     self.stove = self.fixture_refs["stove"]
        if True:
            for fxtr in self.fixtures.values():
                if "cab" in fxtr.name and "main_group" in fxtr.name:
                    print(fxtr.name)
                if fxtr.name == "cab_mid_left_main_group":
                    self.cabinet_1 = fxtr
                # elif fxtr.name == "cab_mid_right_main_group":
                #     self.cabinet_2 = fxtr
                # elif fxtr.name == "":
                #     self.cabinet_3 = fxtr
            self.fixture_refs["cabinet_1"] = self.cabinet_1
            # self.fixture_refs["cabinet_2"] = self.cabinet_2
            # self.fixture_refs["cabinet_3"] = self.cabinet_3
            self.stove = self.get_fixture(FixtureType.STOVE)
            if "task_refs" in self._ep_meta:
                self.knob = self._ep_meta["task_refs"]["knob"]
                self.cookware_burner = self._ep_meta["task_refs"]["cookware_burner"]
            else:
                valid_knobs = [
                    k for (k, v) in self.stove.knob_joints.items() if v is not None
                ]
                if self.knob_id == "random":
                    self.knob = self.rng.choice(list(valid_knobs))
                else:
                    assert self.knob_id in valid_knobs
                    self.knob = self.knob
                self.cookware_burner = (
                    self.knob
                    if self.rng.uniform() <= 0.50
                    else self.rng.choice(valid_knobs)
                )
                self.counter = self.register_fixture_ref(
                    "counter",
                    dict(id=FixtureType.COUNTER, ref=self.stove, size=(0.30, 0.40)),
                )

        # Initial robot base location
        self.init_robot_base_pos = self.cabinet_1

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        ep_meta[
            "lang"
        ] = "Open the two cabinets, pick the tomato and cheese, place them in the pan, and turn on the stove."
        return ep_meta

    def _reset_internal(self):
        """Ensure cabinet doors start closed."""
        super()._reset_internal()
        self.cabinet_1.set_door_state(min=0.0, max=0.0, env=self, rng=self.rng)
        # self.cabinet_2.set_door_state(min=0.0, max=0.0, env=self, rng=self.rng)
        # self.cabinet_3.set_door_state(min=0.0, max=0.0, env=self, rng=self.rng)

    def _get_obj_cfgs(self):
        cfgs = []

        # Pan on stove
        cfgs.append(
            dict(
                name="pan",
                obj_groups="pan",
                placement=dict(
                    fixture=self.stove,
                    ensure_object_boundary_in_range=False,
                    size=(0.02, 0.02),
                    pos=(0.0, 0.0),
                    rotation=(-1, -0.5),
                ),
            )
        )

        # Plate on counter
        cfgs.append(
            dict(
                name="plate",
                obj_groups="plate",
                graspable=False,
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(ref=self.cabinet_1),
                    size=(0.3, 0.3),  # Smaller, more specific region
                    pos=("ref", -1.0),  # Position directly under cabinet
                    rotation=(-0.3, 0.3),
                    # margin=0.0,                           # Smaller margin for precision
                ),
            )
        )

        # Tomato in first cabinet – place at exact centre of the bottom
        cfgs.append(
            dict(
                name="tomato_1",
                obj_groups="tomato",
                graspable=True,
                placement=dict(
                    fixture=self.cabinet_1,  # cabinet fixture
                    size=(0.0, 0.0),  # zero-sized inner region
                    pos=(0.0, 0.0),  # centre of the reset region
                    rotation=(-0.3, 0.3),  # (optional) keep orientation fixed
                    margin=0.0,  # (optional) don’t shrink the usable area
                ),
            )
        )
        # cfgs.append(
        #     dict(
        #         name="tomato_2",
        #         obj_groups="tomato",
        #         graspable=True,
        #         placement=dict(
        #             fixture=self.cabinet_1,      # cabinet fixture
        #             size=(0.0, 0.0),         # zero-sized inner region
        #             pos=(0.2, 0.0),          # centre of the reset region
        #             rotation=(0, 0),         # (optional) keep orientation fixed
        #             margin=0.0,              # (optional) don’t shrink the usable area
        #         ),
        #     )
        # )

        # Door of first cabinet
        # cfgs.append(
        #     dict(
        #         name="door_1",
        #         obj_groups="all",
        #         graspable=True,
        #         microwavable=False,
        #         placement=dict(
        #             fixture=self.cabinet_1,
        #             size=(0.30, 0.30),
        #             pos=(None, -1.0),
        #         ),
        #     )
        # )

        # Cheese in second cabinet – same idea
        # cfgs.append(
        #     dict(
        #         name="cheese",
        #         obj_groups="cheese",
        #         graspable=True,
        #         placement=dict(
        #             fixture=self.cabinet_2,
        #             size=(0.0, 0.0),
        #             pos=(0.0, 0.0),
        #             rotation=(0, 0),
        #             margin=0.0,
        #         ),
        #     )
        # )

        # cfgs.append(
        #     dict(
        #         name="cheese",
        #         obj_groups="cheese",
        #         graspable=True,
        #         placement=dict(
        #             fixture=self.cabinet_3,
        #             size=(0.0, 0.0),
        #             pos=(0.0, 0.0),
        #             rotation=(0, 0),
        #             margin=0.0,
        #         ),
        #     )
        # )

        # Door of second cabinet
        # cfgs.append(
        #     dict(
        #         name="door_2",
        #         obj_groups="all",
        #         graspable=True,
        #         microwavable=False,
        #         placement=dict(
        #             fixture=self.cabinet_2,
        #             size=(0.30, 0.30),
        #             pos=(None, -1.0),
        #         ),
        #     )
        # )

        return cfgs

    def _check_success(self):
        tomato_on_plate = OU.check_obj_in_receptacle(self, "tomato_1", "plate")
        # tomato_on_plate = OU.check_obj_in_receptacle(self, "tomato_2", "plate")
        # cheese_on_plate = OU.check_obj_in_receptacle(self, "cheese", "plate")
        gripper_far = OU.gripper_obj_far(self, "tomato_1")
        return tomato_on_plate and gripper_far  # and cheese_on_plate #and gripper_far
