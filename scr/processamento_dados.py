import pandas as pd

epw_folder = '../epw_raw/'
inmet_folder = '../inmet_raw/'
export_folder = '../climate_csv/'

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
    required_columns = [
        'Temp', 'Umi', 'Vel_vento', 'Dir_vento', 'Precipitacao','Ori_vento'
    ]

    # Verificação de colunas obrigatórias
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise KeyError(f'Colunas ausentes: {missing_columns} in {df_name}')

    # Define agregações para cada coluna
    aggregations = {
        'Temp': ['max', 'min', 'mean','std','median'],
        'Umi': ['max', 'min', 'mean','std','median'],
        'Vel_vento': ['max', 'min', 'mean','std','median'],
        'Dir_vento': ['mean','std','median','mode'],
        'Precipitacao': ['sum','std'],
        'Ori_vento':['mode']
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
            'sum', 'tot').replace('median', 'mediana').replace(
            'std', 'dp').replace('mode','moda')
    )

    period_df = period_df[period_df['Temp_max'].notnull()]

    if not isinstance(df_name, str):
        raise KeyError(f'O nome do DataFrame <{df_name}> não é uma string!')

    period_df.attrs['Name'] = df_name

    print(f'{period_df.attrs["Name"]} tem {period_df.shape[0]} linhas e {period_df.shape[1]} colunas.')

    return period_df.round(2)

# criar as medias diarias, semanal e mensal
my_csv = {'iguape_epw': 'iguape_epw',
          'inmet_2019': 'inmet_2019',
          'inmet_2020': 'inmet_2020',
          'inmet_2021': 'inmet_2021',
          'inmet_2022': 'inmet_2022',
          'inmet_2023': 'inmet_2023',
          'inmet_2024': 'inmet_2024',
         }

# calcular os valores médios por períodos
periodos = {'diaria': 'D', 'semanal': 'W', 'mensal': 'ME'}
datetime_column = 'Datetime'
ventilation_orientation = 'Ori_vento'

for key, value in my_csv.items():
    print(f'Carregando {value}.csv')
    df = pd.read_csv(f'{export_folder}{value}.csv',parse_dates=True)
    df[datetime_column] = pd.to_datetime(df[datetime_column])
    df.set_index(datetime_column, inplace=True)
    direcoes = ['N', 'NE', 'L', 'SE', 'S', 'SO', 'O', 'NO']
    df[ventilation_orientation] = df[ventilation_orientation].astype('category')
    
    for name, period in periodos.items():
        print(f'Calcular média {name} de {value}.csv')
        new_df = calculate_metrics_by_period(
            df=df,
            period=period,
            df_name=f'{key}_{name}'
        )
        new_df.dropna(inplace=True)
        new_df.to_csv(f'{export_folder}{key}_{name}.csv')

print('.\n.\n.\nCódigo concluído.')