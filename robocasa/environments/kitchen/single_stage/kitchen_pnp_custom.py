from robocasa.environments.kitchen.kitchen import *
from robocasa.environments.kitchen.single_stage.kitchen_pnp import PnP
from robocasa.utils import object_utils as OU
from robocasa.models.fixtures import FixtureType


class PnPCabToCounterTomato(PnP):
    """
    Class encapsulating the atomic cabinet to counter pick and place task with tomato

    This is a simplified pick and place task specifically for tomatoes from cabinet to counter.
    It focuses on the core pick-and-place mechanics without the complexity of cooking operations.

    Args:
        cab_id (str): The cabinet fixture id to pick the object from.
        obj_groups (str): Object groups to sample the target object from.
    """

    def __init__(
        self, cab_id=FixtureType.CABINET_TOP, obj_groups="tomato", *args, **kwargs
    ):
        self.cab_id = cab_id
        super().__init__(obj_groups=obj_groups, *args, **kwargs)

    def _setup_kitchen_references(self):
        """
        Setup the kitchen references for the cabinet to counter pick and place task:
        The cabinet to pick tomato from and the counter to place it on
        """
        super()._setup_kitchen_references()

        # Find left cabinet for tomato pickup
        left_cabinet_names = [
            name
            for name in self.fixtures.keys()
            if "cab" in name.lower() and "mid_left" in name.lower()
        ]
        if left_cabinet_names:
            self.cab = self.fixtures[left_cabinet_names[0]]
        else:
            self.cab = self.register_fixture_ref("cab", dict(id=self.cab_id))

        # Setup counter reference for placement
        self.counter = self.register_fixture_ref(
            "counter", dict(id=FixtureType.COUNTER, ref=self.cab)
        )
        self.init_robot_base_pos = self.cab

    def get_ep_meta(self):
        """
        Get the episode metadata for the cabinet to counter tomato pick and place task.
        This includes the language description of the task.
        """
        """
        Get the episode metadata for the cabinet to counter pick and place task.
        This includes the language description of the task.
        """
        ep_meta = super().get_ep_meta()
        # obj_lang = self.get_obj_lang()
        ep_meta[
            "lang"
        ] = f"pick the tomato from the cabinet and place it on the counter"
        return ep_meta

    def _reset_internal(self):
        """
        Resets simulation internal configurations.
        """
        super()._reset_internal()
        self.cab.set_door_state(min=0.95, max=1.0, env=self, rng=self.rng)

    def _get_obj_cfgs(self):
        """
        Get object configurations for tomato pick and place task.
        """
        cfgs = []

        # Add tomato object in cabinet (using cabinet placement format)
        cfgs.append(
            dict(
                name="tomato_1",
                obj_groups="tomato",
                graspable=True,
                placement=dict(
                    fixture=self.cab,  # cabinet fixture
                    size=(0.0, 0.0),  # zero-sized inner region
                    pos=(0.0, 0.0),  # centre of the reset region
                    rotation=(0, 0),  # keep orientation fixed
                    margin=0.0,  # don't shrink the usable area
                ),
            )
        )

        # Add plate for visual reference on counter (using counter placement format)
        cfgs.append(
            dict(
                name="plate",
                obj_groups="plate",
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.cab,
                    ),
                    size=(0.30, 0.30),
                    pos=(0.0, -1.0),
                    offset=(0.0, 0.0),
                ),
            )
        )

        return cfgs

    def _check_success(self):
        """
        Check if the tomato pick and place task is successful.
        Success is defined as the tomato being placed on the counter.
        """
        obj = self.objects["tomato_1"]
        container = self.objects["plate"]

        obj_container_contact = self.check_contact(obj, container)
        gripper_obj_far = OU.gripper_obj_far(self, obj_name="tomato_1")
        return obj_container_contact and gripper_obj_far

    def _check_obj_in_place(self, obj_pos, target_pos, threshold=0.03):
        """
        Helper function to check if an object is in the target position.
        """
        return np.linalg.norm(obj_pos[:2] - target_pos[:2]) < threshold
