import pandas as pd
from pathlib import Path
from src.utils import set_wind_direction
from src.constants import COLUMNS_RELEVANT, ORI_VENTO

def load_inmet(file_a: str, file_b: str, base_dir: Path) -> pd.DataFrame:
    """
    Carrega e concatena dois arquivos INMET, criando DataFrame padronizado.

    Args:
        file_a (str): Nome do primeiro CSV.
        file_b (str): Nome do segundo CSV.
        base_dir (Path): Diretório onde estão os arquivos.

    Returns:
        pd.DataFrame: Dados climáticos consolidados.
    """
    def parse_file(file: str) -> pd.DataFrame:
        path = base_dir / f"{file}.csv"
        if not path.exists():
            raise FileNotFoundError(f"Arquivo INMET não encontrado: {path}")

        df = pd.read_csv(path, sep=';', decimal=',')

        try:
            date_parts = df['Data'].str.split('/', expand=True).astype(int)
            df['Datetime'] = pd.to_datetime({
                'year': date_parts[2],
                'month': date_parts[1],
                'day': date_parts[0],
                'hour': df['Hora (UTC)'] // 100
            }, errors='raise')
        except Exception as e:
            raise ValueError("Erro ao converter datas INMET") from e

        return df

    df1 = parse_file(file_a)
    df2 = parse_file(file_b)
    df = pd.concat([df1, df2], ignore_index=True)

    df = df[[
        'Datetime', 'Temp. Ins. (C)', 'Umi. Ins. (%)',
        'Vel. Vento (m/s)', 'Dir. Vento (m/s)', 'Chuva (mm)'
    ]]
    df.columns = COLUMNS_RELEVANT
    df[ORI_VENTO] = set_wind_direction(df[COLUMNS_RELEVANT[4]])

    return df[df['Temp'].notnull()]
