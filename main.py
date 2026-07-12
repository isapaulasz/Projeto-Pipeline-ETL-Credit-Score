from src.etl.extract import extract
from src.etl.transform import transform
from src.etl.load import load

bucket = "projeto-datagirls-credit-score-382142767452-us-east-2-an"

dt = extract(kaggle_dataset="parisrohan/credit-score-classification", bucket=bucket)
s3_key = transform(bucket=bucket, dt=dt)

load(
    s3_key=s3_key,
    bucket=bucket,
    table="credit_score.curated"
)
