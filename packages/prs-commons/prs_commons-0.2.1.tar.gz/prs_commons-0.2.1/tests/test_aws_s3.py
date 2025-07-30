"""Tests for AWS S3 client functionality."""

import base64
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import requests
from botocore.exceptions import ClientError
from dotenv import load_dotenv

from prs_commons.aws.s3_client import S3Client
from prs_commons.storage.base import StorageClient

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


class TestS3Client(unittest.TestCase):
    """Test cases for S3Client."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment before any tests run."""
        # Set AWS environment variables from S3_ prefixed ones if they exist
        if not os.getenv("BUCKET_ACCESS_KEY_ID") and os.getenv("BUCKET_ACCESS_KEY_ID"):
            os.environ["BUCKET_ACCESS_KEY_ID"] = os.getenv("BUCKET_ACCESS_KEY_ID")
        if not os.getenv("BUCKET_SECRET_ACCESS_KEY") and os.getenv(
            "BUCKET_SECRET_ACCESS_KEY"
        ):
            os.environ["BUCKET_SECRET_ACCESS_KEY"] = os.getenv(
                "BUCKET_SECRET_ACCESS_KEY"
            )
        if not os.getenv("REGION") and os.getenv("REGION"):
            os.environ["REGION"] = os.getenv("REGION")

        # Check for required AWS credentials
        required_vars = [
            "BUCKET_ACCESS_KEY_ID",
            "BUCKET_SECRET_ACCESS_KEY",
            "REGION",
            "BUCKET_NAME",
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise unittest.SkipTest(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

        if not TEST_BUCKET:
            raise unittest.SkipTest("BUCKET_NAME environment variable not set")

        # Initialize the S3 client
        cls.s3: StorageClient = S3Client()
        cls.test_files = []

        # Verify we can connect to S3
        try:
            cls.s3.client.head_bucket(Bucket=TEST_BUCKET)
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code == "404":
                raise unittest.SkipTest(f"Test bucket {TEST_BUCKET} does not exist")
            elif error_code in ("403", "AccessDenied"):
                raise unittest.SkipTest(f"Access denied to test bucket {TEST_BUCKET}")
            else:
                raise unittest.SkipTest(
                    f"Failed to access test bucket {TEST_BUCKET}: {str(e)}"
                )

    @classmethod
    def tearDownClass(cls):
        """Clean up test files from S3 after all tests complete."""
        if not hasattr(cls, "test_files") or not TEST_BUCKET:
            return

        for key in cls.test_files:
            try:
                cls.s3.delete_object(bucket=TEST_BUCKET, key=key)
            except Exception as e:
                print(f"Warning: Failed to delete {key}: {str(e)}")
                pass

    def _upload_test_file(self, key_suffix: str = "") -> str:
        """Upload a test file to S3 and return its key."""
        key = f"{TEST_PREFIX}test_file_{key_suffix or id(self)}.txt"
        self.s3.client.put_object(Bucket=TEST_BUCKET, Key=key, Body=TEST_FILE_CONTENT)
        self.test_files.append(key)
        return key

    def test_upload_file_and_download_file_WithValidFile_ShouldSucceed(self):
        """Test that uploading and then downloading a file works correctly."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(TEST_FILE_CONTENT)

        try:
            # Upload the file
            key = f"{TEST_PREFIX}test_upload_download.txt"
            self.test_files.append(key)

            # Test upload
            result = self.s3.upload_file(temp_file_path, TEST_BUCKET, key)
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["bucket"], TEST_BUCKET)
            self.assertEqual(result["key"], key)

            # Test download
            download_path = f"{temp_file_path}_downloaded"
            success = self.s3.download_file(TEST_BUCKET, key, download_path)
            self.assertTrue(success)

            # Verify content
            with open(download_path, "rb") as f:
                content = f.read()
                self.assertEqual(content, TEST_FILE_CONTENT)

        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            if os.path.exists(download_path):
                os.unlink(download_path)

    def test_download_as_base64_WithExistingFile_ShouldReturnBase64Content(self):
        """Test that downloading an existing file
        as base64 returns the correct content."""
        # Upload a test file
        key = self._upload_test_file("base64_test")

        # Test download as base64
        result = self.s3.download_as_base64(TEST_BUCKET, key)

        # Verify result
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)

        # Decode and verify content
        decoded = base64.b64decode(result)
        self.assertEqual(decoded, TEST_FILE_CONTENT)

    def test_download_as_base64_WithNonExistentFile_ShouldRaiseFileNotFound(self):
        """Test that downloading a non-existent file raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            self.s3.download_as_base64(TEST_BUCKET, "non-existent-file.txt")

    def test_download_as_base64_WhenDownloadFails_ShouldRaiseClientError(self):
        """Test that ClientError is raised when download fails with S3 error."""
        # Create a test file first
        key = self._upload_test_file("error_test")

        # Mock the download_fileobj to raise an error, but let head_object succeed
        with patch.object(
            self.s3.client,
            "download_fileobj",
            side_effect=ClientError(
                error_response={"Error": {"Code": "403", "Message": "Forbidden"}},
                operation_name="DownloadFile",
            ),
        ):
            with self.assertRaises(ClientError):
                self.s3.download_as_base64(TEST_BUCKET, key, check_exists=True)

    def test_upload_via_presigned_url_WithValidFile_ShouldUploadAndDownloadSuccessfully(
        self,
    ):
        """Test complete workflow with presigned URL
        including upload, download, and delete operations."""
        # Setup
        svg_key = f"{TEST_PREFIX}test_upload_{id(self)}.jpg"
        svg_path = os.path.join(os.path.dirname(__file__), "resource", "test.jpg")

        # 1. Read the file content first
        with open(svg_path, "rb") as f:
            original_content = f.read()

        # 2. Generate presigned URL for upload with required parameters
        upload_url = self.s3.generate_upload_url(
            bucket=TEST_BUCKET, key=svg_key, ContentType="image/jpeg"
        )
        print("\nGenerated upload URL:", upload_url)
        self.assertIsNotNone(upload_url, "Upload URL should not be None")
        self.assertIn(svg_key, upload_url, "Upload URL should contain the key")
        self.assertIn("X-Amz-Signature", upload_url, "Upload URL should be signed")

        # 3. Upload the file using presigned URL
        try:
            # Create a session to reuse the connection
            session = requests.Session()
            session.verify = False  # Disable SSL verification
            session.mount("https://", requests.adapters.HTTPAdapter(max_retries=3))

            # Upload the file content with the required content type
            response = session.put(
                upload_url,
                data=original_content,
                headers={"Content-Type": "image/jpeg"},
            )

            response.raise_for_status()

            # 4. Verify the file was uploaded
            head = self.s3.client.head_object(Bucket=TEST_BUCKET, Key=svg_key)
            self.assertEqual(
                head["ResponseMetadata"]["HTTPStatusCode"],
                200,
                "File should exist in S3",
            )
            self.assertEqual(
                head["ContentType"], "image/jpeg", "Content type should be preserved"
            )

            # 5. Generate and test download URL
            download_url = self.s3.generate_download_url(
                bucket=TEST_BUCKET, key=svg_key, ResponseContentType="image/jpeg"
            )
            self.assertIsNotNone(download_url, "Download URL should not be None")
            self.assertIn(svg_key, download_url, "Download URL should contain the key")

            # 6. Download the file using the presigned URL
            response = session.get(download_url)
            response.raise_for_status()
            downloaded_content = response.content
            self.assertEqual(
                downloaded_content,
                original_content,
                "Downloaded content should match original",
            )

            # 7. Test download as base64 and verify against saved base64
            base64_content = self.s3.download_as_base64(TEST_BUCKET, svg_key)
            self.assertIsNotNone(base64_content, "Base64 content should not be None")
            self.assertIsInstance(
                base64_content, str, "Base64 content should be a string"
            )

            # Define path for base64 file
            base64_path = os.path.join(
                os.path.dirname(__file__), "resource", "test_base64.txt"
            )

            # Read the expected base64 from file
            with open(base64_path, "r", encoding="utf-8") as f:
                expected_base64 = f.read().strip()

            # Verify base64 content matches the expected value
            self.assertEqual(
                base64_content,
                expected_base64,
                "Base64 content should match the expected value",
            )

            # Also verify the decoded content matches the original
            decoded_content = base64.b64decode(base64_content)
            self.assertEqual(
                decoded_content,
                original_content,
                "Base64 decoded content should match original",
            )

        except Exception as e:
            self.fail(f"Test failed during upload/download: {str(e)}")
        finally:
            # Clean up - delete the test file
            try:
                result = self.s3.delete_object(TEST_BUCKET, svg_key)
                self.assertEqual(
                    result["status"], "success", "Delete should be successful"
                )

                # Verify deletion
                with self.assertRaises(ClientError) as cm:
                    self.s3.client.head_object(Bucket=TEST_BUCKET, Key=svg_key)
                self.assertEqual(
                    cm.exception.response["Error"]["Code"],
                    "404",
                    "File should be deleted",
                )
            except Exception as e:
                print(f"Warning: Failed to clean up test file {svg_key}: {str(e)}")

    def test_delete_object_WithExistingFile_ShouldRemoveFromS3(self):
        """Test that deleting an existing object removes it from S3."""
        # Upload a test file
        key = self._upload_test_file("delete_test")

        # Delete the file
        result = self.s3.delete_object(TEST_BUCKET, key)
        self.assertEqual(result["status"], "success")

        # Verify the file is deleted
        with self.assertRaises(ClientError) as cm:
            self.s3.client.head_object(Bucket=TEST_BUCKET, Key=key)
        self.assertEqual(cm.exception.response["Error"]["Code"], "404")


if __name__ == "__main__":
    unittest.main()
