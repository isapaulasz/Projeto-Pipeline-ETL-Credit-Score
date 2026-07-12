import kagglehub
from kagglehub import KaggleDatasetAdapter
import numpy as np
import pandas as pd
import re
import os
import time
from src.config.config import s3

def extrair_dados_kaggle(dataset_slug: str, file_path: str, max_tentativas: int = 3):
  tentativa = 0
  while tentativa < max_tentativas:
    try:
      df = kagglehub.dataset_load(
          KaggleDatasetAdapter.PANDAS,
          dataset_slug,
          file_path,
      )
      if df is None or df.empty:
        raise ValueError("Dataframe vazio.")
      print(f"Dados extraídos com sucesso: {len(df)} linhas, {len(df.columns)} colunas.")
      return df

    except FileNotFoundError as e:
      print(f"Arquivo não encontrado: {e}")
      raise

    except Exception as e:
      tentativa += 1
      print(f"Tentativa {tentativa}/{max_tentativas} falhou: {e}")
      if tentativa < max_tentativas:
        time.sleep(5 * tentativa)
      else:
        print("Falha após múltiplas tentativas. Abortando extração.")
        raise


def ver_dados(df):
    df.head()

    df.shape

    df.info()

    df.isnull().sum()
    
    df.describe()

def limpar_valor_invalido(df):
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].astype(str).str.strip().str.strip('_')


    df = df.replace(
        to_replace=r'(?i)^nan$',  # (?i) = ignora maiúscula/minúscula; ^...$ = precisa ser exatamente isso
        value=np.nan,
        regex=True
    )

    df = df.replace(["NA", "NM", "!@9#%8", "#F%$D@*&8", "__10000__","_", "_______", "", " "], np.nan)
    
    return df

def converter_tipos(df):
    colunas_valor_float = ['renda_anual', 'salario_mensal_liquido', 'variacao_limite_credito', 'divida_pendente', 'valor_investido_mensal', 'saldo_mensal']

    for col in colunas_valor_float:
        df[col] = df[col].astype(float)

    colunas_valor_int = ['idade', 'qtd_consultas_credito', 'qtd_emprestimos', 'qtd_pagamentos_atrasados', 'qtd_contas_bancarias', 'qtd_cartoes_credito']

    for col in colunas_valor_int:
        df[col] = df[col].astype('Int64')
    
    return df

def converter_em_nulo(df):
    Q1 = df['renda_anual'].quantile(0.25)
    Q3 = df['renda_anual'].quantile(0.75)
    IQR = Q3 - Q1
    limite_superior = Q3 + 1.5 * IQR
    df.loc[df['renda_anual'] > limite_superior, 'renda_anual'] = np.nan

    colunas_valores_negativos = ['idade', 'qtd_emprestimos', 'qtd_contas_bancarias', 'qtd_pagamentos_atrasados']

    for col in colunas_valores_negativos:
        qtd_negativos = (df[col] < 0).sum()
        print(f"{col}: {qtd_negativos} valores negativos encontrados")
        df.loc[df[col] < 0, col] = np.nan

    df.loc[df['idade'] > 110, 'idade'] = np.nan

    colunas_valores_acima_de_40 = ['qtd_cartoes_credito', 'taxa_juro', 'qtd_pagamentos_atrasados']

    for col in colunas_valores_acima_de_40:
        df.loc[df[col] > 40, col] = np.nan

    df.loc[df['qtd_consultas_credito'] > 20, 'qtd_consultas_credito'] = np.nan

    df.loc[df['qtd_contas_bancarias'] > 15, 'qtd_contas_bancarias'] = np.nan

    df.loc[df['qtd_emprestimos'] > 10, 'qtd_emprestimos'] = np.nan

    return df

def arredondar_numericos(df):
    colunas_monetarias = [
        'renda_anual', 'salario_mensal_liquido', 'variacao_limite_credito', 'divida_pendente', 'saldo_mensal', 'valor_investido_mensal', 'emi_total_ao_mes'
    ]

    for col in colunas_monetarias:
        df[col] = df[col].round(2)

    df['taxa_utilizacao_credito'] = df['taxa_utilizacao_credito'].round(4)

    return df

def converter_para_meses(valor):
    if pd.isna(valor):
        return np.nan
    match = re.match(r'(\d+) Years and (\d+) Months', valor)
    if match:
        anos, meses = int(match.group(1)), int(match.group(2))
        meses_totais = int(anos * 12 + meses)
        return meses_totais
    return np.nan

def one_hot_encode_tipo_emprestimo(df):
    df['tem_auto_loan'] = df['tipo_de_emprestimo'].str.contains('Auto Loan', na=False)
    df['tem_credit_builder_loan'] = df['tipo_de_emprestimo'].str.contains('Credit-Builder Loan', na=False)
    df['tem_debt_consolidation_loan'] = df['tipo_de_emprestimo'].str.contains('Debt Consolidation Loan', na=False)
    df['tem_home_equity_loan'] = df['tipo_de_emprestimo'].str.contains('Home Equity Loan', na=False)
    df['tem_mortgage_loan'] = df['tipo_de_emprestimo'].str.contains('Mortgage Loan', na=False)
    df['tem_payday_loan'] = df['tipo_de_emprestimo'].str.contains('Payday Loan', na=False)
    df['tem_personal_loan'] = df['tipo_de_emprestimo'].str.contains('Personal Loan', na=False)
    df['tem_student_loan'] = df['tipo_de_emprestimo'].str.contains('Student Loan', na=False)
    # Substitui células que são compostas inteiramente por "Not Specified" repetido (com vírgulas e "and")
    df['tipo_de_emprestimo'] = df['tipo_de_emprestimo'].replace(
        to_replace=r'^(Not Specified[,\s]*(and)?[,\s]*)+$',
        value=np.nan,
        regex=True
    )
    df = df.drop(columns=['tipo_de_emprestimo'])
    
    return df

