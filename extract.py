#pip install kagglehub[pandas-datasets]
#pip install boto3
import kagglehub
from kagglehub import KaggleDatasetAdapter
import boto3
import os
import glob
from datetime import date

def extract(kaggle_dataset, bucket, domain="credit_score"):
    dt = date.today().isoformat()

    # 1. Baixa o dataset do Kaggle
    path = kagglehub.dataset_download(kaggle_dataset)
    print(f"Dataset baixado em: {path}")

    # 2. Encontra os arquivos CSV baixados
    csv_files = glob.glob(f"{path}/*.csv")

    # 3. Sobe cada CSV para o S3, na camada raw/
    s3 = boto3.client('s3')
    for local_file in csv_files:
        filename = os.path.basename(local_file)
        s3_key = f"raw/{domain}/dt={dt}/{filename}"
        s3.upload_file(local_file, bucket, s3_key)
        print(f"Enviado: s3://{bucket}/{s3_key}")

    return dt  # retorna a data usada, para as próximas etapas reaproveitarem

if __name__ == "__main__":
    extract(
        kaggle_dataset="parisrohan/credit-score-classification",  # ajuste para o dataset real
        bucket="projeto-datagirls-credit-score-382142767452-us-east-2-an"
    )