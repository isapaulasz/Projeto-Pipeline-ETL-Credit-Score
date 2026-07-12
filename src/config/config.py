from dotenv import load_dotenv
import os
import boto3

load_dotenv()  # carrega o .env para as variáveis de ambiente
os.environ["KAGGLE_API_TOKEN"] = os.getenv("KAGGLE_API_TOKEN")

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION")
)