def imputar_valores(df):
    colunas_puxar_mesmo_cliente = [
        'idade', 'profissao', 'seguro_social_ssn', 'nome',
        'qtd_contas_bancarias', 'qtd_cartoes_credito', 'taxa_juro'
    ]

    for col in colunas_puxar_mesmo_cliente:
        df[col] = df.groupby('id_cliente')[col].transform(
            lambda x: x.fillna(x.mode()[0] if not x.mode().empty else np.nan)
        )

    colunas_imputar_mediana = [
        'renda_anual', 'salario_mensal_liquido', 'divida_pendente',
        'saldo_mensal', 'valor_investido_mensal', 'emi_total_ao_mes',
        'variacao_limite_credito', 'taxa_utilizacao_credito',
        'qtd_emprestimos', 'qtd_pagamentos_atrasados', 'qtd_consultas_credito',
        'atraso_dias', 'tempo_historico_credito_meses'
    ]

    for col in colunas_imputar_mediana:
        df[col] = df[col].fillna(df[col].median())

    colunas_categoricas = ['classificacao_credito', 'pagamento_valor_min', 'padrao_comportamento_pagamento']

    for col in colunas_categoricas:
        df[col] = df[col].fillna(df[col].mode()[0])
        return df

def transform(bucket, dt, domain="credit_score"):

    # Lê train e test separadamente
    df_train = extrair_dados_kaggle("parisrohan/credit-score-classification", "train.csv")
    df_test = extrair_dados_kaggle("parisrohan/credit-score-classification", "test.csv")

    # --- Etapa intermediária: unir train + test, limpeza básica ---
    df_train['origem'] = 'train'
    df_test['origem'] = 'test'

    # Garante que test tenha a coluna faltante, preenchida com NaN
    if 'Credit_Score' not in df_test.columns:
        df_test['Credit_Score'] = pd.NA

    # Reordena as colunas de test para bater com train antes de concatenar
    df_test = df_test[df_train.columns]

    df = pd.concat([df_train, df_test], ignore_index=True)

    df = df.rename(columns={
        "ID": "id_registro",
        "Customer_ID": "id_cliente",
        "Month": "mes",
        "Name":"nome",
        "Age":"idade",
        "SSN":"seguro_social_ssn",
        "Occupation":"profissao",
        "Annual_Income": "renda_anual",
        "Monthly_Inhand_Salary": "salario_mensal_liquido",
        "Num_Bank_Accounts": "qtd_contas_bancarias",
        "Num_Credit_Card": "qtd_cartoes_credito",
        "Interest_Rate": "taxa_juro",
        "Num_of_Loan": "qtd_emprestimos",
        "Type_of_Loan": "tipo_de_emprestimo",
        "Delay_from_due_date": "atraso_dias",
        "Num_of_Delayed_Payment": "qtd_pagamentos_atrasados",
        "Changed_Credit_Limit": "variacao_limite_credito",
        "Num_Credit_Inquiries": "qtd_consultas_credito",
        "Credit_Mix": "classificacao_credito",
        "Outstanding_Debt":"divida_pendente",
        "Credit_Utilization_Ratio":"taxa_utilizacao_credito",
        "Credit_History_Age":"tempo_historico_credito",
        "Payment_of_Min_Amount":"pagamento_valor_min",
        "Total_EMI_per_month":"emi_total_ao_mes",
        "Amount_invested_monthly": "valor_investido_mensal",
        "Payment_Behaviour":"padrao_comportamento_pagamento",
        "Monthly_Balance":"saldo_mensal",
        "Credit_Score": "score_credito"
    })

    ver_dados(df)
    df_staging = limpar_valor_invalido(df)
    df_staging = converter_tipos(df_staging)
    df_staging = converter_em_nulo(df_staging)
    df_staging = arredondar_numericos(df_staging)
    df_staging['tempo_historico_credito_meses'] = df_staging['tempo_historico_credito'].apply(converter_para_meses)
    df_staging = df_staging.drop(columns=['tempo_historico_credito'])
    df_staging = one_hot_encode_tipo_emprestimo(df_staging)
    df_staging = imputar_valores(df_staging)
    ver_dados(df_staging)

    
    # --- Etapa final: validações, tipos, schema definitivo ---
    df_curated = df_staging.drop(columns=['nome', 'seguro_social_ssn'])
    df_curated = df_curated.dropna()

    local_curated_file = "curated_temp.parquet"
    df_curated.to_parquet(local_curated_file, index=False)
    
    s3_key = f"curated/{domain}/dt={dt}/part-00000.parquet"
    s3.upload_file(local_curated_file, bucket, s3_key)
    print(f"Curated gravado em: s3://{bucket}/{s3_key}")
    
    os.remove(local_curated_file)
    
    return s3_key

if __name__ == "__main__":
    transform(bucket="projeto-datagirls-credit-score-382142767452-us-east-2-an", dt="2026-07-10")