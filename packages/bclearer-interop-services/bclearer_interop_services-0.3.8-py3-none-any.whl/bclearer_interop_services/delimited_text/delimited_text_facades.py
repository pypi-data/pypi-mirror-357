import csv
import os
import warnings
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
)

import pandas as pd
from bclearer_core.constants.standard_constants import (
    UTF_8_ENCODING_NAME,
    WRITE_ACRONYM,
)

# Import delimited_text service functions
from bclearer_interop_services.delimited_text.csv_files_from_folder_to_dataframe_dictionary_reader import (
    read_csv_files_from_folder_to_dataframe_dictionary,
)
from bclearer_interop_services.delimited_text.csv_summarizer import (
    generate_detailed_csv_summary,
    summarize_csv,
    summarize_csv_directory,
)
from bclearer_interop_services.delimited_text.dataframe_dictionary_to_csv_files_writer import (
    write_dataframe_dictionary_to_csv_files,
    write_dataframe_to_csv_file,
)
from bclearer_interop_services.delimited_text.delimited_text_read import (
    get_table_from_csv_with_header,
    get_table_from_csv_with_header_with_encoding_detection,
)
from bclearer_interop_services.delimited_text.list_of_strings_to_csv_exporter import (
    export_list_of_strings_to_csv,
)
from bclearer_interop_services.delimited_text.table_as_dictionary_to_csv_exporter import (
    export_table_as_dictionary_to_csv,
)
from bclearer_interop_services.file_system_service.encoding.file_encoding_detector import (
    detect,
)
from bclearer_interop_services.file_system_service.objects.files import (
    Files,
)
from bclearer_interop_services.file_system_service.objects.folders import (
    Folders,
)
from pandas import DataFrame


