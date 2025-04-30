import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

EXPORT_DIR = Path(__file__).resolve().parent.parent / 'climate_csv'
IMG_DIR = Path(__file__).resolve().parent.parent / 'img'
IMG_DIR.mkdir(parents=True, exist_ok=True)

def load_csv_data(files: list[str]) -> dict:
    """
    Carrega múltiplos arquivos CSV para análise de distribuição.

    Args:
        files (list[str]): Lista de nomes de arquivos CSV.

    Returns:
        dict: Nome base como chave e DataFrame como valor.
    """
    data = {}
    for file in files:
        path = EXPORT_DIR / file
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")

        df = pd.read_csv(path)
        name = file.replace('.csv', '')
        df.attrs['file_name'] = name
        df.attrs['graph_name'] = (
            f"Distribuição - Iguape/SP (EPW)"
            if 'epw' in file else
            f"Distribuição - Iguape/SP ({file[6:10]})"
        )
        data[name] = df
    return data

def plot_histogram(df: pd.DataFrame, column: str, bins: int = 30) -> None:
    """
    Plota histograma para uma coluna específica do DataFrame.

    Args:
        df (pd.DataFrame): DataFrame com os dados.
        column (str): Nome da coluna para o histograma.
        bins (int): Número de bins do histograma.
    """
    if column not in df.columns:
        return

    plt.figure(figsize=(10, 5))
    plt.hist(df[column].dropna(), bins=bins, color='#1f77b4', edgecolor='black')
    plt.title(f"{df.attrs['graph_name']} - {column}", fontsize=14)
    plt.xlabel(column)
    plt.ylabel('Frequência')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    filename = f"{df.attrs['file_name']}_hist_{column}.png"
    plt.savefig(IMG_DIR / filename)
    plt.close()

def main():
    freq_types = ['horaria', 'diaria', 'semanal', 'mensal']
    years = range(2019, 2025)

    files = [f'iguape_epw_{f}.csv' for f in freq_types[1:]]  # diária, semanal, mensal
    for freq in freq_types:
        files += [f'inmet_{year}_{freq}.csv' for year in years]

    columns = [
        'Temp', 'Temp_med', 'Temp_max', 'Temp_min',
        'Umi', 'Umi_med', 'Precipitacao', 'Precipitacao_tot'
    ]

    data = load_csv_data(files)
    for name, df in data.items():
        for col in columns:
            if col in df.columns:
                plot_histogram(df, col)

if __name__ == '__main__':
    main()
