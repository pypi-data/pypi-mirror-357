"""
A dataloader for PyTorch
"""

from pathlib import Path

import torch
from torch.utils.data import DataLoader as DataLoaderImpl

from iclearn.data import Splits, Dataloader, DataloaderCreate


class TorchDataloader(Dataloader):
    """
    A dataloader for PyTorch
    """

    def __init__(
        self,
        config: DataloaderCreate,
        path: Path | None = None,
    ):

        super().__init__(config, path)

    def _generate_splits(self, splits: Splits):
        if splits.type == "torch.random":
            fracs = [s.fraction for s in splits.items]
            self._load_dataset(self.config.dataset, "base", splits)
            sub_datasets = torch.utils.data.random_split(self.datasets["base"], fracs)

            for name, ds in zip([s.name for s in splits.items], sub_datasets):
                self.datasets[name] = ds

        else:
            super()._generate_splits(splits)

    def load_dataloader(
        self, dataset, batch_size: int, shuffle: bool, sampler, num_workers: int
    ):
        """
        Override base method to return torch dataloader
        """
        return DataLoaderImpl(
            dataset=dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            sampler=sampler,
            num_workers=num_workers,
        )