class DelimitedTextFacades:
    """
    A facade for working with CSV files and other delimited text formats.

    This class provides a unified interface for reading, writing, and analyzing
    CSV files and other delimited text formats. It wraps the functionality of the
    delimited_text module in a single, easy-to-use class.
    """

    def __init__(
        self,
        file_path: Optional[
            Union[str, Path]
        ] = None,
    ):
        """
        Initialize the DelimitedTextFacades class.

        Args:
            file_path: Optional path to a CSV file to work with.
        """
        self.file_path = file_path
        self._dataframe = None
        self._encoding = None

        # Load the file if provided
        if file_path:
            self.load_csv(file_path)

    # ---- CSV Reading Methods ----

    def load_csv(
        self,
        file_path: Union[str, Path],
        encoding: Optional[str] = None,
        sep: str = ",",
        custom_header: List[str] = None,
    ) -> DataFrame:
        """
        Load a CSV file into a pandas DataFrame.

        Args:
            file_path: Path to the CSV file
            encoding: Encoding of the file (auto-detected if None)
            sep: Separator character
            custom_header: Optional list of column names to use

        Returns:
            The loaded DataFrame with appropriate type conversion
        """
        self.file_path = file_path

        if encoding:
            self._encoding = encoding
            self._dataframe = get_table_from_csv_with_header(
                relative_filename=file_path,
                file_encoding=encoding,
                sep=sep,
                custom_header=custom_header,
            )
        else:
            self._encoding = detect(
                file_path
            )
            self._dataframe = get_table_from_csv_with_header_with_encoding_detection(
                relative_filename=file_path,
                custom_header=custom_header,
            )

        # Convert numeric columns to appropriate types
        self._dataframe = self._convert_numeric_columns(
            self._dataframe
        )

        return self._dataframe

    def _convert_numeric_columns(
        self, df: DataFrame
    ) -> DataFrame:
        """
        Convert numeric columns from strings to appropriate numeric types.

        Args:
            df: DataFrame to convert

        Returns:
            DataFrame with numeric columns converted
        """
        for col in df.columns:
            # Try to convert to numeric, but only if all values can be converted
            try:
                df[col] = pd.to_numeric(
                    df[col]
                )
            except (
                ValueError,
                TypeError,
            ):
                # Keep as is if conversion fails
                pass

        return df

    def get_dataframe(
        self,
    ) -> DataFrame:
        """
        Get the currently loaded DataFrame.

        Returns:
            The current DataFrame or None if no file is loaded
        """
        if self._dataframe is None:
            raise ValueError(
                "No CSV file has been loaded. Use load_csv() first."
            )
        return self._dataframe

    @staticmethod
    def read_csv_files_from_directory(
        directory_path: Union[
            str, Path
        ],
        file_extension: str = ".csv",
    ) -> Dict[str, DataFrame]:
        """
        Read all CSV files from a directory and return a dictionary of DataFrames.

        Args:
            directory_path: Path to the directory
            file_extension: The file extension to look for (default is ".csv")

        Returns:
            Dictionary with file names (without extension) as keys and DataFrames as values
        """
        dir_path = str(directory_path)
        result = {}

        # Get list of CSV files in the directory (non-recursive)
        for file in os.listdir(
            dir_path
        ):
            file_path = os.path.join(
                dir_path, file
            )
            if os.path.isfile(
                file_path
            ) and file.endswith(
                file_extension
            ):
                # Get file name without extension as the key
                file_name = (
                    os.path.splitext(
                        file
                    )[0]
                )

                # Read CSV file and convert numeric columns
                df = pd.read_csv(
                    file_path
                )

                # Try to convert numeric columns
                for col in df.columns:
                    try:
                        df[col] = (
                            pd.to_numeric(
                                df[col]
                            )
                        )
                    except (
                        ValueError,
                        TypeError,
                    ):
                        pass

                result[file_name] = df

        return result

    # ---- CSV Writing Methods ----

    def save_csv(
        self,
        file_path: Optional[
            Union[str, Path]
        ] = None,
        encoding: Optional[str] = None,
        index: bool = False,
    ) -> None:
        """
        Save the current DataFrame to a CSV file.

        Args:
            file_path: Path where to save the CSV file (uses self.file_path if None)
            encoding: Encoding to use (uses detected encoding if None)
            index: Whether to include the DataFrame index in the output
        """
        if self._dataframe is None:
            raise ValueError(
                "No DataFrame to save. Load or create a DataFrame first."
            )

        output_path = (
            file_path
            if file_path
            else self.file_path
        )
        if output_path is None:
            raise ValueError(
                "No file path provided and no default file path set."
            )

        # Create directory if it doesn't exist
        directory = os.path.dirname(
            output_path
        )
        if (
            directory
            and not os.path.exists(
                directory
            )
        ):
            os.makedirs(directory)

        # Save using the appropriate function
        write_dataframe_to_csv_file(
            dataframe=self._dataframe,
            csv_file_name_and_path=output_path,
            encoding=(
                encoding
                if encoding
                else (
                    self._encoding
                    or UTF_8_ENCODING_NAME
                )
            ),
            index=index,
        )

    @staticmethod
    def write_dataframes_to_csv_files(
        dataframes: Dict[
            str, DataFrame
        ],
        output_directory: Union[
            str, Path
        ],
        encoding: str = UTF_8_ENCODING_NAME,
        index: bool = False,
    ) -> None:
        """
        Write a dictionary of DataFrames to CSV files.

        Args:
            dataframes: Dictionary with keys as filenames and values as DataFrames
            output_directory: Directory where to save the CSV files
            encoding: Encoding to use for the files
            index: Whether to include the DataFrame index in the output
        """
        write_dataframe_dictionary_to_csv_files(
            dataframe_dictionary=dataframes,
            csv_files_folder=output_directory,
            encoding=encoding,
            index=index,
        )

    @staticmethod
    def export_list_to_csv(
        output_path: Union[str, Path],
        data: List[str],
        encoding: str = UTF_8_ENCODING_NAME,
    ) -> None:
        """
        Export a list of strings to a CSV file.

        Args:
            output_path: Path where to save the CSV file
            data: List of strings to write, one per row
            encoding: Encoding to use for the file
        """
        export_list_of_strings_to_csv(
            output_file_path=output_path,
            list_of_strings=data,
            encoding=encoding,
        )

    @staticmethod
    def export_dictionary_to_csv(
        output_path: Union[str, Path],
        data: Dict[str, List[Any]],
        encoding: str = UTF_8_ENCODING_NAME,
    ) -> None:
        """
        Export a dictionary representation of a table to a CSV file.

        Args:
            output_path: Path where to save the CSV file
            data: Dictionary with column names as keys and lists of values as values
            encoding: Encoding to use for the file
        """
        # Create DataFrame directly for consistent handling
        df = pd.DataFrame(data)

        # Create directory if it doesn't exist
        directory = os.path.dirname(
            output_path
        )
        if (
            directory
            and not os.path.exists(
                directory
            )
        ):
            os.makedirs(directory)

        # Write to CSV
        df.to_csv(
            path_or_buf=output_path,
            sep=",",
            quotechar='"',
            index=False,
            quoting=csv.QUOTE_ALL,
            escapechar="\\",
            encoding=encoding,
        )

    # ---- CSV Analysis Methods ----

    @staticmethod
    def summarize_csv(
        csv_file_path: Union[str, Path]
    ) -> DataFrame:
        """
        Generate a summary of a CSV file.

        Args:
            csv_file_path: Path to the CSV file to summarize

        Returns:
            DataFrame with summary information
        """
        return summarize_csv(
            csv_file_path
        )

    @staticmethod
    def summarize_directory(
        directory_path: Union[
            str, Path
        ],
        file_extension: str = ".csv",
        recursive: bool = False,
    ) -> DataFrame:
        """
        Generate summaries for all CSV files in a directory.

        Args:
            directory_path: Path to the directory containing CSV files
            file_extension: The file extension to look for (default is ".csv")
            recursive: Whether to search subdirectories (default is False)

        Returns:
            DataFrame with summary information for all CSV files
        """
        dir_path = str(directory_path)

        # Get list of CSV files in the directory (non-recursive)
        csv_files = []
        for file in os.listdir(
            dir_path
        ):
            file_path = os.path.join(
                dir_path, file
            )
            if os.path.isfile(
                file_path
            ) and file.endswith(
                file_extension
            ):
                csv_files.append(
                    file_path
                )

        # Create empty summary DataFrame
        summary_columns = [
            "file_name",
            "number_of_rows",
            "number_of_columns",
            "parent_directory",
        ]
        summary_df = pd.DataFrame(
            columns=summary_columns
        )

        # Process each file
        for file_path in csv_files:
            file_summary = (
                summarize_csv(file_path)
            )
            summary_df = pd.concat(
                [
                    summary_df,
                    file_summary,
                ],
                ignore_index=True,
            )

        return summary_df

    @staticmethod
    def detailed_summary(
        csv_file_path: Union[str, Path]
    ) -> Dict[str, Any]:
        """
        Generate a detailed summary of a CSV file including column statistics.

        Args:
            csv_file_path: Path to the CSV file to analyze

        Returns:
            Dictionary containing detailed summary information
        """
        return generate_detailed_csv_summary(
            csv_file_path
        )

    # ---- DataFrame Manipulation Methods ----

    def set_dataframe(
        self, dataframe: DataFrame
    ) -> None:
        """
        Set the current DataFrame.

        Args:
            dataframe: The DataFrame to set
        """
        self._dataframe = dataframe

    # ---- Utility Methods ----

    @staticmethod
    def detect_encoding(
        file_path: Union[str, Path]
    ) -> str:
        """
        Detect the encoding of a file.

        Args:
            file_path: Path to the file

        Returns:
            Detected encoding
        """
        return detect(file_path)

    @staticmethod
    def convert_to_files_object(
        file_path: Union[str, Path]
    ) -> Files:
        """
        Convert a path string or Path to a Files object.

        Args:
            file_path: Path string or Path object

        Returns:
            Files object
        """
        return Files(file_path)

    @staticmethod
    def convert_to_folders_object(
        directory_path: Union[str, Path]
    ) -> Folders:
        """
        Convert a path string or Path to a Folders object.

        Args:
            directory_path: Path string or Path object

        Returns:
            Folders object
        """
        return Folders(directory_path)
