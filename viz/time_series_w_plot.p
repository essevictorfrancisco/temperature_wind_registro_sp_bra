# viz/time_series_plot.py
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

EXPORT_DIR = Path(__file__).resolve().parent.parent / 'climate_csv'
IMG_DIR = Path(__file__).resolve().parent.parent / 'img'
IMG_DIR.mkdir(parents=True, exist_ok=True)

def load_series_data(files: list[str]) -> dict:
    """
    Carrega arquivos de séries temporais.

    Args:
        files (list): Lista de nomes de arquivos CSV.

    Returns:
        dict: Nome base como chave, DataFrame como valor.
    """
    data = {}
    for file in files:
        path = EXPORT_DIR / file
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")

        df = pd.read_csv(path)
        df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
        df.dropna(subset=['Datetime'], inplace=True)
        df.set_index('Datetime', inplace=True)

        name = file.replace('.csv', '')
        df.attrs['file_name'] = name
        df.attrs['graph_name'] = (
            f"Série Temporal - Iguape/SP (EPW)"
            if 'epw' in file else
            f"Série Temporal - Iguape/SP ({file[6:10]})"
        )
        data[name] = df
    return data

def plot_time_series(df: pd.DataFrame, col: str) -> None:
    """
    Plota série temporal da coluna escolhida.

    Args:
        df (pd.DataFrame): Dados agregados.
        col (str): Nome da coluna para plotar.
    """
    if col not in df.columns:
        raise KeyError(f"Coluna '{col}' não encontrada no DataFrame.")

    plt.figure(figsize=(14, 5))
    plt.plot(df.index, df[col], label=col, color='#1f77b4')
    plt.title(f"{df.attrs['graph_name']} - {col}", fontsize=14)
    plt.xlabel('Data')
    plt.ylabel(col)
    plt.grid(True)
    plt.tight_layout()
    output_path = IMG_DIR / f"{df.attrs['file_name']}_{col}.png"
    plt.savefig(output_path)
    plt.close()

def main():
    diaria_files = [
        'iguape_epw_diaria.csv',
        'inmet_2019_diaria.csv',
        'inmet_2020_diaria.csv',
        'inmet_2021_diaria.csv',
        'inmet_2022_diaria.csv',
        'inmet_2023_diaria.csv',
        'inmet_2024_diaria.csv'
    ]

    semanal_files = [
        'iguape_epw_semanal.csv',
        'inmet_2019_semanal.csv',
        'inmet_2020_semanal.csv',
        'inmet_2021_semanal.csv',
        'inmet_2022_semanal.csv',
        'inmet_2023_semanal.csv',
        'inmet_2024_semanal.csv'
    ]

    columns_to_plot = ['Temp_med', 'Umi_med', 'Precipitacao_tot']

    for freq_name, file_list in [('diaria', diaria_files), ('semanal', semanal_files)]:
        data = load_series_data(file_list)
        for name, df in data.items():
            for col in columns_to_plot:
                if col in df.columns:
                    df.attrs['file_name'] = f"{name}_{freq_name}"
                    plot_time_series(df, col)

if __name__ == '__main__':
    main()
