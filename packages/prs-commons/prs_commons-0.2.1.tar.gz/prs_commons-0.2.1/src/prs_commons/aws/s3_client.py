"""S3 Client module for AWS S3 storage.

This module provides a thread-safe singleton S3 client that can be used across
the application. It uses boto3 for AWS S3 operations and supports configuration
via environment variables.

Environment Variables:
    REGION: AWS region name (e.g., 'us-east-1')
    BUCKET_ACCESS_KEY_ID: AWS access key ID
    BUCKET_SECRET_ACCESS_KEY: AWS secret access key
"""

import base64
import io
import logging
import os
from threading import Lock
from typing import Any, Dict, Optional, Type, TypeVar

import boto3
from boto3.session import NoCredentialsError
from botocore.client import BaseClient
from botocore.exceptions import ClientError
from typing_extensions import override

from prs_commons.storage.base import StorageClient

# Type aliases
S3Response = Dict[str, Any]

# Type variables for generic class methods
T = TypeVar("T", bound="S3Client")

# Set up logger
logger = logging.getLogger(__name__)


class S3Client(StorageClient):
    """Thread-safe singleton client for AWS S3 operations.

    This client provides a simple interface to interact with AWS S3 using boto3.
    It implements the singleton pattern to ensure only one instance exists.
    """

    _instance: Optional["S3Client"] = None
    _lock: Lock = Lock()

    def __new__(cls: Type[T]) -> T:
        """Create or return the singleton instance of S3Client."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(S3Client, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance  # type: ignore

    def __init__(self) -> None:
        """Initialize the S3 client with configuration from environment variables."""
        if getattr(self, "_initialized", False):
            return

        # Initialize session and client
        self._session = boto3.Session(
            region_name=os.getenv("REGION"),
            aws_access_key_id=os.getenv("BUCKET_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("BUCKET_SECRET_ACCESS_KEY"),
        )
        self._client: Optional[BaseClient] = None
        self._initialized = True

    @property
    @override
    def client(self) -> BaseClient:
        """Get the boto3 S3 client instance.

        Returns:
            The boto3 S3 client instance.

        Raises:
            RuntimeError: If the S3 client cannot be initialized.
        """
        if self._client is None:
            try:
                self._client = self._session.client("s3")
            except Exception as e:
                raise RuntimeError("Failed to initialize S3 client") from e
        return self._client

    @override
    def upload_file(
        self, file_path: str, bucket: str, key: str, **kwargs: Any
    ) -> S3Response:
        """Upload a file to an S3 bucket.

        Args:
            file_path: Path to the file to upload
            bucket: Target S3 bucket name
            key: S3 object key (path in the bucket)
            **kwargs: Additional arguments to pass to boto3 upload_file

        Returns:
            S3Response: Dictionary containing status and operation details

        Raises:
            ClientError: If the upload fails
        """
        try:
            self.client.upload_file(file_path, bucket, key, **kwargs)
            return {"status": "success", "bucket": bucket, "key": key}
        except (ClientError, NoCredentialsError) as e:
            logger.error(
                "Failed to upload file %s to s3://%s/%s: %s",
                file_path,
                bucket,
                key,
                str(e),
            )
            raise

    @override
    def download_file(
        self, bucket: str, key: str, file_path: str, **kwargs: Any
    ) -> bool:
        """Download a file from an S3 bucket to the local filesystem.

        Args:
            bucket: Source S3 bucket name
            key: S3 object key (path in the bucket)
            file_path: Local filesystem path where the file will be saved.
                     Must include the target filename and extension.
                     Example: '/path/to/destination/filename.ext'
                     The parent directory must exist and be writable.
            **kwargs: Additional arguments to pass to boto3 download_file

        Returns:
            bool: True if download was successful

        Raises:
            FileNotFoundError: If the file doesn't exist in S3 or local path is invalid
            PermissionError: If there are permission issues with S3 or local filesystem
            botocore.exceptions.ClientError: For other S3-specific errors
            IOError: If there are issues writing to the local filesystem

        Example:
            >>> s3 = S3Client()
            >>> success = s3.download_file(
            ...     bucket='my-bucket',
            ...     key='folder/file.txt',
            ...     file_path='/local/path/to/save/file.txt'
            ... )
            >>> if success:
            ...     print("File downloaded successfully")
        """
        try:
            self.client.download_file(bucket, key, file_path, **kwargs)
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code == "404":
                raise FileNotFoundError(f"File not found: s3://{bucket}/{key}") from e
            if error_code in ["403", "AccessDenied"]:
                raise PermissionError(
                    f"Access denied to file: s3://{bucket}/{key}"
                ) from e
            raise  # Re-raise other ClientError instances

    @override
    def delete_object(self, bucket: str, key: str) -> S3Response:
        """Delete an object from an S3 bucket.

        Args:
            bucket: S3 bucket name
            key: S3 object key to delete

        Returns:
            S3Response: Dictionary containing status and operation details
        """
        try:
            response = self.client.delete_object(Bucket=bucket, Key=key)
            return {
                "status": "success",
                "response": response,
                "bucket": bucket,
                "key": key,
            }
        except ClientError as e:
            return {
                "status": "error",
                "error": str(e),
                "bucket": bucket,
                "key": key,
            }

    @override
    def generate_presigned_url(
        self,
        bucket: str,
        key: str,
        operation: str = "get_object",
        expiration: int = 3600,
        **kwargs: Any,
    ) -> Optional[str]:
        """Generate a pre-signed URL for an S3 object.

        Args:
            bucket: S3 bucket name
            key: S3 object key (path in the bucket)
            operation: The S3 operation to allow with this URL.
                     Common values: 'get_object', 'put_object', 'delete_object'
            expiration: Time in seconds until the URL expires (default: 1 hour)
            **kwargs: Additional parameters to pass to the S3 operation

        Returns:
            Optional[str]: The pre-signed URL as a string,
            or None if credentials are invalid

        Example:
            # Generate a URL to upload a file
            >>> upload_url = s3.generate_presigned_url(
            ...     bucket='my-bucket',
            ...     key='uploads/file.txt',
            ...     operation='put_object',
            ...     ContentType='text/plain'
            ... )

            # Generate a URL to download a file
            >>> download_url = s3.generate_presigned_url(
            ...     bucket='my-bucket',
            ...     key='downloads/file.txt',
            ...     operation='get_object',
            ...     ResponseContentType='application/octet-stream'
            ... )
        """
        params = {"Bucket": bucket, "Key": key, **kwargs}

        url: str = self.client.generate_presigned_url(
            ClientMethod=operation, Params=params, ExpiresIn=expiration
        )
        return url

    @override
    def generate_upload_url(
        self,
        bucket: str,
        key: str,
        expiration: int = 3600,
        **kwargs: Any,
    ) -> Optional[str]:
        """Generate a pre-signed URL for uploading a file to S3.

        This is a convenience wrapper around generate_presigned_url for uploads.

        Args:
            bucket: S3 bucket name
            key: S3 object key where the file will be stored
            expiration: Time in seconds until the URL expires (default: 1 hour)
            **kwargs: Additional parameters to pass to the S3 put_object operation
                Common parameters:
                - ContentType: The content type of the file (e.g., 'image/jpeg')
                - ACL: Access control for the file (e.g., 'private', 'public-read')
                - Metadata: Dictionary of metadata to store with the object

        Returns:
            Optional[str]: The pre-signed URL as a string,
            or None if credentials are invalid

        Example:
            >>> upload_url = s3.generate_upload_url(
            ...     bucket='my-bucket',
            ...     key='uploads/file.jpg',
            ...     ContentType='image/jpeg',
            ...     ACL='private',
            ...     Metadata={
            ...         'custom': 'value'
            ...     }
            ... )
        """
        # Convert ContentType to proper case if provided
        if "contenttype" in kwargs:
            kwargs["ContentType"] = kwargs.pop("contenttype")

        # Ensure ContentType is set if not provided
        if "ContentType" not in kwargs:
            # Try to determine content type from file extension
            if "." in key:
                ext = key.split(".")[-1].lower()
                if ext in {"jpg", "jpeg"}:
                    kwargs["ContentType"] = "image/jpeg"
                elif ext == "png":
                    kwargs["ContentType"] = "image/png"
                elif ext == "pdf":
                    kwargs["ContentType"] = "application/pdf"
                elif ext == "txt":
                    kwargs["ContentType"] = "text/plain"
            else:
                # Default to binary data if type can't be determined
                kwargs["ContentType"] = "application/octet-stream"

        # Set default ACL if not provided
        if "ACL" not in kwargs and "acl" not in kwargs:
            # Don't set default ACL as it's causing signature issues
            # The bucket's default ACL will be used instead
            pass

        return self.generate_presigned_url(
            bucket=bucket,
            key=key,
            operation="put_object",
            expiration=expiration,
            **kwargs,
        )

    @override
    def generate_download_url(
        self,
        bucket: str,
        key: str,
        expiration: int = 3600,
        **kwargs: Any,
    ) -> Optional[str]:
        """Generate a pre-signed URL for downloading a file from S3.

        This is a convenience wrapper around generate_presigned_url for downloads.

        Args:
            bucket: S3 bucket name
            key: S3 object key of the file to download
            expiration: Time in seconds until the URL expires (default: 1 hour)
            **kwargs: Additional parameters to pass to the S3 get_object operation

        Returns:
            Optional[str]: The pre-signed URL as a string,
            or None if credentials are invalid

        Example:
            >>> download_url = s3.generate_download_url(
            ...     bucket='my-bucket',
            ...     key='downloads/file.txt',
            ...     ResponseContentType='application/pdf',
            ...     ResponseContentDisposition='attachment; filename=report.pdf'
            ... )
        """
        return self.generate_presigned_url(
            bucket=bucket,
            key=key,
            operation="get_object",
            expiration=expiration,
            **kwargs,
        )

    @override
    def download_as_base64(
        self,
        bucket: str,
        key: str,
        check_exists: bool = True,
        **kwargs: Any,
    ) -> Optional[str]:
        """Download a file from S3 and return its contents as a base64-encoded string.

        This method is useful when you need to work with the file contents
        directly in memory without saving to disk, such as when sending files
        in API responses or processing file contents in memory.

        Args:
            bucket: Name of the S3 bucket
            key: S3 object key (path in the bucket)
            check_exists: If True, verify the file exists before downloading
            **kwargs: Additional arguments to pass to boto3 download_fileobj

        Returns:
            Base64-encoded string of the file contents

        Raises:
            FileNotFoundError: If the file doesn't exist
            PermissionError: If there are permission issues
            botocore.exceptions.ClientError: For S3-specific errors
            Exception: For any other unexpected errors

        Example:
            >>> # Download a file as base64
            >>> file_data = s3.download_as_base64(
            ...     bucket='my-bucket',
            ...     key='documents/report.pdf',
            ... )
            >>> if file_data:
            ...     # Use the base64 data (e.g., embed in HTML, send in API response)
            ...     print(f"File size: {len(file_data)} bytes")
        """
        if check_exists:
            # Check if object exists first
            try:
                self.client.head_object(Bucket=bucket, Key=key, **kwargs)
            except ClientError as e:
                if e.response.get("Error", {}).get("Code") == "404":
                    raise FileNotFoundError(
                        f"File not found: s3://{bucket}/{key}"
                    ) from e
                if e.response.get("Error", {}).get("Code") in ["403", "AccessDenied"]:
                    raise PermissionError(
                        f"Access denied to file: s3://{bucket}/{key}"
                    ) from e
                raise  # Re-raise other ClientError instances

        # Download file to in-memory buffer
        buffer = io.BytesIO()
        self.client.download_fileobj(bucket, key, buffer, **kwargs)
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode("utf-8")
