import os.path
import pickle as pkl
import numpy as np
import torch
from sklearn.preprocessing import StandardScaler
from typing import List
import lightgbm as lgb

from QuICT.core import Circuit
from QuICT.core.gate import BasicGate
from QuICT.core.utils import GateType
from QuICT.core.virtual_machine import VirtualQuantumMachine, InstructionSet
from QuICT.qcda.utility.fidelity_estimator.circuit_path import enumerate_all_path
from QuICT.qcda.utility.fidelity_estimator.circuit_feature import CircuitFeature


class LGMFidelityEstimator:
    """
        lightgbm based fidelity estimator.
    """

    # built-in supported machines
    SUPPORTED_MACHINE = [
        'ibm_geneva',
        'ibm_hanoi',
        'ibm_montreal',
        'ibm_mumbai',
        'ibm_toronto',
    ]

    def __init__(
            self,
            vqm: VirtualQuantumMachine = None,
            step=2):
        """
        Warnings:
            vqm can be None, but you should specify self.vqm before using
            other functions.
        Args:
            vqm(VirtualQuantumMachine): target machine.
            step(int): step of path to be considered, should be 2 as default.
        """
        self.vqm = vqm
        self.step = step
        self.path = []
        self.model = None
        self.scaler = StandardScaler()
        if self.vqm is not None:
            self._init_path()

    @classmethod
    def from_target_machine(cls, target_machine):
        """
        Info:
            Load default fidelity estimator from given target_machine.
            See LGMFidelityEstimator.SUPPORTED_MACHINE for supported machines.

        Args:
            target_machine(str): target machine
        Returns:
            LGMFidelityEstimator: fidelity estimator
        """
        if target_machine not in cls.SUPPORTED_MACHINE:
            raise ValueError(f'Unsupported machine: {target_machine}')
        data_id = cls.SUPPORTED_MACHINE.index(target_machine) + 1
        base_dir = os.path.join(os.path.dirname(__file__), 'models')
        scaler = pkl.load(open(os.path.join(base_dir, 'scaler' + str(data_id) + '.pkl'), 'rb'))
        model = pkl.load(open(os.path.join(base_dir, 'model' + str(data_id) + '.pkl'), 'rb'))
        vqm = pkl.load(open(os.path.join(base_dir, 'vqm' + str(data_id) + '.pkl'), 'rb'))
        fe = cls(vqm=vqm)
        fe.scaler = scaler
        fe.model = model
        fe.model.params["verbose"] = -1
        return fe

    @classmethod
    def load(cls, file_path=None, file_prefix=""):
        """
        Load a fidelity estimator from given path and prefix.
        Args:
            file_path(str): path of files
            file_prefix(str): prefix of files
        Returns:
            LGMFidelityEstimator: fidelity estimator
        """
        if file_path is None:
            file_path = os.path.join(os.path.dirname(__file__), 'models')
        scaler = pkl.load(open(os.path.join(file_path, file_prefix + 'scaler.pkl'), 'rb'))
        model = pkl.load(open(os.path.join(file_path, file_prefix + 'model.pkl'), 'rb'))
        vqm = pkl.load(open(os.path.join(file_path, file_prefix + 'vqm.pkl'), 'rb'))
        fe = cls(vqm=vqm)
        fe.scaler = scaler
        fe.model = model
        fe.model.params["verbose"] = -1
        return fe

    def save(self, file_path=None, file_prefix=None):
        """
        Save a fidelity estimator to given path and prefix.
        Args:
            file_path(str): path of files
            file_prefix(str): prefix of files
        """
        if file_path is None:
            file_path = os.path.join(os.path.dirname(__file__), 'models')
        if file_prefix is None:
            file_prefix = ""
        pkl.dump(self.scaler, open(os.path.join(file_path, file_prefix + 'scaler.pkl'), 'wb'))
        pkl.dump(self.model, open(os.path.join(file_path, file_prefix + 'model.pkl'), 'wb'))
        pkl.dump(self.vqm, open(os.path.join(file_path, file_prefix + 'vqm.pkl'), 'wb'))

    def _init_path(self):
        # after loading data, first init self.path
        self.path = enumerate_all_path(self.step, self.vqm.instruction_set)

    def data2feature_label(self, data, mapping: List[int] = None, is_train=True):
        """
        Convert [(Circuit, vqm),...] into (features, labels).
        Here vqm can be None, if you have already specified vqm.
        Args:
            data(list): data to be converted
            mapping(List[int]): mapping of qubits
            is_train(bool): data is for train or not
        Returns:
            tuple(torch.Tensor, torch.Tensor): (features, labels)
        """
        features = []
        labels = []
        if isinstance(data[0], Circuit):
            data = [data]
        for datum in data:
            feature = self._compute_feature(datum, mapping)
            feature = feature.reshape(1, -1)
            features.append(feature)
            labels.append(datum[2])
        features = torch.cat(features, dim=0)
        readout = features[:, -1].reshape(-1, 1)
        features = features[:, :-1].numpy()
        if is_train:
            features = self.scaler.fit_transform(features)
        else:
            self.scaler.transform(features)
        labels = torch.tensor(labels).reshape(-1, 1)
        features = torch.from_numpy(features)
        features = torch.cat([features, readout], dim=1)
        return features, labels

    def data2feature(self, data, mapping: List[int] = None):
        """
        Convert [(Circuit, vqm),...] into features.
        Here vqm can be None, if you have already specified vqm.
        Args:
            data(list): data to be converted
            mapping(List[int]): mapping of qubits
        Returns:
            torch.Tensor: features
        """
        features = []
        if isinstance(data[0], Circuit):
            data = [data]
        for datum in data:
            feature = self._compute_feature(datum, mapping)
            feature = feature.reshape(1, -1)
            features.append(feature)
        features = torch.cat(features, dim=0)
        readout = features[:, -1].reshape(-1, 1)
        features = features[:, :-1].numpy()
        features = self.scaler.transform(features)
        features = torch.from_numpy(features)
        features = torch.cat([features, readout], dim=1)
        return features

    def _compute_feature(self, datum, mapping):
        """
        Compute the feature according to the vqm as datum[1].
        If datum[1] is None, use self.vqm instead.
        Args:
            datum(list or Circuit): a datum in data
            mapping(List[int]): mapping of qubits
        Returns:
            torch.Tensor: output tensor
        """
        # first check vqm
        if self.vqm is None:
            assert isinstance(datum[1], VirtualQuantumMachine), "No VirtualQuantumMachine is found"
            self.vqm = datum[1]
            self.path = []
        # then check path
        if len(self.path) == 0:
            self._init_path()
        # if datum[1] is None or out of index
        if len(datum) <= 1 or datum[1] is None:
            using_vqm = self.vqm
        else:
            using_vqm = datum[1]
        # then handle mapping
        if mapping is None:
            mapping = list(range(using_vqm.qubit_number))

        affect_qubit = []
        for g in datum[0].gates:
            g: BasicGate
            if g.type == GateType.measure or g.type == GateType.barrier:
                continue
            for qubit in [mapping[x] for x in g.cargs + g.targs]:
                if qubit not in affect_qubit:
                    affect_qubit.append(qubit)
        feature = torch.zeros((len(self.path), 1))
        cf = CircuitFeature(datum[0], using_vqm, self.step, mapping)
        for idx in range(len(self.path)):
            feature[idx, 0] = cf.count_path(self.path[idx])
        readout = torch.tensor(1)
        for qubit in affect_qubit:
            readout = readout * max(using_vqm.qubit_fidelity[qubit][0],
                                    using_vqm.qubit_fidelity[qubit][1])
        readout = readout.reshape(1, 1)
        feature = torch.cat([feature, readout], dim=0)

        return feature

    def _check_circuit(self, circ: Circuit,
                       vqm: VirtualQuantumMachine = None,
                       mapping: List[int] = None):
        # check if the circuit can be fulfilled on the target vqm
        if vqm is None:
            vqm = self.vqm
        if circ.width() > vqm.qubit_number:
            return False
        if mapping is None:
            mapping = list(range(vqm.qubit_number))

        for g in circ.gates:
            g: BasicGate
            if g.type == GateType.measure or g.type == GateType.barrier:
                continue

            if g.type not in vqm.instruction_set.gates:
                return False

            if g.type == vqm.instruction_set.two_qubit_gate:
                q1 = mapping[g.cargs[0]] if len(g.cargs) > 0 else mapping[g.targs[1]]
                q2 = mapping[g.targs[0]]
                if q1 not in vqm.double_gate_fidelity[q2].keys() \
                        or vqm.double_gate_fidelity[q2][q1] <= 0.01:
                    return False
        return True

    def fit(self, data, mapping: List[int] = None, **kwargs):
        """
        Fit this estimator with given data
        Args:
            data(List[Circuit, vqm, labels]): list of data for fitting
            mapping(List[int]): mapping of qubits
            kwargs: args in lightGBM
        """
        kwargs['objective'] = 'regression'
        if self.vqm is None:
            assert isinstance(data[0][1], VirtualQuantumMachine), "No VirtualQuantumMachine is found"
            self.vqm = data[0][1]
        if mapping is None:
            mapping = list(range(self.vqm.qubit_number))
        train_features, train_labels = self.data2feature_label(data, mapping, is_train=True)
        train_features = train_features.numpy()
        train_labels = train_labels.numpy()
        if "num_boost_round" not in kwargs.keys():
            num_boost_round = 100
        else:
            num_boost_round = kwargs["num_boost_round"]
            del kwargs["num_boost_round"]
        d_train = lgb.Dataset(train_features, label=train_labels)
        self.model = lgb.train(params=kwargs, train_set=d_train, num_boost_round=num_boost_round)
        if "verbose" in kwargs and kwargs["verbose"] >= 1:
            print("Fit done.")

    def estimate_fidelity(self, circ: Circuit,
                          vqm: VirtualQuantumMachine = None,
                          mapping: List[int] = None):
        """
        Estimate the fidelity on the target vqm.
        If the vqm remains the same, please set as None.
        This vqm should have the same InstructionSet as self.vqm
        Args:
            circ(Circuit): circuit to estimate
            vqm(VirtualQuantumMachine): vqm to estimate
            mapping(List[int]): mapping of qubits
        Returns:
            list(float): fidelity
        """
        assert self.model is not None, "No trained model!"
        if self.vqm is None:
            assert isinstance(vqm, VirtualQuantumMachine), "No VirtualQuantumMachine is found!"
            self.vqm = vqm
            self.path = []

        elif vqm is None:
            vqm = self.vqm

        if mapping is None:
            mapping = list(range(self.vqm.qubit_number))
        assert self._check_circuit(circ, vqm, mapping), \
            "This circuit cannot be implemented on this VirtualQuantumMachine!"
        features = self.data2feature([circ, vqm], mapping).numpy()

        return self.model.predict(features).item()
