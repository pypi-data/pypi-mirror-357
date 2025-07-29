"""CLI for MODI"""

import itertools
from pathlib import Path

import click
from rdkit import Chem
from rdkit.rdBase import BlockLogs

from .modi import modi


def _read_sdf_file(
    file_path: Path, label_prop_name: str, ignore_failed: bool = False
) -> tuple[list[Chem.Mol], list[str]]:
    """Read an SDF file and return a list of Molable objects."""
    _lock = BlockLogs()

    suppl = Chem.SDMolSupplier(file_path)

    mols: list[Chem.Mol] = []
    labels: list[str] = []

    for i, mol in enumerate(suppl):
        # skip bad molecules if asked to
        if mol is None:
            if not ignore_failed:
                raise ValueError(f"RDKit failed to read molecule at index {i} from {file_path}")
        # get label, skip molecule if it doesn't have the label property
        if label_prop_name in mol.GetPropNames():
            mols.append(mol)
            labels.append(mol.GetProp(label_prop_name))
        else:
            if not ignore_failed:
                raise ValueError(
                    f"Molecule at index {i} from {file_path} does not "
                    f"have property {label_prop_name}"
                )

    return mols, labels


def _read_csv_file(
    file_path: Path,
    smiles_col: str | int,
    label_col: str | int,
    ignore_failed: bool = False,
    has_header: bool = True,
    separator: str = ",",
) -> tuple[list[Chem.Mol], list[str]]:
    """Read a CSV file and return a list of Molable objects."""
    mols: list[Chem.Mol] = []
    labels: list[str] = []

    with open(file_path, "r") as csv_file:
        header_line = csv_file.readline().strip()
        header = header_line.split(separator)
        num_cols = len(header)
        if has_header:
            # get smiles col index
            if isinstance(smiles_col, str):
                try:
                    smiles_col_idx = header.index(smiles_col)
                except ValueError as e:
                    raise ValueError(
                        f"Column {smiles_col} not found in header of {file_path}"
                    ) from e
            else:
                smiles_col_idx = smiles_col

            # get label col index
            if isinstance(label_col, str):
                try:
                    label_col_idx = header.index(label_col)
                except ValueError as e:
                    raise ValueError(
                        f"Column {label_col} not found in header of {file_path}"
                    ) from e
            else:
                label_col_idx = label_col

        else:
            # no header, use indices directly
            if not isinstance(smiles_col, int):
                raise ValueError("smiles_col must be an integer if has_header is False")
            if not isinstance(label_col, int):
                raise ValueError("label_col must be an integer if has_header is False")
            smiles_col_idx = smiles_col
            label_col_idx = label_col

        # check indices are in range
        if smiles_col_idx >= len(header):
            raise ValueError(
                f"Column index {smiles_col_idx} of smiles column out of "
                f"range for columns in {file_path}"
            )
        if label_col_idx >= len(header):
            raise ValueError(
                f"Column index {label_col_idx} of label column out of "
                f"range for columns in {file_path}"
            )

        for i, line in enumerate(
            csv_file if has_header else itertools.chain([header_line], csv_file)
        ):
            parts = line.strip().split(separator)
            if len(parts) > num_cols:
                raise ValueError(f"Line {i} in {file_path} is missing columns")

            smi = parts[smiles_col_idx]
            mol = Chem.MolFromSmiles(smi)

            if smi == "" or mol is None:
                if not ignore_failed:
                    raise ValueError(f"Invalid SMILES '{smi}' at line {i} from {file_path}")
                else:
                    continue

            label = parts[label_col_idx]
            if label == "":
                if not ignore_failed:
                    raise ValueError(f"Missing label at line {i} from {file_path}")
                else:
                    continue

            mols.append(mol)
            labels.append(label)

    return mols, labels


