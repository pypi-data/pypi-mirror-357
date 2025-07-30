from datetime import datetime, timedelta, timezone
from typing import List, Optional, Union, Iterable, Dict, overload

import backoff
from google.cloud.storage import Client as GoogleStorageClient, Blob, Bucket

from arcane.core.exceptions import GOOGLE_EXCEPTIONS_TO_RETRY


class FileSizeTooLargeException(Exception):
    """ Raise when a file is too large to be uploaded """
    pass

DEFAULT_MINUTES_SINCE_LAST_UPDATE = 30
ALLOWED_IMAGE_EXTENSIONS = { 'jpg', 'jpeg', 'png'}
def allowed_file(filename):
    ''' Check if the file extension is supported by our application
        Args:
            filename (string): The name of the input file

        Returns:
            bool: True if the file is allowed to be processed, false if not
        '''
    return '.' in filename and get_file_extension(filename) in ALLOWED_IMAGE_EXTENSIONS


def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()


class Client(GoogleStorageClient):
    def __init__(self, project=None, credentials=None, _http=None):
        super().__init__(project=project, credentials=credentials, _http=_http)

    @backoff.on_exception(backoff.expo, GOOGLE_EXCEPTIONS_TO_RETRY, max_tries=5)
    def list_blobs(
        self,
        bucket_or_name: Union[Bucket, str],
        prefix: Union[str, None] = None,
        **kwargs) -> Iterable[Blob]:
        return super().list_blobs(bucket_or_name, prefix=prefix, **kwargs)

    @backoff.on_exception(backoff.expo, GOOGLE_EXCEPTIONS_TO_RETRY, max_tries=5)
    def list_gcs_directories(self, bucket_name: str, prefix: str = None):
        """
            Get subdirectories of a "folder"
        :param bucket:
        :param prefix:
        :return list of "directories":
        """
        # from https://github.com/GoogleCloudPlatform/google-cloud-python/issues/920
        if prefix:
            if prefix[-1] != '/':
                prefix += '/'
        iterator = self.list_blobs(bucket_name, prefix=prefix, delimiter='/')
        prefixes = set()
        for page in iterator.pages:
            prefixes.update(page.prefixes)
        return [directory.strip(prefix).strip('/') for directory in prefixes]

    @backoff.on_exception(backoff.expo, GOOGLE_EXCEPTIONS_TO_RETRY, max_tries=5)
    def get_blob(self, bucket_name: str, file_name: str) -> Blob:
        bucket = self.get_bucket(bucket_name)
        blob = bucket.get_blob(file_name)
        return blob

    def upload_image_to_bucket(self, bucket_name: str, id_image: str, content, content_type, file_size: int):
        if(file_size > 1048576 ):
            raise FileSizeTooLargeException('The maximun size is 1 Mo (1 048 576 bytes)')
        bucket_client = self.bucket(bucket_name)
        blob = bucket_client.blob(id_image)
        blob.upload_from_string(
            content,
            content_type = content_type
        )
        bucket_url = blob.public_url
        return bucket_url

    @staticmethod
    @backoff.on_exception(backoff.expo, GOOGLE_EXCEPTIONS_TO_RETRY, max_tries=3)
    def compose_blobs(
        blobs_list: List[Blob],
        master_blob_path: str,
        bucket: Bucket,
        metadata: Optional[Dict] = None
    ) -> Blob:
        """Concatenate a list of google storage object into one"""
        master_blob = bucket.blob(master_blob_path)
        master_blob.content_type = 'text/plain'

        if metadata is not None:
            master_blob.metadata = metadata

        master_blob.compose(blobs_list)
        return master_blob

    @staticmethod
    @backoff.on_exception(backoff.expo, GOOGLE_EXCEPTIONS_TO_RETRY, max_tries=3)
    def delete_blobs(blobs_list: List[Blob]) -> None:
        """Delete a list of google storage objects"""
        for blob in blobs_list:
            blob.delete()

    @backoff.on_exception(backoff.expo, GOOGLE_EXCEPTIONS_TO_RETRY, max_tries=3)
    def concatenate_sub_files(
        self,
        blobs_list: List[Blob],
        blob_path: str,
        bucket: Bucket,
        metadata: Optional[Dict] =  None
    ) -> Blob:
        """Concatenate all google storage objects stored at a specific path into one"""

        temporary_folder = 1
        int_blobs_list = list(blobs_list)

        while len(int_blobs_list) > 32:

            blobs_to_combine = list()
            index = 1

            for idx, blob in enumerate(int_blobs_list):

                blobs_to_combine.append(blob)

                # If we reached the limit of composite blobs to be combined, or the end of the list
                if (len(blobs_to_combine) == 32) or (idx == len(int_blobs_list) - 1):
                    combined_blob = bucket.blob(f'{blob_path}/{temporary_folder}/{index}')
                    combined_blob.content_type = 'text/plain'
                    combined_blob.compose(blobs_to_combine)
                    self.delete_blobs(blobs_to_combine)
                    index += 1
                    blobs_to_combine = list()

            int_blobs_list = list(self.list_blobs(bucket, prefix=f'{blob_path}/{str(temporary_folder)}'))
            temporary_folder += 1

        try:
            master_blob = self.compose_blobs(
                int_blobs_list, blob_path, bucket, metadata)
            self.delete_blobs(int_blobs_list)
            return master_blob

        except ValueError as err:
            print(f"Error occured when combining files for file {blob_path}/ "
                f"execution_id - Trace : {str(err)}")
            raise ValueError(f"Error occured when combining shards for {blob_path} / "
                            f"execution_id - Trace : {str(err)}")

    @backoff.on_exception(backoff.expo, GOOGLE_EXCEPTIONS_TO_RETRY, max_tries=5)
    def upload_file_from_string(self, bucket_name: str, blob_name: str, content: str, metadata: Optional[Dict] = None) -> Blob:
        """ uploads a string as a file to a given bucket/blob """
        blob: Blob = self.bucket(bucket_name).blob(blob_name)
        if metadata is not None:
            blob.metadata = metadata
        blob.upload_from_string(content)
        return blob

    @backoff.on_exception(backoff.expo, GOOGLE_EXCEPTIONS_TO_RETRY, max_tries=5)
    def check_file_updated(
        self,
        bucket: str,
        file_name: str,
        minutes_since_last_update: int = DEFAULT_MINUTES_SINCE_LAST_UPDATE
    ):
        """check if the given file name exist in the bucket and has been updated in the last minutes_since_last_update minutes"""
        bucket = self.bucket(bucket)
        blob = bucket.get_blob(file_name)

        if blob is None:
            raise FileNotFoundError(f"File {file_name} does not exist")
        blob_update_time = blob.updated
        if blob_update_time is None:
            raise FileNotFoundError(f"File {file_name} has never been updated")
        if blob_update_time < datetime.now(tz=timezone.utc) - timedelta(minutes=minutes_since_last_update):
            raise FileNotFoundError(
                f"File {file_name} has not been updated since {blob.updated}")
        return blob


