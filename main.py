from src.etl.extract import extract
from src.etl.transform import transform

bucket = "datagirlsfinance-creditscore"

dt = extract(kaggle_dataset="usuario/nome-do-dataset", bucket=bucket)
transform(bucket=bucket, dt=dt)