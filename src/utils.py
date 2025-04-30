import pandas as pd
import numpy as np
from pathlib import Path
from src.constants import CARDINAL_DIRECTIONS

def set_wind_direction(wind_series: pd.Series) -> pd.Categorical:
    """
    Converte direção angular em direção cardinal categórica ordenada.

    Args:
        wind_series (pd.Series): Série de ângulos (0 a 360).

    Returns:
        pd.Categorical: Direções cardinais ('N', 'NE', ...).
    """
    if wind_series is None or wind_series.empty:
        raise ValueError("Série de vento vazia ou inválida.")

    adjusted_angles = (wind_series + 22.5) % 360
    sectors = np.floor(adjusted_angles / 45)
    return pd.Categorical(
        values=pd.Series(sectors).map(dict(enumerate(CARDINAL_DIRECTIONS))),
        categories=CARDINAL_DIRECTIONS,
        ordered=True
    )

def save_dataframe(df: pd.DataFrame, name: str, folder: Path) -> None:
    """
    Salva DataFrame como CSV, validando conteúdo.

    Args:
        df (pd.DataFrame): Dados a salvar.
        name (str): Nome do arquivo.
        folder (Path): Diretório de saída.

    Raises:
        ValueError: Se o DataFrame estiver vazio.
    """
    if not isinstance(df, pd.DataFrame) or df.empty:
        raise ValueError(f"DataFrame {name} é inválido ou vazio.")

    folder.mkdir(parents=True, exist_ok=True)
    df.to_csv(folder / f"{name}.csv", index=False)
