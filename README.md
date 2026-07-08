# Pipeline ETL para Score de Crédito

**Status geral: 🟡 Em andamento** | Bootcamp de Engenharia de Dados | 2026

Pipeline de dados para estruturar informações de clientes bancários, permitindo que equipes de Analytics e Crédito utilizem os dados em modelos de score de crédito e análise de risco.

Dataset de origem: [Credit Score Classification (Kaggle)](https://www.kaggle.com/datasets/parisrohan/credit-score-classification)

---

## Arquitetura do pipeline

![Arquitetura do pipeline](imagens/arquitetura.svg)

O projeto está sendo construído em etapas. Abaixo, o status real de cada uma:

| Etapa | Descrição | Status |
|---|---|---|
| Extração | Coleta dos dados via `kagglehub` (train/test) | ✅ Concluído |
| Transformação | Limpeza, padronização de tipos, tratamento de outliers, imputação de nulos, one-hot encoding | ✅ Concluído |
| Armazenamento local | Exportação do dataset curado em `.parquet` | ✅ Concluído |
| Processamento distribuído | Reescrita/adaptação do pipeline em PySpark, ingestão via Kafka | 🔲 Planejado |
| Data Lake | Armazenamento em AWS S3 e Azure Data Lake Storage Gen2 | 🔲 Planejado |
| Data Warehouse | Carga estruturada em AWS Redshift e Azure Synapse Analytics | 🔲 Planejado |
| Orquestração | Automação e agendamento das etapas com Apache Airflow | 🔲 Planejado |
| Segurança/Acesso | Gestão de permissões via AWS IAM | 🔲 Planejado |

> Este README é atualizado conforme o pipeline evolui. A versão atual cobre apenas a etapa de **extração e limpeza dos dados em Python**, feita no notebook desta pasta.

---

## O que já foi feito

O notebook [`notebooks/Credit_Score_Classification.ipynb`](notebooks/Credit_Score_Classification.ipynb) contém:

- **Extração**: carregamento dos conjuntos `train` e `test` diretamente do Kaggle com `kagglehub`, com retentativas automáticas em caso de falha.
- **Unificação**: concatenação dos dois conjuntos, com marcação de origem (`train`/`test`).
- **Padronização**: renomeação de colunas para português, limpeza de espaços/underscores e normalização de valores nulos disfarçados (`"NM"`, `"!@9#%8"`, `"_______"`, etc.).
- **Tipagem**: conversão de colunas monetárias para `float` e de colunas de contagem para `Int64`.
- **Tratamento de outliers**: valores impossíveis (idade > 110, valores negativos, taxas fora do esperado) convertidos em nulos via regras de negócio e IQR.
- **Engenharia de atributos**: conversão de `tempo de histórico de crédito` (texto "X anos e Y meses") para número de meses; one-hot encoding da coluna de tipos de empréstimo.
- **Imputação**: preenchimento de nulos por moda (dados do mesmo cliente) e por mediana (variáveis numéricas contínuas).
- **Exportação**: dataset final salvo em formato `.parquet` (compressão gzip), pronto para consumo por outras equipes.

## Próximos passos

1. Migrar o processamento para **PySpark**, preparando o pipeline para volumes maiores.
2. Configurar ingestão via **Kafka** para simular dados chegando em stream.
3. Subir a infraestrutura de **Data Lake** (AWS S3 / Azure Data Lake Storage Gen2).
4. Modelar e carregar os dados no **Data Warehouse** (AWS Redshift / Azure Synapse Analytics).
5. Orquestrar todas as etapas com **Apache Airflow**.
6. Configurar controle de acesso com **AWS IAM**.

## Stack

**Já utilizado:**
Python, pandas, numpy, kagglehub

**Planejado para as próximas etapas:**
PySpark, Apache Kafka, Apache Airflow, AWS (IAM, S3, Redshift), Azure (Data Lake Storage Gen2, Synapse Analytics)

## Estrutura do repositório

```
pipeline-etl-credito/
├── notebooks/
│   └── Credit_Score_Classification.ipynb
├── imagens/
│   └── arquitetura.svg
└── README.md
```

## Como executar

```bash
pip install kagglehub[pandas-datasets] pandas numpy
jupyter notebook notebooks/Credit_Score_Classification.ipynb
```

---
*Projeto desenvolvido como parte do Bootcamp de Engenharia de Dados (2026).*