@click.command(name="modi")
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--input-format",
    type=click.Choice(["sdf", "csv"]),
    required=False,
    default=None,
    help="Format of the input file",
)
@click.option(
    "--label-name",
    "-l",
    type=str,
    required=False,
    default="Label",
    help="Name of the property/column to use as the class label",
)
@click.option(
    "--smiles-col",
    "-s",
    type=str,
    required=False,
    default="SMILES",
    help="Name or index of the column containing SMILES (for CSV input only)",
)
@click.option(
    "--fp-type",
    "-f",
    type=click.Choice(
        [
            "bFCFP4",
            "bFCFP6",
            "bECFP4",
            "bECFP6",
            "bAtomPair",
            "bTopologicalTorsion",
            "bRDKit",
        ]
    ),
    required=False,
    default="bFCFP4",
    help="Type of fingerprint to compute",
)
@click.option(
    "--use-chirality",
    "-c",
    is_flag=True,
    help="Whether to account for chirality in the fingerprints",
)
@click.option(
    "--ignore-failed",
    is_flag=True,
    help="Whether to ignore molecules that fail to parse or are "
    "missing required properties/columns",
)
@click.option(
    "--no-header",
    is_flag=True,
    help="Whether the CSV input file has a header row (for CSV input only)",
)
@click.option(
    "--separator",
    "-d",
    type=str,
    required=False,
    default=",",
    help="Column separator for CSV input (for CSV input only)",
)
@click.option(
    "--force-loop",
    is_flag=True,
    help="Force the use of a loop for nearest neighbor calculation "
    "(slower, but lower memory usage)",
)
@click.option(
    "--force-pdist",
    is_flag=True,
    help="Force the use of pairwise distance matrix for nearest neighbor "
    "calculation (faster, but higher memory usage)",
)
@click.option(
    "--use-tqdm",
    is_flag=True,
    help="Whether to show a progress bar during calculation (if available)",
)
def modi_cli(
    input_file: Path,
    input_format: str | None,
    label_name: str,
    smiles_col: str | int,
    fp_type: str,
    use_chirality: bool,
    ignore_failed: bool,
    no_header: bool,
    separator: str,
    force_loop: bool,
    force_pdist: bool,
    use_tqdm: bool,
):
    """
    Calculate the MODI for a set of chemicals in an input file.

    INPUT_FILE is the path to the input file containing the chemicals and their class labels.

    The input file can be in SDF or CSV format. If the format is not specified,
    it will be inferred from the file extension (.sdf or .csv).

    For SDF files, the class labels are read from a property named LABEL_NAME (default "Label").

    For CSV files, the class labels are read from a column named LABEL_NAME (default "Label"),
    and the SMILES are read from a column named SMILES_COL (default "SMILES").
    SMILES_COL can also be specified as an integer index (0-based).

    Example usage:

        modi input.sdf --input-format sdf --label-name Activity

        modi input.csv --input-format csv --label-name Class --smiles-col SMILES

        modi input.csv --input-format csv --smiles-col 0 --label-name 1 --no-header
    """
    _input_file = Path(input_file)
    if input_format is None:
        if _input_file.suffix.lower() == ".sdf":
            _input_format = "sdf"
        elif _input_file.suffix.lower() == ".csv":
            _input_format = "csv"
        else:
            raise click.UsageError(
                "Could not infer input format from file extension; please specify --input-format"
            )
    else:
        _input_format = input_format

    if _input_format == "sdf":
        mols, labels = _read_sdf_file(input_file, label_name, ignore_failed)
    elif _input_format == "csv":
        _smiles_col: int | str
        try:
            _smiles_col = int(smiles_col)
        except ValueError:
            _smiles_col = smiles_col

        _label_col: int | str
        try:
            _label_col = int(label_name)
        except ValueError:
            _label_col = label_name

        mols, labels = _read_csv_file(
            input_file,
            _smiles_col,
            _label_col,
            ignore_failed,
            has_header=not no_header,
            separator=separator,
        )
    else:
        raise click.UsageError(f"Unsupported input format: {input_format}")

    if len(mols) == 0:
        raise click.UsageError("No valid molecules found in the input file")

    if len(mols) != len(labels):
        raise click.UsageError("Number of molecules does not match number of labels")

    modi_value, class_contributions = modi(
        chemicals=mols,
        labels=labels,
        fp_type=fp_type,
        use_chirality=use_chirality,
        force_loop=force_loop,
        force_pdist=force_pdist,
        use_tqdm=use_tqdm,
    )
    print(f"Calculating MODI for {len(mols)} molecules with {len(set(labels))} classes")
    print(f"Using fingerprint type: {fp_type} (chirality: {'on' if use_chirality else 'off'})")
    print(f"MODI: {modi_value:.3f}")
    print("\nClass contributions:")
    for class_label, contribution in class_contributions.items():
        print(f"  {class_label}: {contribution:.3f}")
