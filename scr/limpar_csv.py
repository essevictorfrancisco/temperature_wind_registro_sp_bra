"""
Módulo para processamento de dados climáticos em formato EPW e INMET.
"""

from pathlib import Path
import pandas as pd
import numpy as np

epw_folder = '../epw_raw/'
inmet_folder = '../inmet_raw/'
export_folder = '../climate_csv/'

def epw_to_pandas(epw_path: str) -> pd.DataFrame | None:
    """
    Converte arquivo EPW para DataFrame pandas com tratamento de erros.

    Args:
        epw_path (str): Caminho do arquivo .epw

    Returns:
        pd.DataFrame | None: DataFrame com dados ou None se erro

    Raises:
        FileNotFoundError: Se arquivo não existir
        ValueError: Se extensão for inválida
    """
    path = Path(epw_path)
    
    # Validações iniciais
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {epw_path}")
    if path.suffix.lower() != ".epw":
        raise ValueError("Extensão inválida. Esperado .epw")

    # Mapeamento de colunas
    columns = [
        'Year', 'Month', 'Day', 'Hour[1-24]', 'Minute', 'Source flags',
        'Dry Bulb Temperature', 'Dew_Point Temperature', 'Relative Humidity',
        'Atmospheric Station Pressure', 'Extraterrestrial Horizontal Radiation',
        'Extraterrestrial Direct Normal Radiation',
        'Horizontal Infrared Radiation Intensity', 'Global Horizontal Radiation',
        'Direct Normal Radiation', 'Diffuse Horizontal Radiation',
        'Global Horizontal Illuminance', 'Direct Normal Illuminance',
        'Diffuse Horizontal Illuminance', 'Zenith Luminance', 'Wind Direction',
        'Wind Speed', 'Total Sky Cover', 'Opaque Sky Cover', 'Visibility',
        'Ceiling Height', 'Present Weather Observation', 'Present Weather Codes',
        'Precipitable Water', 'Aerosol Optical Depth', 'Snow Depth',
        'Days Since Last Snowfall', 'Albedo', 'Liquid Precipitation Depth',
        'Liquid Precipitation Quantity'
    ]

    # Leitura do arquivo
    df = pd.read_csv(path, skiprows=8, names=columns)
    
    # Processamento de datas
    df['Year'] = 2000
    df['Hour'] = df['Hour[1-24]'] - 1
    df['Datetime'] = pd.to_datetime(
        df[['Year', 'Month', 'Day', 'Hour', 'Minute']],
        format='%Y-%m-%d %H:%M'
    )
    
    return df

def inmet_to_pandas(file_path: str | Path) -> pd.DataFrame:
    """
    Carrega dados do INMET de arquivo CSV formatando datas e horas.

    Processa colunas de data e hora para criar um índice datetime unificado.
    Assume formato brasileiro DD/MM/YYYY na coluna 'Data' e HHMM em 'Hora (UTC)'.

    Args:
        file_path (str | Path): Caminho para o arquivo CSV do INMET

    Returns:
        pd.DataFrame: DataFrame com dados processados e coluna datetime

    Raises:
        FileNotFoundError: Se o arquivo não existir
        ValueError: Se extensão inválida ou estrutura de dados incorreta
        KeyError: Se colunas obrigatórias não estiverem presentes
    """
    # Validação inicial do arquivo
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo INMET não encontrado: {file_path}")
    if path.suffix.lower() != ".csv":
        raise ValueError("Extensão inválida. Arquivo deve ser .csv")

    # Carregamento dos dados com tratamento de tipos
    try:
        df = pd.read_csv(
            path,
            sep=';',
            decimal=','
        )
    except KeyError as e:
        raise ValueError(f"Coluna obrigatória ausente: {e}") from e

    # Processamento da data com verificação de formato
    date_parts = df['Data'].str.split('/', expand=True)
    if date_parts.shape[1] != 3:
        raise ValueError("Formato de data inválido. Esperado DD/MM/YYYY")
    
    # Conversão para inteiros com tratamento de erros
    try:
        df = df.assign(
            Day=date_parts[0].astype('int8'),
            Month=date_parts[1].astype('int8'),
            Year=date_parts[2].astype('int16'),
            Hour=df['Hora (UTC)'] // 100,
            Minute=0  # INMET não fornece minutos
        )
    except ValueError as e:
        raise ValueError("Valor numérico inválido nas colunas de tempo") from e

    # Criação da coluna datetime otimizada
    try:
        df['Datetime'] = pd.to_datetime(
            df[['Year', 'Month', 'Day', 'Hour', 'Minute']],
            format='%Y-%m-%d %H:%M'
        )
    except pd.errors.OutOfBoundsDatetime as e:
        raise ValueError("Data fora do intervalo suportado (1677-2262)") from e

    return df[df[df.columns[2]].notna()]

