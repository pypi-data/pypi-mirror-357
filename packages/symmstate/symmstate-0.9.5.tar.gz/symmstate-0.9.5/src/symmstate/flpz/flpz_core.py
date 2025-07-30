from symmstate._symm_state_core import SymmStateCore
import os


class FlpzCore(SymmStateCore):
    """
    The base class to the Flpz subprogram
    """

    def __init__(
        self,
        name: str = "catio3",
        num_datapoints: int = "10",
        abi_file: str = "abifile.abi",
        min_amp: int = 0,
        max_amp: int = 0.5,
    ):
        """
        Stores the attributes of the original input file
        """

        # Validate and assign the other parameters
        if not isinstance(min_amp, float) or not isinstance(max_amp, float):
            raise ValueError("min_amp and max_amp should be floats.")

        if not isinstance(num_datapoints, int) or num_datapoints <= 0:
            raise ValueError("num_datapoints should be a positive integer.")

        if not os.path.isfile(abi_file):
            raise FileNotFoundError("An Abinit file was not detected!")

        self.name = str(name)
        self.num_datapoints = int(num_datapoints)
        self.abi_file = str(abi_file)
        self.min_amp = float(min_amp)
        self.max_amp = float(max_amp)

    def update_abinit_file(self, new_file):
        self.abi_file = self.get_new_file_path(self.abi_file, new_file)
