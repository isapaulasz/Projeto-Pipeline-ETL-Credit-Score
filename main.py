from extract import extract
from transform import transform

bucket = "datagirlsfinance-creditscore"

dt = extract(kaggle_dataset="usuario/nome-do-dataset", bucket=bucket)
transform(bucket=bucket, dt=dt)