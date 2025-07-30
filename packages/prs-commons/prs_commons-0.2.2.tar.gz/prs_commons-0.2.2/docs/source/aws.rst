AWS S3 Client
=============

A thread-safe singleton client for interacting with AWS S3 storage, implementing the `StorageClient` interface. The client provides both synchronous and asynchronous methods for interacting with S3, with automatic cleanup of test resources when used in test environments.

.. note::
   This client is designed to be used as a singleton within your application.
   Multiple instances will return the same underlying client.

Configuration
-------------

The S3Client is configured using environment variables. All parameters are required.

.. list-table::
   :header-rows: 1
   :widths: 20 10 10 60

   * - Variable
     - Type
     - Default
     - Description
   * - REGION
     - string
     - None
     - AWS region name (e.g., 'us-east-1')
   * - BUCKET_ACCESS_KEY_ID
     - string
     - None
     - AWS access key ID with S3 permissions
   * - BUCKET_SECRET_ACCESS_KEY
     - string
     - None
     - AWS secret access key
   * - BUCKET_NAME
     - string
     - None
     - Default bucket name (optional, can be passed to methods)

Example ``.env`` file:

.. code-block:: bash

   REGION=us-east-1
   BUCKET_ACCESS_KEY_ID=your-access-key-id
   BUCKET_SECRET_ACCESS_KEY=your-secret-access-key
   BUCKET_NAME=my-default-bucket

Basic Usage
-----------

Initialization
~~~~~~~~~~~~~

The S3Client is configured using environment variables. Make sure these are set before initializing the client:

.. code-block:: python

   from prs_commons import S3Client

   # Initialize with environment variables
   s3 = S3Client()

   # The client is now ready to use

Testing
~~~~~~~

When using the S3Client in tests, it automatically handles cleanup of test files. The test suite includes fixtures that:

- Clean up test files after each test
- Handle both synchronous and asynchronous test methods
- Provide proper error handling and reporting

To use in tests, simply extend from the test class and use the provided fixtures.

File Operations
~~~~~~~~~~~~~~

Uploading Files
^^^^^^^^^^^^^^

.. code-block:: python

   # Basic upload
   result = s3.upload_file(
       file_path="local_file.txt",
       bucket="my-bucket",
       key="path/in/s3/file.txt"
   )

   # Upload with additional S3 parameters
   result = s3.upload_file(
       file_path="local_file.txt",
       bucket="my-bucket",
       key="path/in/s3/file.txt",
       ExtraArgs={
           'ContentType': 'text/plain',
           'Metadata': {'author': 'user'}
       }
   )

Downloading Files
^^^^^^^^^^^^^^^

.. code-block:: python

   # Basic download
   try:
       success = s3.download_file(
           bucket="my-bucket",
           key="path/in/s3/file.txt",
           file_path="local_file.txt"
       )
       if success:
           print("File downloaded successfully")
   except FileNotFoundError as e:
       print(f"File not found: {e}")
   except PermissionError as e:
       print(f"Permission denied: {e}")
   except ClientError as e:
       print(f"S3 error: {e}")

   # Download as base64-encoded string
   try:
       file_data = s3.download_as_base64(
           bucket="my-bucket",
           key="documents/report.pdf"
       )
       print(f"Downloaded file (base64, {len(file_data)} bytes)")
   except FileNotFoundError as e:
       print(f"File not found: {e}")
   except PermissionError as e:
       print(f"Permission denied: {e}")
   except ClientError as e:
       print(f"S3 error: {e}")

Deleting Files
^^^^^^^^^^^^^

.. code-block:: python

   result = s3.delete_object(
       bucket="my-bucket",
       key="path/in/s3/file.txt"
   )

Pre-signed URLs
~~~~~~~~~~~~~

Generate Upload URL
^^^^^^^^^^^^^^^^^^^

