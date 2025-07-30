from sklearn.metrics import mean_squared_error
import lightgbm as lgb
import numpy as np
from typing import List
import os
import pickle as pkl

from QuICT.core.virtual_machine import VirtualQuantumMachine
from QuICT.qcda.utility.fidelity_estimator.lgm_fidelity_estimator import LGMFidelityEstimator


class LGMFidelityTrainer:
    def __init__(
            self,
            vqm: VirtualQuantumMachine = None,
            step: int = 2):
        """
        A trainer for training LGMFidelityEstimator.
        All cached data are saved in self.temp.
        Args:
            vqm(VirtualQuantumMachine): desired vqm to estimate
            step(int): step of path in estimator
        """
        self.vqm = vqm
        self.temp = {}
        self.step = step
        self.estimator = LGMFidelityEstimator(step=step, vqm=vqm)

    def save_cached_data(self, file_path=None, file_prefix=None):
        """
        Save temp files to given path and prefix.
        Args:
            file_path(str): path of files
            file_prefix(str): prefix of files
        """
        if file_path is None:
            file_path = os.path.join(os.path.dirname(__file__), 'models')
        if file_prefix is None:
            file_prefix = ""
        pkl.dump(self.temp, open(os.path.join(file_path, file_prefix + 'temp file.pkl'), 'wb'))

    def load_cached_data(self, file_path=None, file_prefix=None):
        """
        Load temp files from given path and prefix.
        Args:
            file_path(str): path of files
            file_prefix(str): prefix of files
        """
        if file_path is None:
            file_path = os.path.join(os.path.dirname(__file__), 'models')
        if file_prefix is None:
            file_prefix = ""
        self.temp = pkl.load(open(os.path.join(file_path, file_prefix + 'temp file.pkl'), 'rb'))

    def save_estimator(self, file_path=None, file_prefix=None):
        """
        Save a fidelity estimator to given path and prefix.
        Args:
            file_path(str): path of files
            file_prefix(str): prefix of files
        """
        assert self.estimator is not None, "No estimator to save!"
        self.estimator.save(file_path=file_path, file_prefix=file_prefix)

    def load_estimator(self, file_path=None, file_prefix=""):
        """
        Load a fidelity estimator from given path and prefix.
        Args:
            file_path(str): path of files
            file_prefix(str): prefix of files
        """
        self.estimator = LGMFidelityEstimator.load(file_path=file_path, file_prefix=file_prefix)

    def clear_cache(self):
        """
        Clear the cache of this trainer.
        """
        self.temp = {}

    def estimate_cached_test(self):
        """
        Estimate the cached test and return the predictions, together with true labels.
        Returns:
            (ndarray, ndarray): (predictions, true labels)
        """
        return self.estimator.model.predict(self.temp["test_features"]), \
            self.temp["test_labels"]

    def _train(self, train_features, train_labels,
               test_features=None, test_labels=None,
               criterion=mean_squared_error, print_score=True, **kwargs):
        # basic training function
        d_train = lgb.Dataset(train_features, label=train_labels)
        if "num_boost_round" not in kwargs.keys():
            num_boost_round = 100
        else:
            num_boost_round = kwargs["num_boost_round"]
            del kwargs["num_boost_round"]
        self.estimator.model = lgb.train(params=kwargs, train_set=d_train, num_boost_round=num_boost_round)
        if test_features is not None:
            pred = self.estimator.model.predict(test_features)
            score = criterion(test_labels, pred)
            if print_score:
                print("In this training, the score on test set is,", score)
            return score
        return None

    def _cross_validate(self, data, fold=5, best_score=0.0,
                        criterion=mean_squared_error, **kwargs):
        # basic function for cross validation
        order = np.random.permutation(data.shape[0])
        if "num_boost_round" not in kwargs.keys():
            num_boost_round = 100
        else:
            num_boost_round = kwargs["num_boost_round"]
            del kwargs["num_boost_round"]
        data_list = np.array_split(data[order, :], fold)
        closet_score = None
        for ii in range(0, fold):
            temp = []
            for jj in range(0, fold):
                if jj != ii:
                    temp.append(data_list[jj])
            temp = tuple(temp)
            train_features = np.concatenate(temp, axis=0)
            train_labels, train_features = \
                train_features[:, -1].reshape(-1, 1), train_features[:, :-1]
            score = self._train(train_features=train_features, train_labels=train_labels,
                                test_features=data_list[ii][:, :-1], num_boost_round=num_boost_round,
                                test_labels=data_list[ii][:, -1].reshape(-1, 1),
                                criterion=criterion,
                                print_score=False,
                                **kwargs)
            if closet_score is None or abs(score - best_score) < abs(closet_score - best_score):
                closet_score = score
                self.temp["temp_cross_validate"] = self.estimator.model
                self.estimator.model = None
        self.estimator.model = self.temp["temp_cross_validate"]
        del self.temp["temp_cross_validate"]

    def fit(self, data=None, save=False, file_path=None, file_prefix=None,
            cross_validate=False, fold=5, best_score=0.0, mapping: List[int] = None,
            criterion=mean_squared_error,
            **kwargs):
        """
        To fit estimator with given data, or cached data if input data is None.
        You can specify the criterion and best score of this criterion.
        Args:
            data(List): data for fitting. Please set None if using preprocessed.
            save(bool): save the model or not.
            file_path(str): path of files to save. Default as ./models
            file_prefix(str): prefix of files to save.
            cross_validate(bool): use cross validate or not.
            fold(int): fold in cross validate.
            best_score(float): best score of the criterion.
            You can set None, but should consist of labels.
            criterion(func): the criterion of test data.
            mapping(List[int]): mapping of qubits
            **kwargs: args in LightGBM, optional to tune.
        Returns:
            criterion(test_labels, prediction) if there are test data or None otherwise.
        """
        # this should be regression
        kwargs['objective'] = 'regression'
        if self.estimator.vqm is None:
            assert isinstance(data[0][1], VirtualQuantumMachine), "No VirtualQuantumMachine is found"
            self.estimator.vqm = data[0][1]
        if mapping is None:
            mapping = list(range(self.estimator.vqm.qubit_number))

        if data is None:
            assert "train_features" in self.temp.keys(), "No data!"
            train_features = self.temp["train_features"]
            train_labels = self.temp["train_labels"]
        else:
            train_features, train_labels = self.estimator.data2feature_label(data, mapping, is_train=True)
            train_features = train_features.numpy()
            train_labels = train_labels.numpy()

        if "num_boost_round" not in kwargs.keys():
            num_boost_round = 100
        else:
            num_boost_round = kwargs["num_boost_round"]
            del kwargs["num_boost_round"]
        if cross_validate:
            train_data = np.concatenate((train_features, train_labels), axis=1)
            self._cross_validate(data=train_data, fold=fold, best_score=best_score,
                                 criterion=criterion, num_boost_round=num_boost_round,
                                 **kwargs)
        else:
            self._train(train_features=train_features, num_boost_round=num_boost_round,
                        train_labels=train_labels, criterion=criterion,
                        print_score="verbose" in kwargs.keys() and kwargs["verbose"] >= 1,
                        **kwargs)
        if save:
            try:
                self.estimator.save(file_path, file_prefix)
            except FileNotFoundError or IOError:
                print("The given path is not valid. The model has been saved to default path.")
                self.estimator.save("", file_prefix)

    def shuffle_data(self, mixed=False):
        """
        Shuffle the preprocessed data
        Args:
            mixed(bool): mix the test data and train data or not.
            The sizes are maintained.
            If not test data, this is automatically set as False.
        """

        assert "train_features" in self.temp.keys(), "No data for shuffle!"
        if "test_features" not in self.temp.keys():
            mixed = False
        data = np.concatenate((self.temp["train_features"],
                               self.temp["train_labels"]), axis=1)
        if mixed:
            test_size = self.temp["test_labels"].shape[0]
            test_data = np.concatenate((self.temp["test_features"],
                                        self.temp["test_labels"]), axis=1)
            data = np.concatenate((data, test_data), axis=0)
        order = np.random.permutation(data.shape[0])
        data = data[order, :]
        if mixed:
            data, test_data = data[test_size:, :], data[:test_size, :]
            self.temp["test_features"], self.temp["test_labels"] = \
                test_data[:, :-1], test_data[:, -1].reshape(-1, 1)
        self.temp["train_labels"], self.temp["train_features"] = \
            data[:, -1].reshape(-1, 1), data[:, :-1]

    def preprocess_data(self, data, mapping: List[int] = None, is_train=True):
        """
        Preprocess the data and save into memories to avoid computing features repeatedly
        Args:
            data(List): data for preprocessing, should consist of labels
            mapping(List[int]): mapping of qubits
            is_train(bool): is the data for train or test
        """
        if self.estimator.vqm is None:
            assert isinstance(data[0][1], VirtualQuantumMachine), "No VirtualQuantumMachine is found"
            self.estimator.vqm = data[0][1]
        if mapping is None:
            mapping = list(range(self.estimator.vqm.qubit_number))
        features, labels = self.estimator.data2feature_label(data, mapping, is_train=is_train)
        features = features.numpy()
        labels = labels.numpy()
        if is_train:
            self.temp["train_features"] = features
            self.temp["train_labels"] = labels
        else:
            self.temp["test_features"] = features
            self.temp["test_labels"] = labels
