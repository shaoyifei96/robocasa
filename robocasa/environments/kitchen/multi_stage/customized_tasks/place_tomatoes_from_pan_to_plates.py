from robocasa.environments.kitchen.kitchen import *


class PlaceTomatoesFromPanToPlates(Kitchen):
    """
    Place Tomatoes From Pan To Plates.

    Steps:
        1. Start with two tomatoes in a pan that is on and heating (stove on).
        2. Two empty plates are on the counter near the stove.
        3. Goal: one tomato on each plate and stove turned off.
    """

    def __init__(self, knob_id="random", *args, **kwargs):
        self.knob_id = knob_id
        super().__init__(*args, **kwargs)

    def _setup_kitchen_references(self):
        super()._setup_kitchen_references()

        # Stove and counter
        self.stove = self.register_fixture_ref("stove", dict(id=FixtureType.STOVE))
        self.counter = self.register_fixture_ref(
            "counter", dict(id=FixtureType.COUNTER, ref=self.stove, size=(0.30, 0.40))
        )

        # Determine which burner / knob we care about
        if "task_refs" in self._ep_meta:
            self.knob = self._ep_meta["task_refs"]["knob"]
        else:
            valid_knobs = [k for k, v in self.stove.knob_joints.items() if v is not None]
            if self.knob_id == "random":
                self.knob = self.rng.choice(valid_knobs)
            else:
                assert self.knob_id in valid_knobs
                self.knob = self.knob_id

        self.init_robot_base_pos = self.stove

    def get_ep_meta(self):
        ep_meta = super().get_ep_meta()
        ep_meta["lang"] = (
            f"move each tomato from the pan onto separate plates and turn off the {self.knob.replace('_', ' ')} burner"
        )
        return ep_meta

    def _reset_internal(self):
        super()._reset_internal()
        # Turn the specified knob ON at the beginning
        self.stove.set_knob_state(env=self, rng=self.rng, knob=self.knob, mode="on")

    def _get_obj_cfgs(self):
        cfgs = []

        # Pan on stove (already containing tomatoes)
        cfgs.append(
            dict(
                name="pan",
                obj_groups="pan",
                placement=dict(
                    fixture=self.stove,
                    ensure_object_boundary_in_range=False,
                    size=(0.02, 0.02),
                ),
            )
        )

        # Tomatoes inside pan
        for i in range(2):
            cfgs.append(
                dict(
                    name=f"tomato{i+1}",
                    obj_groups="tomato",
                    graspable=True,
                    placement=dict(
                        fixture=self.stove,
                        ensure_object_boundary_in_range=False,
                        ensure_valid_placement=False,
                        size=(0.02, 0.02),
                        # they will fall into pan after settle
                    ),
                )
            )

        # Two plates on counter
        for i in range(2):
            cfgs.append(
                dict(
                    name=f"plate{i+1}",
                    obj_groups="plate",
                    placement=dict(
                        fixture=self.counter,
                        ensure_object_boundary_in_range=False,
                        ensure_valid_placement=False,
                        size=(0.25, 0.25),
                        pos=((-0.5 if i == 0 else 0.5), -1.0),
                    ),
                )
            )
        return cfgs

    def _check_success(self):
        # tomato-plate pairing (order agnostic)
        t1_p1 = OU.check_obj_in_receptacle(self, "tomato1", "plate1")
        t1_p2 = OU.check_obj_in_receptacle(self, "tomato1", "plate2")
        t2_p1 = OU.check_obj_in_receptacle(self, "tomato2", "plate1")
        t2_p2 = OU.check_obj_in_receptacle(self, "tomato2", "plate2")

        tomatoes_on_plates = (t1_p1 and t2_p2) or (t1_p2 and t2_p1)

        # Stove off condition
        knob_angle = self.stove.get_knobs_state(env=self)[self.knob]
        stove_off = knob_angle < 0.05 or knob_angle > 2 * np.pi - 0.05

        gripper_far = OU.gripper_obj_far(self)
        return tomatoes_on_plates and stove_off and gripper_far 