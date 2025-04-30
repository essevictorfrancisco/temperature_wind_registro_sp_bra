import pandas as pd
from src.constants import ORI_VENTO

def aggregate_climate_data(
    df: pd.DataFrame, period: str, name: str
) -> pd.DataFrame:
    """
    Agrega dados climáticos por período com estatísticas descritivas.

    Args:
        df (pd.DataFrame): DataFrame com dados originais.
        period (str): Frequência (D, W, M etc).
        name (str): Nome para atribuição no atributo 'Name'.

    Returns:
        pd.DataFrame: Dados agregados e renomeados.
    """
    if not isinstance(df, pd.DataFrame) or df.empty:
        raise ValueError("DataFrame de entrada inválido ou vazio.")

    if ORI_VENTO not in df.columns:
        raise KeyError("Coluna 'Ori_vento' ausente nos dados.")

    agg = {
        'Temp': ['max', 'min', 'mean', 'std'],
        'Umi': ['max', 'min', 'mean', 'std'],
        'Vel_vento': ['max', 'min', 'mean', 'std'],
        'Dir_vento': ['mean', 'std'],
        'Precipitacao': ['sum', 'std']
    }

    grouped = df.resample(period).agg(agg)
    grouped.columns = [f"{col}_{stat}" for col, stat in grouped.columns]

    moda_ori = df[ORI_VENTO].resample(period).apply(
        lambda x: x.mode().iloc[0] if not x.mode().empty else None
    )
    grouped[f'{ORI_VENTO}_moda'] = moda_ori

    grouped = grouped.rename(columns=lambda c: (
        c.replace('mean', 'med')
         .replace('sum', 'tot')
         .replace('median', 'mediana')
         .replace('std', 'dp')
    ))

    grouped.attrs['Name'] = name
    return grouped.round(1)