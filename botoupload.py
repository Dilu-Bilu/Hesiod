import boto3

s3 = boto3.client("s3")

s3.upload_file("pytorch_model.bin", "hesiodbucket", "pytorch_model.bin")
