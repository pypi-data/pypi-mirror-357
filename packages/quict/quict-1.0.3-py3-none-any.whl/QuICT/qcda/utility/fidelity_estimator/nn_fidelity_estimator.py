import os.path
import pickle as pkl
from typing import List

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import StandardScaler

from QuICT.core import Circuit
from QuICT.core.gate import BasicGate
from QuICT.core.utils import GateType
from QuICT.core.virtual_machine import VirtualQuantumMachine


class ShallowFidelityNN(nn.Module):
    """
    A simple NN for quantum circuit fidelity estimation.
    """

    def __init__(self, input_size, hidden_size):
        """
        Args:
            input_size(int): input size of NN
            hidden_size(int): hidden size of NN
        """

        output_size = 1
        super(ShallowFidelityNN, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.relu2 = nn.ReLU()
        self.fc3 = nn.Linear(hidden_size, hidden_size)
        self.relu3 = nn.ReLU()
        self.fc4 = nn.Linear(hidden_size, output_size)
        self.tanh = nn.Tanh()

    def forward(self, x):
        """
        Args:
            x(torch.Tensor): input tensor

        Returns:
            torch.Tensor: output tensor
        """

        x = self.fc1(x)
        x = self.relu2(x)
        x = self.fc2(x)
        x = self.relu2(x)
        x = self.fc3(x)
        x = self.relu3(x)
        x = self.fc4(x)
        x = self.tanh(x)
        return x


class NNFidelityEstimator:
    """
    NN based fidelity estimator.
    """

    # built-in supported machines
    SUPPORTED_MACHINE = [
        'ibm_geneva',
        'ibm_hanoi',
        'ibm_montreal',
        'ibm_mumbai',
        'ibm_toronto',
        'original_KF_C6_130'
    ]

    def __init__(self, vqm: VirtualQuantumMachine, hidden_size=200, use_vqm=False):
        """
        Args:
            vqm(VirtualQuantumMachine): target machine
            hidden_size(int): hidden size of NN
            use_vqm(bool): whether to use vqm information when estimating
        """

        self.vqm = vqm
        self.hidden_size = hidden_size
        self.use_vqm = use_vqm
        self.scaler = StandardScaler()

        feature = self._compute_features(Circuit(vqm.qubit_number), vqm)
        self.model = ShallowFidelityNN(len(feature), hidden_size)

    @classmethod
    def from_target_machine(cls, target_machine):
        """
        Load default fidelity estimator from given target_machine.
        See NNFidelityEstimator.SUPPORTED_MACHINE for supported machines.

        Args:
            target_machine(str): target machine

        Returns:
            NNFidelityEstimator: fidelity estimator
        """

        if target_machine not in cls.SUPPORTED_MACHINE:
            raise ValueError(f'Unsupported machine: {target_machine}')

        dir_path = os.path.join(os.path.dirname(__file__), 'models', f'{target_machine}')
        return cls.load(dir_path)

    @classmethod
    def load(cls, path):
        """
        Load a fidelity estimator from a given path.

        Args:
            path(str): path to the estimator

        Returns:
            NNFidelityEstimator: fidelity estimator
        """

        scaler = pkl.load(open(os.path.join(path, 'scaler.pkl'), 'rb'))
        params = pkl.load(open(os.path.join(path, 'params.pkl'), 'rb'))

        fe = cls(*params)
        fe.scaler = scaler
        fe.model.load_state_dict(torch.load(os.path.join(path, 'model.pt')))
        fe.model.eval()
        return fe

    def save(self, path):
        """
        Save the fidelity estimator to a given path.

        Args:
            path(str): path to save the estimator
        """

        if not os.path.exists(path):
            os.makedirs(path)
        torch.save(self.model.state_dict(), os.path.join(path, 'model.pt'))
        pkl.dump(self.scaler, open(os.path.join(path, 'scaler.pkl'), 'wb'))
        params = (self.vqm, self.hidden_size, self.use_vqm)
        pkl.dump(params, open(os.path.join(path, 'params.pkl'), 'wb'))

    def _vqm_feature(self, vqm: VirtualQuantumMachine, gt_dict):
        """
        Compute the feature of a given vqm. The feature includes:
            1. single qubit gate fidelity
            2. two qubit gate fidelity (coupling strength)
            3. qubit readout fidelity
            4. qubit t1 and t2 times

        Args:
            vqm(VirtualQuantumMachine): given vqm
            gt_dict(dict): gate type dict

        Returns:
            list: feature vector
        """

        feature = []
        for q in range(vqm.qubit_number):
            if isinstance(vqm.gate_fidelity[q], float):
                feature.extend([vqm.gate_fidelity[q]] * len(vqm.instruction_set.one_qubit_gates))
            else:
                gate_fidelity = sorted(vqm.gate_fidelity[q].items(), key=lambda x: gt_dict[x[0]])
                feature.extend([x[1] for x in gate_fidelity])

        double_gate_fidelity = {}
        for q1 in vqm.double_gate_fidelity:
            for q2 in vqm.double_gate_fidelity[q1]:
                double_gate_fidelity[(q1, q2)] = vqm.double_gate_fidelity[q1][q2]

        double_gate_fidelity = sorted(double_gate_fidelity.items(), key=lambda x: x[0])
        feature.extend([x[1] for x in double_gate_fidelity])

        for q in range(vqm.qubit_number):
            if isinstance(vqm.qubit_fidelity[q], float):
                feature.extend([vqm.qubit_fidelity[q], vqm.qubit_fidelity[q]])
            else:
                feature.extend(list(vqm.qubit_fidelity[q]))

        feature.extend(vqm.t1_times)
        feature.extend(vqm.t2_times)
        return feature

    def _compute_features(self, circ: Circuit, vqm: VirtualQuantumMachine, mapping: List[int] = None):
        """
        Compute the feature of a given circuit and vqm. The feature includes:
            1. vqm features
            2. gate count of each type of gate on each qubit(s)

        Args:
            circ(Circuit): given circuit
            vqm(VirtualQuantumMachine): given vqm
            mapping(List[int]): Mapping of the circuit.

        Returns:
            list: feature vector
        """

        # use default vqm if not given
        if vqm is None:
            vqm = self.vqm

        # use identity if mapping not given
        if mapping is None:
            mapping = list(range(vqm.qubit_number))

        # index (gate type, qubits)
        gate_types = sorted(vqm.instruction_set.one_qubit_gates + [vqm.instruction_set.two_qubit_gate],
                            key=lambda x: x.value)
        gt_dict = {gt: idx for idx, gt in enumerate(gate_types)}

        feature = self._vqm_feature(vqm, gt_dict) if self.use_vqm else []

        # compute gate counts
        gate_count = {}
        for q1 in vqm.double_gate_fidelity:
            for q2 in vqm.double_gate_fidelity[q1]:
                key = tuple([gt_dict[vqm.instruction_set.two_qubit_gate], q1, q2])
                gate_count[key] = 0

        for q in range(vqm.qubit_number):
            for gt in vqm.instruction_set.one_qubit_gates:
                key = tuple([gt_dict[gt], q])
                gate_count[key] = 0

        for g in circ.gates:
            g: BasicGate
            if g.type == GateType.measure or g.type == GateType.barrier:
                continue

            if g.type not in gt_dict:
                assert False, f'gate type not supported, {g.type}, {g.cargs + g.targs}'

            mapped_qubit = [mapping[x] for x in g.cargs + g.targs]
            key = tuple([gt_dict[g.type]] + mapped_qubit)
            if key not in gate_count:
                assert False, f'qubit out of range or not connected, {g.type} on {mapped_qubit}'
            gate_count[key] += 1

        # sort values by key in gate_count
        gate_count = sorted(gate_count.items(), key=lambda x: x[0])

        feature.extend([x[1] for x in gate_count])
        return feature

    def fidelity_to_label(self, f):
        return 1 - f

    def label_to_fidelity(self, label):
        return 1 - max(label, 0)

    def fit(self, data, have_vqm=False, num_epochs=50000):
        """
        Fit the fidelity estimator with given data.

        Args:
            data(list): list of tuples (circ, vqm, fidelity)
            have_vqm(bool): whether the data contains vqm
            num_epochs(int): number of epochs to train
        """

        # use default vqm if not given
        if not have_vqm:
            data = [[circ, None, f] for circ, f in data]

        features = []
        labels = []
        for circ, vqm, f in data:
            feature = self._compute_features(circ, vqm)
            features.append(feature)
            labels.append(self.fidelity_to_label(f))

        X = self.scaler.fit_transform(np.array(features))
        X = torch.tensor(X, dtype=torch.float32)

        y = torch.tensor(np.array(labels).reshape(-1, 1), dtype=torch.float32)
        criterion = nn.MSELoss()
        optimizer = optim.SGD(self.model.parameters(), lr=0.01)

        for epoch in range(num_epochs):
            outputs = self.model(X)
            optimizer.zero_grad()
            loss = criterion(outputs, y)
            loss.backward()
            optimizer.step()
            if epoch % 100 == 0:
                print('epoch {}, loss {}'.format(epoch, loss.item()))

    def estimate_fidelity(self, circ: Circuit, vqm: VirtualQuantumMachine = None, mapping: List[int] = None):
        """
        Estimate the fidelity of a given circuit.

        Args:
            circ(Circuit): given circuit
            vqm(VirtualQuantumMachine): given vqm, use default vqm if not given
            mapping(List[int]): Mapping of the circuit. Identity if None.

        Returns:
            float: fidelity
        """

        circ.flatten()
        feature = self._compute_features(circ, vqm, mapping)
        feature = self.scaler.transform(np.array([feature]))
        inputs = torch.from_numpy(feature).float()
        outputs = self.model(inputs)
        return self.label_to_fidelity(outputs.item())
