import os
from typing import (
    Dict,
    List,
    Optional,
    Union,
)

import pandas as pd
from bclearer_interop_services.delimited_text.delimited_text_read import (
    get_table_from_csv_with_header_with_encoding_detection,
)


def summarize_csv(
    csv_file_path: str,
) -> pd.DataFrame:
    """
    Generate a summary of a CSV file.

    Args:
        csv_file_path: Path to the CSV file to summarize

    Returns:
        A pandas DataFrame with summary information including row count, column count, and file name
    """
    try:
        # Read the CSV file into a DataFrame with automatic encoding detection
        csv_data = get_table_from_csv_with_header_with_encoding_detection(
            csv_file_path,
        )

        # Clean the DataFrame by dropping completely empty rows
        csv_data = csv_data.dropna(
            how="all",
        ).reset_index(drop=True)

        # Calculate dimensions
        dim = csv_data.shape
        rows = dim[0]
        cols = dim[1]

        # Create a summary DataFrame
        summary_df = pd.DataFrame(
            {
                "number_of_columns": [
                    cols
                ],
                "number_of_rows": [
                    rows
                ],
                "file_name": [
                    os.path.basename(
                        csv_file_path
                    )
                ],
            }
        )

        return summary_df

    except Exception as e:
        # Create an error summary
        error_summary = pd.DataFrame(
            {
                "number_of_columns": [
                    0
                ],
                "number_of_rows": [0],
                "file_name": [
                    os.path.basename(
                        csv_file_path
                    )
                ],
                "error": [str(e)],
            }
        )

        return error_summary


def summarize_csv_directory(
    directory_path: str,
    file_extension: str = ".csv",
) -> pd.DataFrame:
    """
    Generate summaries for all CSV files in a directory.

    Args:
        directory_path: Path to the directory containing CSV files
        file_extension: The file extension to look for (default is ".csv")

    Returns:
        A pandas DataFrame with summary information for all CSV files in the directory
    """
    # Initialize an empty DataFrame for the summaries
    summary_df = pd.DataFrame()

    print(
        f"\n------Reading directory {directory_path}---------\n"
    )

    # Walk through the directory
    for parent_dir, _, files in os.walk(
        directory_path
    ):
        for file_name in files:
            _, extension = (
                os.path.splitext(
                    file_name
                )
            )

            if (
                extension.lower()
                == file_extension.lower()
            ):
                print(
                    f"*********Summarising file {file_name} in {parent_dir}**********\n"
                )

                file_path = (
                    os.path.join(
                        parent_dir,
                        file_name,
                    )
                )
                try:
                    # Get summary for this CSV file
                    file_summary = (
                        summarize_csv(
                            file_path
                        )
                    )

                    # Add directory information
                    file_summary[
                        "parent_directory"
                    ] = parent_dir

                    # Append to the main summary
                    summary_df = pd.concat(
                        [
                            summary_df,
                            file_summary,
                        ]
                    )

                except Exception as e:
                    print(
                        f"Error processing file {file_name}: {str(e)}"
                    )

    return summary_df


def generate_detailed_csv_summary(
    csv_file_path: str,
) -> Dict:
    """
    Generate a detailed summary of a CSV file including column statistics.

    Args:
        csv_file_path: Path to the CSV file to analyze

    Returns:
        A dictionary containing detailed summary information
    """
    try:
        # Read the CSV file
        csv_data = get_table_from_csv_with_header_with_encoding_detection(
            csv_file_path,
        )

        # Basic file info
        file_name = os.path.basename(
            csv_file_path
        )
        file_size = os.path.getsize(
            csv_file_path
        )
        file_path = os.path.dirname(
            csv_file_path
        )

        # Basic statistics
        row_count = len(csv_data)
        column_count = len(
            csv_data.columns
        )
        column_names = list(
            csv_data.columns
        )

        # Column-level statistics
        column_stats = {}
        for column in csv_data.columns:
            # Get data type
            data_type = str(
                csv_data[column].dtype
            )

            # Count non-null values
            non_null_count = csv_data[
                column
            ].count()
            null_percentage = (
                (
                    (
                        row_count
                        - non_null_count
                    )
                    / row_count
                )
                * 100
                if row_count > 0
                else 0
            )

            # Count unique values
            unique_count = csv_data[
                column
            ].nunique()

            column_stats[column] = {
                "data_type": data_type,
                "non_null_count": int(
                    non_null_count
                ),
                "null_percentage": round(
                    null_percentage, 2
                ),
                "unique_count": int(
                    unique_count
                ),
                "sample_values": csv_data[
                    column
                ]
                .dropna()
                .head(3)
                .tolist(),
            }

            # Add numeric statistics if applicable
            if pd.api.types.is_numeric_dtype(
                csv_data[column]
            ):
                column_stats[
                    column
                ].update(
                    {
                        "min": (
                            float(
                                csv_data[
                                    column
                                ].min()
                            )
                            if not csv_data[
                                column
                            ].empty
                            else None
                        ),
                        "max": (
                            float(
                                csv_data[
                                    column
                                ].max()
                            )
                            if not csv_data[
                                column
                            ].empty
                            else None
                        ),
                        "mean": (
                            float(
                                csv_data[
                                    column
                                ].mean()
                            )
                            if not csv_data[
                                column
                            ].empty
                            else None
                        ),
                    }
                )

        # Compile the summary dictionary
        summary = {
            "file_info": {
                "file_name": file_name,
                "file_path": file_path,
                "file_size_bytes": file_size,
            },
            "data_summary": {
                "row_count": row_count,
                "column_count": column_count,
                "column_names": column_names,
            },
            "column_statistics": column_stats,
        }

        return summary

    except Exception as e:
        return {
            "error": str(e),
            "file_name": os.path.basename(
                csv_file_path
            ),
        }