def set_wind_direction(wind_series: pd.Series) -> pd.Series:
    """Converte direção angular do vento em orientação categórica (8 pontos cardeais).

    Args:
        wind_series (pd.Series): Série contendo ângulos de direção do vento em graus (0-360).

    Returns:
        pd.Series: Série categórica com direções em português ('N', 'NE', ..., 'NO').

    Exemplos:
        >>> direcoes = pd.Series([0, 90, 180, 270, 350])
        >>> set_wind_direction(direcoes)
        0     N
        1     L
        2     S
        3     O
        4     N
        dtype: category
    """
    # Mapeamento de setores para direções
    direcoes = ['N', 'NE', 'L', 'SE', 'S', 'SO', 'O', 'NO']
    
    # Ajuste para alinhar setores de 45° com os pontos cardeais
    angulos_ajustados = (wind_series + 22.5) % 360
    setores = np.floor(angulos_ajustados / 45)#.astype('int32')
    
    # Criar série categórica ordenada
    return pd.Categorical(
        values=pd.Series(setores).map(dict(enumerate(direcoes))),
        categories=direcoes,
        ordered=True
    )

def slice_dataframe(
    dataframe: pd.DataFrame,
    columns: list[str],
    name: str = ''
) -> pd.DataFrame | None:
    """
    Filtra colunas específicas do DataFrame.

    Args:
        dataframe (pd.DataFrame): DataFrame original
        columns (list[str]): Lista de colunas para manter
        name (str): Nome para atribuir ao DataFrame

    Returns:
        pd.DataFrame | None: DataFrame filtrado ou None se erro
    """
    if not isinstance(dataframe, pd.DataFrame) or not isinstance(columns, list):
        raise ValueError("Coluna não encontrada no DataFrame")
        return None

    try:
        filtered_df = dataframe[columns].copy()
        filtered_df.attrs['Name'] = name
        return filtered_df
    except KeyError as e:
        print(f"Erro ao filtrar colunas: {e}")
        return None


def calculate_n_percent_rows(dataframe: pd.DataFrame, percent: float) -> int:
    """
    Calcula número de linhas equivalente a uma porcentagem do total.

    Args:
        dataframe (pd.DataFrame): DataFrame de entrada
        percent (float): Percentual desejado (0.0 a 1.0)

    Returns:
        int: Número de linhas equivalente à porcentagem
    """
    if not isinstance(percent, (int, float)) or not 0 <= percent <= 1:
        raise ValueError("Percentual deve ser numérico entre 0 e 1")
    
    return int(dataframe.shape[0] * percent)


def slice_sorted_dataframe(
    dataframe: pd.DataFrame,
    sort_by: str,
    ascending: bool = True,
    percent: float = 0.2,
    name: str = ''
) -> pd.DataFrame | None:
    """
    Ordena e seleciona top N% de um DataFrame.

    Args:
        dataframe (pd.DataFrame): DataFrame original
        sort_by (str): Coluna para ordenação
        ascending (bool): Ordem crescente/decrescente
        percent (float): Percentual de linhas a selecionar
        name (str): Nome para atribuir ao DataFrame

    Returns:
        pd.DataFrame | None: DataFrame processado ou None se erro
    """
    try:
        n_rows = calculate_n_percent_rows(dataframe, percent)
        sorted_df = dataframe.sort_values(
            by=sort_by, 
            ascending=ascending
        ).iloc[:n_rows].copy()
        sorted_df.attrs['Name'] = name
        return sorted_df
    except Exception as e:
        print(f"Erro ao processar DataFrame: {e}")
        return None


def save_as_csv(dataframe: pd.DataFrame, folder_path: str) -> None:
    """
    Salva DataFrame em arquivo CSV com nome específico.

    Args:
        dataframe (pd.DataFrame): DataFrame a ser salvo
        folder_path (str): Pasta de destino

    Raises:
        ValueError: Se caminho inválido ou DataFrame vazio
    """
    if not dataframe.empty and isinstance(dataframe, pd.DataFrame):
        folder = Path(folder_path).resolve()
        folder.mkdir(parents=True, exist_ok=True)
        file_path = folder / f"{dataframe.attrs.get('Name', 'data')}.csv"
        dataframe.to_csv(file_path, index=False)
    else:
        raise ValueError("DataFrame inválido ou vazio para exportação")