@overload
def generate_download_signed_url_v4(
    storage_client: Client, bucket_name: str, blob_name: str, downloaded_file_name: str, blob: None = None
) -> str:
    """
    Generates a signed URL for downloading a blob using bucket and blob names.

    Args:
        storage_client (Client): An instance of the custom Google Cloud Storage client.
        bucket_name (str): The name of the bucket containing the blob.
        blob_name (str): The name of the blob to generate the URL for.
        downloaded_file_name (str): The filename to be used when the blob is downloaded.
        blob (None): This overload is used when `blob` is not provided.

    Returns:
        str: A signed URL that allows downloading the blob.
    """
    ...


@overload
def generate_download_signed_url_v4(
    storage_client: Client, bucket_name: Optional[str], blob_name: Optional[str], downloaded_file_name: str, blob: Blob
) -> str:
    """
    Generates a signed URL for downloading a blob using an existing Blob object.

    Args:
        storage_client (Client): An instance of the custom Google Cloud Storage client.
        bucket_name (Optional[str]): The name of the bucket containing the blob. Not required if `blob` is provided.
        blob_name (Optional[str]): The name of the blob to generate the URL for. Not required if `blob` is provided.
        downloaded_file_name (str): The filename to be used when the blob is downloaded.
        blob (Blob): An existing Blob object.

    Returns:
        str: A signed URL that allows downloading the blob.
    """
    ...


def generate_download_signed_url_v4(storage_client: Client , bucket_name: Optional[str], blob_name: Optional[str], downloaded_file_name: str, blob: Optional[Blob] = None) -> str:
    """
    Generates a signed URL for downloading a blob.
    
    Args:
        storage_client (Client): An instance of the custom Google Cloud Storage client.
        bucket_name (Optional[str]): The name of the bucket containing the blob. Required if `blob` is not provided.
        blob_name (Optional[str]): The name of the blob to generate the URL for. Required if `blob` is not provided.
        downloaded_file_name (str): The filename to be used when the blob is downloaded.
        blob (Optional[Blob]): An existing Blob object. If provided, `bucket_name` and `blob_name` are not required.

    Returns:
        str: A signed URL that allows downloading the blob.
    
    Raises:
        FileNotFoundError: If the blob does not exist in the bucket.
    """
    if not blob:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
    if blob.exists(storage_client):
        url = blob.generate_signed_url(
            # This URL is valid for 15 minutes
            expiration=timedelta(minutes=15),
            response_disposition=f'attachment; filename={downloaded_file_name}',
            # Allow GET requests using this URL.
            method='GET')
        return url
    else:
        raise FileNotFoundError
