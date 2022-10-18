from datetime import datetime
import logging
import os

import boto3
from botocore.exceptions import ClientError


#REALM_DIR_LOCATION = "/c/Users/Daniel/AppData/Roaming/Stashpad/"
REALM_DIR_LOCATION = "/mnt/c/Users/15san/AppData/Roaming/Stashpad/"
REALM_FILE_NAME = "data.realm"
BUCKET_NAME = "cdev-bucket-f206d6f16c5816e9215949f6021aeb1b"


def check_local_file() -> bool:
    return os.path.isfile(os.path.join(REALM_DIR_LOCATION, REALM_FILE_NAME))


def pull_new_version() -> None:
    s3 = boto3.client('s3')
    
    get_last_modified_expr = lambda obj: int(obj['LastModified'].strftime('%s'))

    objs = s3.list_objects_v2(Bucket=BUCKET_NAME)['Contents']
    last_added = [obj['Key'] for obj in sorted(objs, key=get_last_modified_expr)][0]


    with open(os.path.join(REALM_DIR_LOCATION, REALM_FILE_NAME), 'wb') as fh:
        s3.download_fileobj(BUCKET_NAME, last_added, fh)


def push_new_version() -> None:
    if not check_local_file():
        raise Exception(f"Can not find file to sync")

    rv = upload_file(os.path.join(REALM_DIR_LOCATION, REALM_FILE_NAME), BUCKET_NAME, f"{REALM_FILE_NAME}_{_generate_timestamp()}")

    if not rv:
        raise Exception("Error uploading the file")


def _generate_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S")


def upload_file(file_name: str, bucket: str, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


push_new_version()
#pull_new_version()