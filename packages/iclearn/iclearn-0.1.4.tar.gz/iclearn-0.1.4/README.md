# iclearn

This project has tools for building production-focused machine learning workflows. It is used in some ICHEC projects and [demos](https://git.ichec.ie/performance/recipes/machine_learning).


## What is this project for? ##

Machine learning research often uses tools such as Jupyter Notebooks for exploring and iterating on models. On the other hand a production machine learning system will look quite different - focusing on reliability, error handling and standarization.

While Jupyter Notebooks work well for individual researchers they create issues in a team and collaborative setting, namely:

* difficulty in working with version control
* discourages testing and re-use of components
* doesn't emphasise reliability and monitoring

This library aims to encourage collaborative work on machine learning problems, with outputs that are easier to deploy to a production setting than taking them from a Notebook. It does this by:

* introducing opinionated APIs to standardize all elements of the workflow, down to which command line arguments to use in scripts.
* including common, tested components that we can develop together and rely on
* making best-practice tooling and choices prominent and easily available
* supporting high performance and distributed processing by default

There are many libraries supporting machine learning workflows - by definition they need to be opinionated. This library gives us the option  (which we may or may not always take) to use our own opions and to quickly add any features that we need. It is also a chance to become intimiately familiar with how machine learning workflows work.

## Features ##

The project is both a library of utilities than can be used themselves in building a machine learning workflow and a template for quickly constructing workflows.

It has the following modules:

* `cli`: A standarized set of CLI arguments for loading with `argparse`, allows you do to `my_prog train`, `my_prog infer` etc.
* `data`: Data preparation, processing and loading utilities
* `environment`: Sampling of the runtime environment to get info on available GPUs, CUDA features etc
* `model`: Generic interface for machine learning models, holds things like the optimizer and metrics definitions. Similar to Keras.
* `output`: Output handlers for logging, plotting, syncing with mlflow during training
* `utils`: Utilities such as profilers

By specializing a `model` with a concrete implementation via class inheritence - including an optimizer and set of metrics it is possible to quickly assemble a script that can be used to train the model in a distributed compute environment, run inference or preview a dataset. As a quick pseudo-code example it will look something like:

```python
from pathlib import Path

from iclearn.data import Dataloader, Splits
from iclearn.model import Model, Metrics

class MyModel(Model):

    def __init__(metrics: Metrics):
        super(metrics = metrics, MyOptimizer(MyLossFunc()))
        
    def predict(self, x):
        return ...
        
class MyDataloader(Dataloader):

    def load_dataset(root: Path, name: str, splits):
        return ...
        
    def load_dataloader(name: str):
        return...


def create_dataset(dataset_dir: Path, batch_size: int):
    return MyDataloader(dataset_dir, batch_size)

def create_model(num_classes: int, learning_rate: float, num_batches: int):
    return MyModel(num_classes, learning_rate, num_batches)


if __name__ == "__main__":

    parser = iclearn.cli.get_default_parser(create_dataset, create_model)

    args = parser.parse_args()
    args.func(args)
```

This will create a program which can be used to train a model with a rich set of command line arguments to control the process, for example:

``` shell
myprog train --dataset_dir $DATASET_DIR --node_id 0 --gpus_per_node 2 --num_epochs 20
```

will run a multi-gpu training session using the data in `$DATASET_DIR`, outputting logs, environment information and model results.

## Installing ##

The package is available on PyPI, you can install the base package with:

``` shell
pip install iclearn
```

Most functionality so far uses PyTorch, you can install the PyTorch add-ons with:

``` shell
pip install 'iclearn[torch]'
```

## Running Tests ##

Install the base test dependencies with:

```
pip install '.[test]'
```

then you can run:

```
pytest test/
```

## License ##

This software is Copyright ICHEC 2024 and can be re-used under the terms of the GPL v3+. See the included `LICENSE` file for details.
