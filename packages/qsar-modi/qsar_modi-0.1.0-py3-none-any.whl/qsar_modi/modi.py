"""main MODI functions"""

import warnings
from typing import Optional, Sequence

import numpy as np
import numpy.typing as npt
from psutil import virtual_memory
from scipy.spatial.distance import cdist, pdist, squareform
from tqdm import tqdm

from .chem_utils import Molable, mols_to_fps_array, to_mol


MAX_SIZE_FOR_NUMPY = 25000


def _get_nearest_neighbor_pairwise_dist_matrix(data: npt.NDArray, metric: str) -> npt.NDArray:
    """
    Get the nearest neighbor for each point in the data using a pairwise distance matrix.

    Parameters
    ----------
    data : npt.NDArray
        The input data for which to calculate the pairwise distance matrix.
    metric : str
        The type of distance metric to use
        see the SciPy docs for info on available metrics

    Returns
    -------
    npt.NDArray
        An array of indices for the nearest neighbors for each point in the data.
        Will have the same length as the first dimension of the data.
    """
    dist_matrix = squareform(pdist(data, metric=metric))
    np.fill_diagonal(dist_matrix, np.inf)
    return np.argmin(dist_matrix, axis=1)


def _get_nearest_neighbor_loop(data: npt.NDArray, metric: str, use_tqdm: bool = False):
    """
    Get the nearest neighbor for each point in the data looping over each element.

    This is better for large datasets where the pairwise distance matrix might
    exceed memory limits. It will be slower though.

    Parameters
    ----------
    data : npt.NDArray
        The input data for which to calculate the pairwise distance matrix.
    metric : str
        The type of distance metric to use
        see the SciPy docs for info on available metrics
    use_tqdm : bool, default=False
        Whether to render a tqdm progress bar

    Returns
    -------
    npt.NDArray
                An array of indices for the nearest neighbors for each point in the data.
        Will have the same length as the first dimension of the data.
    """
    nns = []
    for i, row in tqdm(
        enumerate(data),
        total=data.shape[0],
        disable=not use_tqdm,
        description="Calculating nearest neighbors",
    ):
        dists = cdist(row.reshape(1, -1), data, metric=metric)
        dists[0, i] = np.inf  # Ignore self-distance
        nns.append(np.argmin(dists))
    return nns


def modi(
    labels: Sequence[int | str],
    chemicals: Optional[Sequence[Molable]] = None,
    data: Optional[npt.NDArray] = None,
    metric: Optional[str] = None,
    fp_type: str = "bFCFP4",
    use_chirality: bool = False,
    use_tqdm: bool = False,
    force_pdist: bool = False,
    force_loop: bool = False,
) -> tuple[float, dict[int | str, float]]:
    """
    Calculate the nearest neighbor for each chemical in the input sequence.

    If the number of chemicals is greater than 25,000,
    a loop is used to calculate the nearest neighbors to save memory.

    Parameters
    ----------
    labels : Sequence[int | str]
        the labels assigned to each chemical.
    chemicals : Optional[Sequence[Molable]]]
        A sequence of chemical objects (e.g., SMILES strings or RDKit Mol objects).
        Chemical will be embedded using the fingerprint functions.
        Cannot be used in combination with `data`
    data : Optional[npt.NDArray]
        a 2D array in the shape (num_chemical, embedding_size) of precalculated
        chemical embeddings.
        Cannot be used in combination with `chemicals`
    metric: Optional[str], default = "euclidean" | "jaccard"
        the distance metric to used for the NN calculation
        if not passed, will default to "euclidean" if `data` was used
        or "jaccard" if `chemical` was used
    fp_type : str, default="bFCFP4"
        the type of fingerprint to generate
        see the docs for all possible types
    use_chirality : bool, default=False
        account for chirality in the fingerprint
    use_tqdm : bool, default=False
        Whether to render a tqdm progress bar
    force_pdist : bool, default=False
        Whether to force the use of pairwise distance matrix calculation.
        Preferred method if memory is not a concern
        Cannot be used with `force_loop=True`.
    force_loop : bool, default=False
        Whether to force the use of a loop for calculating nearest neighbors.
        Useful when memory is a concern, but will be slower.
        Cannot be used with `force_pdist=True`.

    Returns
    -------
    tuple[float, dict[int|str, float]]
        the calculated MODI value, the list of class contributions
    """
    # handle chekcing input
    if data is None and chemicals is None:
        raise ValueError("both `data` and `chemcials` cannot be `None`")
    elif data is not None and chemicals is not None:
        raise ValueError("only `data` *or* `chemicals` should passed, not both")
    elif chemicals is not None:
        if metric is None:
            metric = "jaccard"
        data = mols_to_fps_array(
            [to_mol(chem, fail_on_error=True) for chem in chemicals],
            fp_type=fp_type,
            use_chirality=use_chirality,
        )
    elif data is not None:
        if metric is None:
            metric = "euclidean"
    else:
        raise RuntimeError("unreachable; raise issue if observed at runtime")

    if metric is None:
        raise RuntimeError("unreachable; raise issue if observed at runtime")
    else:
        _metric = metric

    if force_loop and force_pdist:
        raise ValueError(
            "Cannot force both loop and pairwise distance matrix calculation; choose one."
        )

    _use_loop = force_loop or (data.shape[0] > MAX_SIZE_FOR_NUMPY)

    if _use_loop:
        nns = _get_nearest_neighbor_loop(data, metric=_metric, use_tqdm=use_tqdm)
    else:
        # check for memory overflow
        _avail_mem = virtual_memory().available
        if (data.shape[0] ** 2) * 8 > _avail_mem:
            warnings.warn(
                f"Pairwise distance matrix required for MODI is likely to exceed available memory;"
                f"estimated size is {round(((data.shape[0] ** 2) * 8) / (1024**3), 2)} GB, "
                f"available memory is {round(_avail_mem / (1024**3), 2)} GB. "
                "Try running modi with `use_loop=True` to avoid memory issues.",
                stacklevel=1,
            )
        nns = _get_nearest_neighbor_pairwise_dist_matrix(data, metric=_metric)

    # handle modi calculation
    labels = np.array(labels)

    classes = np.unique(labels)
    k: int = classes.shape[0]
    nn_labels = labels[nns]

    # calculate the modi
    modi_value: float = 0.0
    class_contrib: dict[int | str, float] = {}

    # loop through each class
    for c in classes:
        c_arr = np.where(labels == c)[0]
        c_labels = labels[c_arr]
        c_nn_labels = nn_labels[c_arr].flatten()

        _class_modi_val = np.sum(c_labels == c_nn_labels) / c_arr.shape[0]
        modi_value += _class_modi_val
        class_contrib[c] = _class_modi_val

    return (modi_value / k), class_contrib
