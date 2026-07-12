# spark_config.py
from pyspark.sql import SparkSession
import os
from dotenv import load_dotenv

load_dotenv()

def get_spark_session():
    spark = SparkSession.builder \
        .appName("CreditScorePipeline") \
        .config("spark.jars.packages",
                "org.apache.hadoop:hadoop-aws:3.4.2,"
                "software.amazon.awssdk:bundle:2.29.52") \
        .config("spark.hadoop.fs.s3a.access.key", os.getenv("AWS_ACCESS_KEY_ID")) \
        .config("spark.hadoop.fs.s3a.secret.key", os.getenv("AWS_SECRET_ACCESS_KEY")) \
        .config("spark.hadoop.fs.s3a.endpoint", f"s3.{os.getenv('AWS_DEFAULT_REGION')}.amazonaws.com") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.aws.credentials.provider",
                "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider") \
        .getOrCreate()
    return spark