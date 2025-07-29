import torch
from torch.utils.data import Dataset as TorchDataset

from iccore.data import Dataset
from iclearn.data import Splits

from .dataloader import TorchDataloader


class LinearDataset(TorchDataset):
    """
    Generate a simple linear dataset
    """

    def __init__(self, dataset: Dataset, stage: str, splits: Splits):
        self.num_classes = 2
        num_datapoints = 10
        w_rand, b_rand = abs(torch.randn(2, 1)) * 2
        noise = torch.randn(num_datapoints, 1)

        self.x = torch.rand(num_datapoints, 1) * 10
        self.y = (w_rand.item()) * (self.x + noise) + b_rand.item()

    def __len__(self):
        return len(self.x)

    def __getitem__(self, idx: int):
        return self.x[idx], self.y[idx]


class LinearDataloader(TorchDataloader):
    """
    Basic dataloader for linear regression problems
    """

    def load_dataset(self, dataset: Dataset, name: str, splits: Splits):
        """
        Creates a PyTorch style dataset of the data for each stage.
        """
        return LinearDataset(dataset, name, splits)