.. py:method:: generate_upload_url(bucket: str, key: str, expiration: int = 3600, **kwargs: Any) -> str | None
   :noindex:

   Generate a pre-signed URL for uploading a file to S3.

   This is a convenience wrapper around :meth:`generate_presigned_url` for uploads.
   The content type will be automatically detected from the file extension if not provided.

   :param bucket: S3 bucket name
   :type bucket: str
   :param key: S3 object key where the file will be stored
   :type key: str
   :param expiration: Time in seconds until the URL expires (default: 3600)
   :type expiration: int
   :param \*\*kwargs: Additional parameters to pass to the S3 put_object operation
   :return: Pre-signed URL as a string, or None if credentials are invalid
   :rtype: str | None

   **Common Parameters**

   - ``ContentType`` (str, optional): The content type of the file (e.g., 'image/jpeg').
     If not provided, it will be automatically detected from the file extension.
   - ``ACL`` (str, optional): Access control for the file. Defaults to the bucket's ACL.
     Common values: 'private', 'public-read', 'public-read-write', 'authenticated-read'
   - ``Metadata`` (dict, optional): Dictionary of metadata to store with the object.
     Keys will be prefixed with 'x-amz-meta-' when stored in S3.
   - Other parameters supported by boto3's `generate_presigned_url` for 'put_object' operation

   **Example**

   .. code-block:: python

      # Generate URL for uploading a text file with metadata
      url = s3.generate_upload_url(
          bucket='my-bucket',
          key='documents/report.txt',
          ContentType='text/plain',
          Metadata={
              'author': 'user@example.com',
              'description': 'Quarterly report Q2 2023'
          },
          expiration=7200  # 2 hours
      )

   # Use the URL to upload a file with a PUT request
   # import requests
   # with open('file.txt', 'rb') as f:
   #     response = requests.put(url, data=f)

Generate Download URL
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Generate a pre-signed URL for file download
   download_url = s3.generate_download_url(
       bucket="my-bucket",
       key="downloads/file.txt",
       ResponseContentType="application/octet-stream",
       expiration=3600  # URL expires in 1 hour (default)
   )
   print(f"Download URL: {download_url}")

Error Handling
~~~~~~~~~~~~~

The S3 client raises the following exceptions:

- ``ClientError``: For AWS service errors
- ``NoCredentialsError``: When AWS credentials are not found
- ``RuntimeError``: For client initialization errors
- ``FileNotFoundError``: When the requested file doesn't exist
- ``PermissionError``: When there are permission issues

Example error handling:

.. code-block:: python

   from botocore.exceptions import ClientError, NoCredentialsError

   try:
       # Your S3 operations here
       pass
   except FileNotFoundError as e:
       print(f"File not found: {e}")
   except PermissionError as e:
       print(f"Permission denied: {e}")
   except NoCredentialsError:
       print("AWS credentials not found")
   except ClientError as e:
       error_code = e.response.get('Error', {}).get('Code')
       if error_code == 'NoSuchBucket':
           print("Bucket does not exist")
       else:
           print(f"AWS error: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")

.. code-block:: python

   from botocore.exceptions import ClientError, NoCredentialsError

   try:
       s3.upload_file("nonexistent.txt", "my-bucket", "file.txt")
   except FileNotFoundError as e:
       print(f"Local file not found: {e}")
   except NoCredentialsError:
       print("AWS credentials not found")
   except ClientError as e:
       print(f"AWS error: {e.response['Error']['Message']}")
   except Exception as e:
       print(f"Unexpected error: {e}")

API Reference
-------------

.. autoclass:: prs_commons.aws.s3_client.S3Client
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: __weakref__

File Operations
--------------

Base64 Download
~~~~~~~~~~~~~~

.. automethod:: prs_commons.aws.s3_client.S3Client.download_as_base64
   :noindex:

Pre-signed URLs
~~~~~~~~~~~~~~

The S3 client provides methods to generate pre-signed URLs for secure, time-limited access to S3 objects:

.. automethod:: prs_commons.aws.s3_client.S3Client.generate_presigned_url
   :noindex:

.. automethod:: prs_commons.aws.s3_client.S3Client.generate_upload_url
   :noindex:

.. automethod:: prs_commons.aws.s3_client.S3Client.generate_download_url
   :noindex:

Error Handling
-------------

All methods return a dictionary with the following structure:

.. code-block:: python

   {
       "status": "success" | "error",
       "bucket": "bucket-name",
       "key": "object-key",
       # Only present if status is "error"
       "error": "error-message",
       # Additional fields may be present depending on the operation
   }

Thread Safety
------------
The S3Client is implemented as a thread-safe singleton. Multiple threads can safely use the same instance.

Dependencies
------------
- boto3 >= 1.28.0
- botocore >= 1.31.0
