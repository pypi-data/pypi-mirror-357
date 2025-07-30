import boto3  # type: ignore
import pandas as pd  # type: ignore
import logging
from tempfile import SpooledTemporaryFile
import sys

logger = logging.getLogger(__name__)


def resolve_dataset(
    dataset_path: str | None = None,
    dataset_buffer: bytes | None = None,
    bucket_type: str = "s3",
    dataset_format: str = "csv",
    chunk_size: int = 8192,
) -> pd.DataFrame:
    """
    Load a dataset from an S3 bucket as a pandas DataFrame.

    Args:
        dataset_path (str): Path to the dataset (s3://bucket-name/path/to/file.csv)
        dataset_buffer (bytes): Raw bytes of the dataset
        bucket_type (str): Type of bucket (only 's3' is supported)
        dataset_format (str): Format of the dataset (currently only supports 'csv')
        chunk_size (int): Size of chunks for downloading from S3 (default: 8192 bytes)

    Returns:
        pd.DataFrame: The loaded dataset as a pandas DataFrame

    Raises:
        ValueError: If the bucket_type is not 's3', dataset_format is not 'csv', or the path is invalid
        ClientError: If there's an error accessing the S3 bucket
        Exception: For other errors during loading
    """
    if bucket_type != "s3":
        raise ValueError(f"Unsupported bucket type: {bucket_type}")

    if dataset_format != "csv":
        raise ValueError(f"Unsupported dataset format: {dataset_format}")

    if dataset_path is None and dataset_buffer is None:
        raise ValueError("Dataset path or buffer must be provided")

    if dataset_buffer:
        # Use SpooledTemporaryFile for buffer data
        with SpooledTemporaryFile(max_size=1024 * 1024) as temp_file:  # 1MB threshold
            temp_file.write(dataset_buffer)
            temp_file.seek(0)
            return pd.read_csv(temp_file)

    if dataset_path:
        # Parse S3 path
        if not dataset_path.startswith("s3://"):
            raise ValueError(f"Invalid S3 path format: {dataset_path}")

        # Parse bucket and key from path
        path_without_prefix = dataset_path[5:]  # Remove 's3://'
        parts = path_without_prefix.split("/", 1)
        if len(parts) < 2:
            raise ValueError(f"Invalid S3 path format: {dataset_path}")

        bucket_name, key = parts

        # Initialize S3 client
        s3_client = boto3.client("s3")

        # Get file size for progress tracking
        try:
            response = s3_client.head_object(Bucket=bucket_name, Key=key)
            file_size = response["ContentLength"]
            logger.info(f"Downloading file: {key} (size: {file_size} bytes)")
        except Exception as e:
            logger.warning(f"Could not get file size for progress tracking: {e}")
            file_size = None

        # Download the file using chunked download with progress tracking
        with SpooledTemporaryFile(max_size=1024 * 1024) as temp_file:  # 1MB threshold
            try:
                # Use get_object for chunked download
                response = s3_client.get_object(Bucket=bucket_name, Key=key)
                stream = response["Body"]

                downloaded_bytes = 0
                last_progress_percent = -1  # Track last printed progress percentage

                while True:
                    chunk = stream.read(chunk_size)
                    if not chunk:
                        break

                    temp_file.write(chunk)
                    downloaded_bytes += len(chunk)

                    # Print progress only every 10% if file size is known
                    if file_size:
                        progress = (downloaded_bytes / file_size) * 100
                        current_progress_percent = (
                            int(progress // 10) * 10
                        )  # Round down to nearest 10%

                        if current_progress_percent > last_progress_percent:
                            sys.stdout.write(
                                f"\rDownload progress: {progress:.1f}% ({downloaded_bytes}/{file_size} bytes)"
                            )
                            sys.stdout.flush()
                            last_progress_percent = current_progress_percent

                if file_size:
                    print()  # New line after progress

                temp_file.seek(0)  # Reset file position to the beginning

                # Load the CSV into a pandas DataFrame
                df = pd.read_csv(temp_file)
                logger.info(
                    f"Successfully loaded dataset with {len(df)} rows and {len(df.columns)} columns"
                )

                return df

            except Exception as e:
                logger.error(f"Error downloading file from S3: {e}")
                raise
    else:
        raise ValueError("Could not resolve dataset from provided path or buffer.")
