"""Tests for AWS S3 client functionality with async support."""

import base64
import os
import tempfile
from pathlib import Path
from typing import List
from unittest.mock import patch

import pytest
import requests
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Import after setting up environment variables
from prs_commons.aws.s3_client import S3Client
from prs_commons.storage.base import StorageClient

# Configure pytest
pytestmark = [pytest.mark.asyncio]

# Load environment variables from .env file in the project root
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)

    # Debug: Print loaded environment variables (without sensitive data)
    print("\nLoaded environment variables:")
    print(f"BUCKET_NAME: {os.getenv('BUCKET_NAME')}")
    print(f"REGION: {os.getenv('REGION')}")
    print(
        "BUCKET_ACCESS_KEY_ID:",
        "set" if os.getenv("BUCKET_ACCESS_KEY_ID") else "not set",
    )
    print(
        "BUCKET_SECRET_ACCESS_KEY:",
        "set" if os.getenv("BUCKET_SECRET_ACCESS_KEY") else "not set",
    )
    print()

# Test configuration
TEST_BUCKET = os.getenv("BUCKET_NAME")
TEST_PREFIX = "test-files/"
TEST_FILE_CONTENT = b"This is a test file for S3 client testing"


class TestS3Client:
    """Test cases for S3Client."""

    s3: StorageClient
    test_files: List[str] = []

    @classmethod
    def setup_class(self):
        """Set up test environment before any tests run."""
        # Skip if test bucket is not configured
        if not TEST_BUCKET:
            pytest.skip("BUCKET_NAME environment variable not set")

        # Initialize the S3 client
        self.s3 = S3Client()
        self.test_files = []

        # Verify we can connect to S3
        try:
            self.s3.client.head_bucket(Bucket=TEST_BUCKET)
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code == "404":
                pytest.skip(f"Test bucket {TEST_BUCKET} does not exist")
            elif error_code in ("403", "AccessDenied"):
                pytest.skip(f"Access denied to test bucket {TEST_BUCKET}")
            else:
                pytest.skip(f"Failed to access test bucket {TEST_BUCKET}: {str(e)}")

    def setup_method(self):
        """Run before each test method."""
        # Reset test files for each test
        self.test_files = []

    @pytest.fixture(autouse=True)
    async def cleanup_after_test(self):
        """Clean up test files after each test."""
        yield  # This is where the test runs
        await self.cleanup_test_files()

    async def cleanup_test_files(self):
        """Clean up test files from S3 after tests complete."""
        if not hasattr(self, "test_files") or not TEST_BUCKET or not self.test_files:
            return

        # Create a copy of the list to avoid modifying it during iteration
        files_to_clean = list(self.test_files)
        # Clear the list first to prevent issues if cleanup fails
        self.test_files.clear()

        for key in files_to_clean:
            try:
                await self.s3.delete_object(bucket=TEST_BUCKET, key=key)
            except Exception as e:
                print(f"Warning: Failed to delete {key}: {str(e)}")
                # Re-add to test_files if cleanup failed so it can be retried
                self.test_files.append(key)

    async def _upload_test_file(self, key_suffix: str = "") -> str:
        """Upload a test file to S3 and return its key."""
        key = f"{TEST_PREFIX}test_file_{key_suffix or 'temp'}.txt"
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(TEST_FILE_CONTENT)
            temp_file_path = temp_file.name

        try:
            await self.s3.upload_file(
                file_path=temp_file_path, bucket=TEST_BUCKET, key=key
            )
            self.test_files.append(key)
            return key
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    async def test_upload_download_file_WithValidFile_ShouldSucceed(self):
        """Test uploading and downloading a file to/from S3."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(TEST_FILE_CONTENT)
            temp_file_path = temp_file.name

        key = f"{TEST_PREFIX}test_upload_download.txt"
        self.test_files.append(key)
        download_path = f"{temp_file_path}.downloaded"

        try:
            # Upload the file
            result = await self.s3.upload_file(
                file_path=temp_file_path, bucket=TEST_BUCKET, key=key
            )
            assert result.get("status") == "success", "Upload should be successful"
            assert result.get("bucket") == TEST_BUCKET, "Bucket should match"
            assert result.get("key") == key, "Key should match"

            # Download the file
            await self.s3.download_file(
                bucket=TEST_BUCKET, key=key, file_path=download_path
            )

            # Verify the downloaded content
            with open(download_path, "rb") as f:
                downloaded_content = f.read()
            assert (
                downloaded_content == TEST_FILE_CONTENT
            ), "Downloaded content doesn't match"

        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            if os.path.exists(download_path):
                os.unlink(download_path)
            self.cleanup_test_files()

    async def test_download_as_base64_WithExistingFile_ShouldReturnBase64Content(self):
        """Test that downloading an existing file as
        base64 returns the correct content."""
        # Upload a test file
        key = await self._upload_test_file("base64_test")

        # Test with check_exists=True
        base64_content = await self.s3.download_as_base64(
            bucket=TEST_BUCKET, key=key, check_exists=True
        )
        assert base64_content is not None
        assert base64.b64decode(base64_content).decode() == TEST_FILE_CONTENT.decode()

        # Test with check_exists=False
        base64_content = await self.s3.download_as_base64(
            bucket=TEST_BUCKET, key=key, check_exists=False
        )
        assert base64_content is not None
        assert base64.b64decode(base64_content).decode() == TEST_FILE_CONTENT.decode()

    async def test_download_as_base64_WithNonExistentFile_ShouldRaiseFileNotFound(self):
        """Test that downloading a non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            await self.s3.download_as_base64(
                bucket=TEST_BUCKET, key="non_existent_file.txt"
            )

    async def test_download_as_base64_WhenDownloadFails_ShouldRaiseClientError(self):
        """Test that ClientError is raised when download fails with S3 error."""
        # Upload a test file
        key = await self._upload_test_file("error_test")

        # Mock the download_fileobj to raise ClientError
        with patch.object(
            self.s3.client,
            "download_fileobj",
            side_effect=ClientError({}, "HeadObject"),
        ):
            with pytest.raises(ClientError):
                await self.s3.download_as_base64(
                    bucket=TEST_BUCKET, key=key, check_exists=False
                )

    async def test_upload_via_presigned_url_WithValidFile_ShouldUploadAndDownloadSuccessfully(  # noqa: E501
        self,
    ):
        """Test complete workflow with presigned URL including upload,
        download, and delete operations."""
        # Generate a presigned URL for upload
        key = f"{TEST_PREFIX}presigned_upload_test.txt"
        upload_url = self.s3.generate_upload_url(
            bucket=TEST_BUCKET, key=key, ContentType="text/plain"
        )

        # Ensure we got a string URL
        assert isinstance(upload_url, str), "Upload URL should be a string"
        assert upload_url.startswith("https://"), "Upload URL should be an HTTPS URL"

        # Create a session with retry
        session = requests.Session()
        session.mount("https://", requests.adapters.HTTPAdapter(max_retries=3))

        # Upload a file using the presigned URL
        response = session.put(
            upload_url,
            data=TEST_FILE_CONTENT,
            headers={"Content-Type": "text/plain"},
            timeout=10,
        )
        assert (
            response.status_code == 200
        ), f"Upload failed with status {response.status_code}: {response.text}"
        self.test_files.append(key)

        # Generate a presigned URL for download
        download_url = self.s3.generate_download_url(
            bucket=TEST_BUCKET, key=key, expiration=3600
        )
        assert download_url is not None, "Download URL should not be None"
        assert key in download_url, "Download URL should contain the key"

        # Download the file using the presigned URL
        response = session.get(download_url, timeout=10)
        assert (
            response.status_code == 200
        ), f"Download failed with status {response.status_code}"
        assert response.content == TEST_FILE_CONTENT, "Downloaded content doesn't match"

        # Verify the file exists and has the correct content type
        head = self.s3.client.head_object(Bucket=TEST_BUCKET, Key=key)
        assert (
            head["ResponseMetadata"]["HTTPStatusCode"] == 200
        ), "File should exist in S3"
        assert (
            head.get("ContentType") == "text/plain"
        ), f"Content type should be 'text/plain' but was {head.get('ContentType')}"

    async def test_delete_object_WithExistingFile_ShouldSucceed(self):
        """Test deleting an existing object from S3."""
        # Upload a test file
        key = await self._upload_test_file("delete_test")

        # Verify the file exists using the client directly since
        # head_object is not async in boto3
        head = self.s3.client.head_object(Bucket=TEST_BUCKET, Key=key)
        assert (
            head["ResponseMetadata"]["HTTPStatusCode"] == 200
        ), "File should exist before deletion"

        # Delete the file using our async method
        result = await self.s3.delete_object(bucket=TEST_BUCKET, key=key)
        assert (
            result.get("status") == "success"
        ), f"Delete operation should be successful, got: {result}"

        # Verify the file is deleted
        with pytest.raises(ClientError) as exc_info:
            self.s3.client.head_object(Bucket=TEST_BUCKET, Key=key)
        assert (
            exc_info.value.response["Error"]["Code"] == "404"
        ), "File should be deleted"
