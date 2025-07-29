import importlib


DEVICE_LIST = ["CPU", "GPU"]
BASED_LINALG = [
    "dot", "tensor", "MatrixTensorI", "MatrixPermutation", "VectorPermutation",
    "multiply", "matrix_dot_vector", "matrix_dot_matrix", "sv_sampling",
    "sv_probability", "sv_sampling_for_all_qubits",
    "partial_sv_sampling_for_all_qubits", "partial_sv_sampling", "array_combination"
]


class LinAlgLoader:
    """
    The Algorithm class with used to load all required algorithm, including based linear algorithm, gate-based matrix
    dot vector algorithm, and algorithms for multi-GPUs.

    Args:
        device(str): one of ["GPU", "CPU"].
        enable_gate_kernel(bool): loading gate-based matrix dot vector algorithm if True.
        enable_multigpu_gate_kernel(bool): loading the required algorithms of multi-GPUs if True.
    """
    def __init__(
        self,
        device: str,
        enable_gate_kernel: bool = False,
        enable_multigpu_gate_kernel: bool = False
    ):
        if device not in DEVICE_LIST:
            raise KeyError(f"Not supported the given device, please choice one of {DEVICE_LIST}")

        linalg_lib = importlib.import_module('QuICT.ops.linalg.cpu_calculator') if device == "CPU" else \
            importlib.import_module('QuICT.ops.linalg.gpu_calculator')
        for attr, value in linalg_lib.__dict__.items():
            if attr in BASED_LINALG:
                self.__dict__[attr] = value

        if enable_gate_kernel:
            gate_lib = importlib.import_module('QuICT.ops.gate_kernel.cpu') if device == "CPU" else \
                importlib.import_module('QuICT.ops.gate_kernel.gpu')
            GATE_KERNEL_FUNCTIONS = gate_lib.__dict__["__outward_functions"]

            for attr, value in gate_lib.__dict__.items():
                if attr in GATE_KERNEL_FUNCTIONS:
                    self.__dict__[attr] = value

        if enable_multigpu_gate_kernel:
            proxy_lib = importlib.import_module('QuICT.ops.gate_kernel.multigpu')
            PROXY_GATE_FUNCTIONS = proxy_lib.__dict__["__outward_functions"]

            for attr, value in proxy_lib.__dict__.items():
                if attr in PROXY_GATE_FUNCTIONS:
                    self.__dict__[attr] = value
