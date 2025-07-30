import os
import numpy as np

from QuICT.core import Circuit
from QuICT.tools.interface import OPENQASMInterface


def check_template():
    save_path = os.path.dirname(__file__)

    file_list = os.listdir(save_path)
    file_list.sort()

    i = 0
    for qasm in file_list[3:]:
        circ: Circuit = OPENQASMInterface.load_file(save_path + '/' + qasm).circuit
        if circ.width() > 12:
            print(f'WARNING: {qasm} too large, skipped.')

        width, size, depth = circ.width(), circ.size(), circ.depth()
        gtype = []
        for g in circ.gates:
            if g.type.name not in gtype:
                gtype.append(g.type.name)

        t_str = '_'.join(gtype)
        file_name = f"w{width}_s{size}_d{depth}_{i}_{t_str}.qasm"
        print(file_name)

        assert np.allclose(circ.matrix(), np.identity(1 << circ.width())), \
            f'ERROR: {qasm} is not identity!'

        circ.qasm(os.path.join(save_path, "temp", file_name))
        i += 1

    print('INFO: check finished.')


if __name__ == '__main__':
    check_template()
