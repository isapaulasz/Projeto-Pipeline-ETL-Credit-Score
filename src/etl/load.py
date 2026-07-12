# load.py
import os
import redshift_connector
from dotenv import load_dotenv

load_dotenv()

def load(s3_key: str, bucket: str, table: str):
    """
    Carrega o parquet curado (gerado pelo transform.py) do S3 
    para uma tabela no Redshift usando o comando COPY.
    """
    conn = redshift_connector.connect(
        host=os.getenv("REDSHIFT_HOST"),
        database=os.getenv("REDSHIFT_DB"),
        port=int(os.getenv("REDSHIFT_PORT", 5439)),
        user=os.getenv("REDSHIFT_USER"),
        password=os.getenv("REDSHIFT_PASSWORD"),
    )
    cursor = conn.cursor()

    s3_path = f"s3://{bucket}/{s3_key}"
    iam_role = os.getenv("REDSHIFT_IAM_ROLE_ARN")

    copy_sql = f"""
        COPY {table}
        FROM '{s3_path}'
        IAM_ROLE '{iam_role}'
        FORMAT AS PARQUET;
    """

    cursor.execute(copy_sql)
    conn.commit()
    print(f"Dados carregados de {s3_path} para a tabela {table}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    load(
        s3_key=f"curated/credit_score/dt=2026-07-12/part-00000.parquet",
        bucket="projeto-datagirls-credit-score-382142767452-us-east-2-an",
        table="credit_score.curated"
    )