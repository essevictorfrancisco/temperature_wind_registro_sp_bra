import pandas as pd
import matplotlib.pyplot as plt
from windrose import WindroseAxes
from pathlib import Path

EXPORT_DIR = Path(__file__).resolve().parent.parent / 'climate_csv'
IMG_DIR = Path(__file__).resolve().parent.parent / 'img'
IMG_DIR.mkdir(parents=True, exist_ok=True)

def load_wind_data(files: list[str]) -> dict:
    """
    Carrega arquivos contendo dados de vento para plotar rosa dos ventos.

    Args:
        files (list[str]): Lista de arquivos CSV com vento.

    Returns:
        dict: Nome base como chave, DataFrame como valor.
    """
    data = {}
    for file in files:
        path = EXPORT_DIR / file
        if not path.exists():
            continue

        df = pd.read_csv(path)
        if 'Vel_vento' not in df.columns or 'Dir_vento' not in df.columns:
            continue

        name = file.replace('.csv', '')
        df.attrs['file_name'] = name
        df.attrs['graph_name'] = (
            f"Rosa dos Ventos - Iguape/SP (EPW)"
            if 'epw' in file else
            f"Rosa dos Ventos - Iguape/SP ({file[6:10]})"
        )
        data[name] = df
    return data

def plot_windrose(df: pd.DataFrame) -> None:
    """
    Gera e salva uma rosa dos ventos a partir do DataFrame.

    Args:
        df (pd.DataFrame): Dados com colunas 'Vel_vento' e 'Dir_vento'.
    """
    wind = df['Vel_vento'].dropna()
    direction = df['Dir_vento'].dropna()

    if wind.empty or direction.empty:
        return

    fig = plt.figure(figsize=(7, 7))
    ax = WindroseAxes.from_ax()
    ax.bar(direction, wind, normed=True, opening=0.8, edgecolor='white')
    ax.set_legend()
    plt.title(df.attrs['graph_name'], fontsize=13, pad=20)

    output_path = IMG_DIR / f"{df.attrs['file_name']}_windrose.png"
    plt.savefig(output_path)
    plt.close()

def main():
    freq_types = ['horaria', 'diaria', 'semanal', 'mensal']
    years = range(2019, 2025)

    files = [f'iguape_epw_{f}.csv' for f in freq_types[1:]]
    for freq in freq_types:
        files += [f'inmet_{year}_{freq}.csv' for year in years]

    data = load_wind_data(files)
    for name, df in data.items():
        plot_windrose(df)

if __name__ == '__main__':
    main()
