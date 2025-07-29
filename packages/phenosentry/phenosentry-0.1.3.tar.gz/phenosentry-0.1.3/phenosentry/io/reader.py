import logging
import typing
from ..model import  CohortInfo, PhenopacketInfo, EagerPhenopacketInfo
from pathlib import Path
from google.protobuf.json_format import Parse, ParseError
from phenopackets.schema.v2.phenopackets_pb2 import Phenopacket


def read_phenopacket(
    directory: str,
    logger: logging.Logger,
) -> PhenopacketInfo:
    """
     Reads a single phenopacket from a specified directory.

     Args:
         directory (str): The path to the directory containing the phenopacket file.
         logger (logging.Logger): Logger instance for logging messages.

     Returns:
         PhenopacketInfo: An object containing information about the phenopacket.

     Raises:
         ValueError: If the phenopacket file cannot be parsed due to invalid format.
     """
    logger.info("Reading phenopacket at `%s`", directory)
    try:
        path = Path(directory)
        pp = Parse(path.read_text(), Phenopacket())
    except ParseError as e:
        logger.error("Failed to parse phenopacket at `%s`: %s", directory, e)
        raise ParseError(f"Invalid phenopacket format in {directory}") from e
    return EagerPhenopacketInfo.from_phenopacket(directory, pp)

def read_phenopackets(directory: str, logger: logging.Logger) -> typing.List[PhenopacketInfo]:
    """
    Reads all phenopackets from a specified directory.

    Args:
        directory (str): The path to the directory containing phenopacket files.
        logger (logging.Logger): Logger instance for logging messages.

    Returns:
        typing.List[PhenopacketInfo]: A list of objects containing information about each phenopacket.
    """
    logger.info("Reading phenopackets at `%s`", directory)
    path = Path(directory)
    phenopackets = []
    for pp_path in path.glob("*.json"):
        phenopackets.append(read_phenopacket(pp_path, logger))
    return phenopackets

def read_cohort(
    directory: str,
    logger: logging.Logger,
) -> CohortInfo:
    """
      Reads a cohort of phenopackets from a specified directory.

      Args:
          directory (str): The path to the directory containing the cohort of phenopackets.
          logger (logging.Logger): Logger instance for logging messages.

      Returns:
          CohortInfo: An object containing information about the cohort, including its name, path, and phenopackets.
      """
    logger.info("Reading cohort at `%s`", directory)
    path = Path(directory)
    phenopackets = read_phenopackets(directory, logger)
    return CohortInfo(name=path.name, path=str(path), phenopackets=phenopackets)