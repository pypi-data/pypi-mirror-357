from __future__ import annotations
from os import PathLike
from seabird import fCNV
import pandas as pd
from typing import Dict, Any, Optional


class StimuliProfile:
    """A class for managing tabular stimuli data with a required 'depth' index."""

    columns: pd.Index
    data: pd.DataFrame
    cnv: Optional[fCNV]

    def __init__(self, data: pd.DataFrame, cnv: Optional[fCNV] = None) -> None:
        """
        Initialize the StimuliTable with given data.

        Parameters
        ----------
        data: Dict[str, Any]
            The stimuli profile data
        """
        if 'depth' not in data.columns:
            raise ValueError("'depth' must be included as a column.")

        self.columns = data.columns
        self.data = data.set_index('depth')
        self.cnv = cnv

    def add_entry(self, depth: float, data: Dict[str, Any]) -> None:
        """
        Add a row of data, indexed by 'depth'.

        Parameters
        ----------
        depth: float
            The depth value for this row.
        data: Dict[str, Any]
            A dictionary of column values (excluding 'depth').
        """
        if not all(col in self.columns for col in data.keys()):
            raise ValueError(f"Invalid columns in data. Expected columns: {self.columns}")

        self.data.loc[depth] = data

    def add_stimuli(self, stimuli: pd.Series) -> None:
        """
        Add a stimuli series to the table.

        Parameters
        ----------
        stimuli: pd.Series
            The stimuli series to add.
        """
        if not all(stimuli.index == self.data.index):
            raise ValueError("Stimuli series 'depth' values must match the existing data.")

        self.data = self.data.join(stimuli)

    @classmethod
    def read_from_tabular_file(cls, file_path: str | PathLike[str], file_type: str = "csv") -> StimuliProfile:
        """
        Read stimuli data from a file and populate the table.

        Parameters
        ----------
        file_path: str
            The path to the file.
        file_type: str
            The file type ('csv', 'excel'). Default is 'csv'.

        Raise
        -----
        ValueError
            If the file type is unsupported.

        Returns
        -------
        StimuliProfile
            The StimuliProfile instance.
        """
        if file_type == "csv":
            df = pd.read_csv(file_path)
        elif file_type == "excel":
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file type. Use 'csv' or 'excel'.")

        return cls(df)


    @classmethod
    def read_from_cnv(cls, file_path: str | PathLike[str]) -> StimuliProfile:
        """
        Read stimuli data from a CNV file and populate the table.
        TODO: Pretty sure the .cnv data needs some love before it can be used here.

        Parameters
        ----------
        file_path: str
            The path to the CNV file.

        Raise
        -----
        ValueError
            If no data is found in the file.

        Returns
        -------
        StimuliProfile
            The StimuliProfile instance
        """
        cnv = fCNV(file_path)
        data = cnv.as_DataFrame()
        if data is None:
            raise ValueError("No data found in file.")

        if 'depth' not in data.columns:
            data['depth'] = data.index

        df = data

        return cls(df, cnv)
