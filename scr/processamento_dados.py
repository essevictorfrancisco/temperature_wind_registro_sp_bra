import pandas as pd

def calculate_metrics_by_period(
    df: pd.DataFrame,
    period: str,
    df_name: str
) -> pd.DataFrame:
    """Agrega métricas de colunas específicas em intervalos temporais definidos.

    Calcula máximo, média e mínimo para as 3 primeiras colunas de trabalho,
    média para a 4ª coluna e soma acumulada para a 5ª coluna.

    Args:
        df (pd.DataFrame): DataFrame contendo os dados originais.
        datetime_column (str): Nome da coluna com dados datetime para indexação.
        period (str): Frequência de agrupamento (ex: 'D' para diário, 'M' para
        mensal).

    Returns:
        pd.DataFrame: DataFrame com métricas agregadas por período.

    Raises:
        KeyError: Se alguma coluna necessária não existir no DataFrame.
    """
    required_columns = ['Temp', 'Umi', 'Vel_vento', 'Dir_vento', 'Chuva']

    # Verificação de colunas obrigatórias
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise KeyError(f'Colunas ausentes: {missing_columns}')

    # Define agregações para cada coluna
    aggregations = {
        'Temp': ['max', 'min', 'mean','std','median'],
        'Umi': ['max', 'min', 'mean','std','median'],
        'Vel_vento': ['max', 'min', 'mean','std','median'],
        'Dir_vento': ['mean','std','median'],
        'Chuva': ['sum','std']
    }

    # Calcula todas as métricas de uma vez
    period_df = df.resample(period).agg(aggregations)
    
    # Renomeia colunas multi-nível e padroniza nomenclatura
    period_df.columns = [
        f'{col}_{stat}' 
        for col, stat in period_df.columns
    ]
    
    # Ajusta sufixos conforme especificação original
    column_rename = {
        'mean': 'med',
        'sum': 'tot',
        'median': 'mediana',
        'std': 'dp'
    }
    period_df = period_df.rename(
        columns=lambda x: x.replace('mean', 'med').replace(
            'sum', 'tot').replace('median', 'mediana').replace('std', 'dp')
    )

    period_df = period_df[period_df['Temp_max'].notnull()]

    if not isinstance(df_name, str):
        raise KeyError(f'O nome do DataFrame <{df_name}> não é uma string!')

    period_df.attrs['Name'] = df_name

    print(f'{period_df.attrs["Name"]} tem {period_df.shape[0]} linhas e {period_df.shape[1]} colunas.')

    return period_df.round(2)