import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

EXPORT_DIR = Path(__file__).resolve().parent.parent / 'data_processed'
IMG_DIR = Path(__file__).resolve().parent.parent / 'img'
IMG_DIR.mkdir(parents=True, exist_ok=True)

# Mapeamento de rótulos mais legíveis para as colunas
COLUMN_LABELS = {
    'Temp': 'Temperatura',
    'Temp_med': 'Temperatura média',
    'Temp_max': 'Temperatura máxima',
    'Temp_min': 'Temperatura mínima',
    'Umi': 'Umidade',
    'Umi_med': 'Umidade média',
    'Precipitacao': 'Precipitação',
    'Precipitacao_tot': 'Precipitação total',
    'Ori_vento': 'Orientação do vento'
}

# Ordem padrão para os pontos cardeais do vento
ORDERED_WIND_DIRECTIONS = ['N', 'NE', 'E', 'SE', 'S', 'SO', 'O', 'NO']

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
            continue

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

def plot_histogram(df: pd.DataFrame, column: str, bins: int = 30, freq: str = '') -> None:
    """
    Plota histograma ou gráfico de barras para colunas numéricas ou categóricas.

    Args:
        df (pd.DataFrame): DataFrame com os dados.
        column (str): Nome da coluna para o histograma.
        bins (int): Número de bins do histograma.
        freq (str): Rótulo de frequência para o título.
    """
    if column not in df.columns:
        return

    col_data = df[column].dropna()
    if col_data.empty:
        return

    column_label = COLUMN_LABELS.get(column, column)

    plt.figure(figsize=(10, 5))
    if pd.api.types.is_numeric_dtype(col_data):
        plt.hist(col_data, bins=bins, color='#1f77b4', edgecolor='black')
    elif column == 'Ori_vento':
        counts = col_data.value_counts()
        # Garantir ordenação personalizada
        counts = counts.reindex(ORDERED_WIND_DIRECTIONS, fill_value=0)
        counts.plot.bar(color='#1f77b4', edgecolor='black')
        plt.xticks(rotation=0)
    else:
        col_data.value_counts().sort_index().plot.bar(color='#1f77b4', edgecolor='black')
        plt.xticks(rotation=45)

    plt.title(f"{df.attrs['graph_name']} - {column_label} {freq}", fontsize=14)
    plt.xlabel(column_label)
    plt.ylabel('Frequência')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    for ext in ['png', 'svg']:
        filename = f"hist_{df.attrs['file_name']}_{column}.{ext}".lower()
        plt.savefig(IMG_DIR / filename)
    plt.close()

def main():
    freq_types = ['horaria', 'diaria', 'semanal', 'mensal']
    years = range(2019, 2025)

    files = [f'iguape_epw_{f}.csv' for f in freq_types[1:]]  # exclui horária epw
    for freq in freq_types:
        files += [f'inmet_{year}_{freq}.csv' for year in years]

    columns = list(COLUMN_LABELS.keys())

    data = load_csv_data(files)
    for name, df in data.items():
        freq_tag = name.split('_')[-1] if '_' in name else ''
        for col in columns:
            if col in df.columns:
                values = df[col].dropna()
                try:
                    bins = min(30, max(10, int(values.max() - values.min()))) if not values.empty and pd.api.types.is_numeric_dtype(values) else 8
                except:
                    bins = 8
                plot_histogram(df, col, bins, freq_tag)

if __name__ == '__main__':
    main()