# definir pasta de trabalho
epw_folder = '../epw_raw/'
inmet_folder = '../inmet_raw/'
export_folder = '../climate_csv/'

# limpando o EPW
iguape_old_epw = epw_to_pandas(
    f'{epw_folder}BRA_SP_Iguape.869230_TMYx.2009-2023.epw'
)

iguape_epw = slice_dataframe(
    dataframe=iguape_old_epw,
    columns=[
        'Datetime', 'Dry Bulb Temperature', 'Relative Humidity',
        'Wind Speed', 'Wind Direction', 'Liquid Precipitation Depth'
    ],
    name='iguape_epw'
)

# renomeando as colunas
iguape_epw.columns = [
    'Datetime', 'Temp', 'Umi', 'Vel_vento', 'Dir_vento', 'Precipitacao'
]

# adicionar orientação da ventilação
ori_vento = 'Ori_vento'
iguape_epw[ori_vento] = set_wind_direction(iguape_epw['Dir_vento'])

# salvar arquivo
iguape_epw.attrs['Name'] = 'iguape_epw'
save_as_csv(iguape_epw,export_folder)
print(f'{iguape_epw.attrs["Name"]} foi salvo.')

del iguape_old_epw

# limpando os arquivos INMET
# definindo os arquivos para importação
inmet_2019 = {'inmet_2019':('a712_iguape_2019a','a712_iguape_2019b')}
inmet_2020 = {'inmet_2020':('a712_iguape_2020a','a712_iguape_2020b')}
inmet_2021 = {'inmet_2021':('a712_iguape_2021a','a712_iguape_2021b')}
inmet_2022 = {'inmet_2022':('a712_iguape_2022a','a712_iguape_2022b')}
inmet_2023 = {'inmet_2023':('a712_iguape_2023a','a712_iguape_2023b')}
inmet_2024 = {'inmet_2024':('a712_iguape_2024a','a712_iguape_2024b')}

inmet_dados = (
    inmet_2019,inmet_2020,inmet_2021,inmet_2022,inmet_2023,inmet_2024
)

# criar os dataframes
for item in inmet_dados:
    for key in item.keys():
        df1 = inmet_to_pandas(f'{inmet_folder}{item[key][0]}.csv')
        df2 = inmet_to_pandas(f'{inmet_folder}{item[key][1]}.csv')
        # juntando os dataframes
        df3 = pd.concat([df1,df2])
        # dando um nome para o dataframe
        df3.attrs['Name'] = key
        # selecionando as colunas usadas
        df3 = df3[[
            'Datetime', 'Temp. Ins. (C)', 'Umi. Ins. (%)', 'Vel. Vento (m/s)',
            'Dir. Vento (m/s)', 'Chuva (mm)'
        ]]
        # renomeando as colunas
        df3.columns = [
            'Datetime', 'Temp', 'Umi', 'Vel_vento', 'Dir_vento', 'Precipitacao'
        ]

        # adicionar orientação do vento
        df3[ori_vento] = set_wind_direction(df3['Dir_vento'])
        
        # removendo as colunas vazias
        df3 = df3[df3['Temp'].notnull()]
        
        save_as_csv(df3,export_folder)
        print(f'{df3.attrs["Name"]} foi salvo.')
        
        del df1, df2, df3

# novos dataframes com os 10% mais quente e frio
iguape_10p_cold = slice_sorted_dataframe(
    dataframe=iguape_epw,
    sort_by='Temp',
    ascending=True,
    percent=0.1,
    name='iguape_cold_hours'
)

iguape_10p_hot = slice_sorted_dataframe(
    dataframe=iguape_epw,
    sort_by='Temp',
    ascending=False,
    percent=0.1,
    name='iguape_hot_hours'
)

# salvar os DataFrame em csv
for df in (iguape_10p_cold, iguape_10p_hot):
    save_as_csv(df, export_folder)
    # limpando a memoria
    print(f'{df.attrs["Name"]} foi salvo.')
    del df

print('.\n.\n.\nCódigo concluído.')