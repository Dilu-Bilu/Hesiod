# import os
# import boto3
# from config.settings.production import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME 
# # Define your AWS credentials
# aws_access_key_id = AWS_ACCESS_KEY_ID
# aws_secret_access_key = AWS_SECRET_ACCESS_KEY

# # Create a boto3 client for S3
# s3 = boto3.client('s3',
#                   aws_access_key_id=aws_access_key_id,
#                   aws_secret_access_key=aws_secret_access_key)

# model_file = "modelreal/pytorch_model.bin"

# if not os.path.exists(model_file):
#     s3.download_file(AWS_STORAGE_BUCKET_NAME, "pytorch_model.bin", model_file)
