import pandas as pd
from src.config import RAW_EPW_DIR
from src.utils import set_wind_direction
from src.constants import COLUMNS_RELEVANT, ORI_VENTO

def load_epw(filename: str) -> pd.DataFrame:
    """
    Carrega dados EPW e converte para DataFrame padronizado.

    Args:
        filename (str): Nome do arquivo EPW.

    Returns:
        pd.DataFrame: Dados climáticos formatados.

    Raises:
        FileNotFoundError: Se o arquivo não existir.
        ValueError: Se estrutura dos dados estiver incorreta.
    """
    path = RAW_EPW_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Arquivo EPW não encontrado: {filename}")

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

    df = pd.read_csv(path, skiprows=8, names=columns)
    df['Year'] = 2001
    df['Hour'] = df['Hour[1-24]'] - 1
    df['Minute'] = 0

    try:
        df['Datetime'] = pd.to_datetime({
            'year': df['Year'],
            'month': df['Month'],
            'day': df['Day'],
            'hour': df['Hour'],
            'minute': df['Minute']
        }, errors='raise')
    except Exception as e:
        raise ValueError("Erro ao converter datas no EPW") from e

    df = df[[
        'Datetime', 'Dry Bulb Temperature', 'Relative Humidity',
        'Wind Speed', 'Wind Direction', 'Liquid Precipitation Depth'
    ]]
    df.columns = COLUMNS_RELEVANT
    df[ORI_VENTO] = set_wind_direction(df[COLUMNS_RELEVANT[4]])

    return df
