from pathlib import Path

from iclearn.environment import has_pytorch

from .dataloader import DataloaderCreate, Dataloader


def load_dataloader(config: DataloaderCreate, data_dir: Path) -> Dataloader | None:
    """
    Return a suitable dataloader based on the provided
    config.

    If none is found return none - error handling is left
    to the caller in this case.
    """

    if config.dataset.name == "linear" and has_pytorch():
        from .torch.linear_data import LinearDataloader

        return LinearDataloader(config)
    return None
