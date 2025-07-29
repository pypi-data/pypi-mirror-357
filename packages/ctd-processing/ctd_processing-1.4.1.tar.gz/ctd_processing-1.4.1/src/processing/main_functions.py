from pathlib import Path
import logging
from seabirdfilehandler import HexCollection, CnvFile
from processing import Procedure, Configuration

logger = logging.getLogger(__name__)


def convert(
    input_dir: Path | str,
    psa_path: Path | str,
    output_dir: Path | str = "",
    xmlcon_dir: Path | str = "",
    pattern: str = "",
) -> list[Path]:
    """
    Converts a list of Sea-Bird raw data files (.hex) to .cnv files.

    Does either use an explicit list of paths or searches for all .hex files in
    the given directory.

    Parameters
    ----------
    input_dir: Path | str :
        The data directory with the target .hex files.
    psa_path: Path | str :
        The path to the .psa for datcnv.
    output_dir: Path | str :
        The directory to store the converted .cnv files in. (Default is the input directory)
    xmlcon_dir: Path | str :
        The directory to look for .xmlcon files. (Default is the input directory)
    pattern: str :
        A name pattern to filter the target .hex files with. (Default is none)

    Returns
    -------
    A list of paths or CnvFiles of the converted files.

    """
    if not output_dir:
        output_dir = input_dir
    if not xmlcon_dir:
        xmlcon_dir = input_dir
    hexes = HexCollection(
        path_to_files=input_dir,
        pattern=pattern,
        file_suffix="hex",
        path_to_xmlcons=xmlcon_dir,
    )
    resulting_cnvs = []
    proc_config = {
        "output_dir": output_dir,
        "modules": {
            "datcnv": {"psa": psa_path},
        },
    }
    procedure = Procedure(
        proc_config,
        auto_run=False,
    )
    for hex in hexes:
        try:
            result = procedure.run(hex.path_to_file)
        except Exception as e:
            logger.error(f"Failed to convert: {hex.path_to_file}, {e}")
        else:
            resulting_cnvs.append(result)
    return resulting_cnvs


def batch_processing(
    input_dir: Path | str,
    config: dict | Path | str,
    pattern: str = ".cnv",
) -> list[Path] | list[CnvFile]:
    """
    Applies a processing config to multiple .hex or. cnv files.

    Parameters
    ----------
    input_dir: Path | str :
        The data directory with the target files.
    config: dict | Path | str:
        Either an explicit config as dict or a path to a .toml config file.
    pattern: str :
        A name pattern to filter the target files with. (Default is ".cnv")

    Returns
    -------
    A list of paths or CnvFiles of the processed files.

    """
    resulting_cnvs = []
    if isinstance(config, dict):
        proc_config = config
    else:
        proc_config = Configuration(config)
    procedure = Procedure(proc_config, auto_run=False)
    for file in Path(input_dir).rglob(f"*{pattern}*"):
        try:
            result = procedure.run(file)
        except Exception as e:
            logger.error(f"Error when processing {file}: {e}")
        else:
            resulting_cnvs.append(result)
    return resulting_cnvs
