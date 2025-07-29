# MODI

Package for calculating the Modelability Index (MODI) of a QSAR dataset. You can read about the MODI in the
[original paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC3984298/).
MODI is mathematically equivalent to the uniform-class average of the leave-one-out cross-validation accuracy for
a 1-nearest neighbor classifier *on the training data*. The paper claims if this value is not high, then not model
will be able to predict well on the new data. While maybe true for small datasets, the law of scaling is real and
this work was written before nueral networks in chemistry became popular. With large non-linear models, this might
not hold True, though it is still a useful metric if tyring to understand how well separated your classes are in feature space.

By default, MODI is calculated using the Tanimoto distance between Morgan fingerprints. However, you can also provide
your own data matrix and distance metric if you are using non-sparse non-binary features.

If you use this package in your work, please cite the original paper:
```text
Golbraikh A, Muratov E, Fourches D, Tropsha A. Data set modelability by QSAR. J Chem Inf Model. 2014 Jan 27;54(1):1-4. doi: 10.1021/ci400572x. Epub 2014 Jan 8. PMID: 24251851; PMCID: PMC3984298.
```

## Installation
You can install the package via pip:

```bash
pip install qsar_modi
```

You can also clone the repository and build from source using poetry:

```bash
git clone https://github.com/molecularmodelinglab/modi
cd modi
poetry build
```

## Usage
You can use MODI in your Python scripts as follows:

```python
from qsar_modi import modi

smiles = ["CCO", "CCN", "CCC", "CCCl", "CCBr", "CCCCl", "CCCBr"]
labels = ["A", "A", "B", "B", "A", "C", "C"]

modi_value, class_contributions = modi(chemicals=smiles, labels=labels)
```
`modi` returns both the MODI value and a breakdown of contributions from each class.
MODI is defined as the uniform average of the class contributions, but observing
the class contributions can help identify which classes are well separated and which are not.

MODI support several types of fingerprints, see the docstring for details.
```python
modi_value, class_contributions = modi(chemicals=smiles, labels=labels, fp_type="bAtomPair")
```

You can also provide your own data matrix and distance metric:
```python
data = numpy.random.random((100, 100)) # pretend this is your feature matrix
labels = [0] * 50 + [1] * 50  # pretend these are your class labels

modi_value, class_contributions = modi(data=data, labels=labels, metric="euclidean")
```

Lastly, pairwise distances are expensive to compute. MODI will automatically avoid calculating the entire
pairwise distance matrix if your dataset is large enough (more than 25,000 chemicals). Instead it will use a
row by row approach to save memory (at the sacrifice of speed). You can control this behavior with the
`force_pdist` and `force_loop` parameters. `force_pdist` will force the use of the full pairwise distance matrix, while
`force_loop` will force the row by row approach. By default, neither is set and MODI will choose the best approach
```python
modi_value, class_contributions = modi(data=data, labels=labels, metric="euclidean", force_loop=True)
```

## Command Line Interface
MODI has a command line interface (CLI) that you can use to calculate MODI from a CSV or SDF file, given some type of
class label is linked to each chemical. The CLI can be accessed via the `modi` command after installing the package.

```bash
modi my_chemicals.sdf --label-name activity_class
```

This will return the MODI value and class contributions for the chemicals in `my_chemicals.sdf`, as
well as some extra info about how it was calculated (FP type, number of classes, etc.).
> [!note]
> The CLI does not support pre-embedded data. If you have a CSV with pre-calculated features, you will need to
> to use the Python API instead.
