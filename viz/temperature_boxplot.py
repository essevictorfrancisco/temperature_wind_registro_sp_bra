# viz/temperature_boxplot.py
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

# Diretórios de dados e saída de imagens
EXPORT_DIR = (
    Path(__file__).resolve().parent.parent / 'data_processed'
)
# fallback se não existir
if not EXPORT_DIR.exists():
    EXPORT_DIR = Path(__file__).resolve().parent.parent / 'climate_csv'
IMG_DIR = Path(__file__).resolve().parent.parent / 'img'
IMG_DIR.mkdir(parents=True, exist_ok=True)

# Ordem das direções do vento para rotulagem
ORDERED_WIND_DIRECTIONS = ['N', 'NE', 'L', 'SE', 'S', 'SO', 'O', 'NO']


def load_temperature_data(files: list[str]) -> dict:
    """
    Carrega CSVs com colunas 'Ori_vento' e 'Temp'.

    Args:
        files (list[str]): Nomes de arquivos CSV.
    Returns:
        dict: chave=nome do arquivo, valor=DataFrame carregado.
    """
    data = {}
    for fname in files:
        path = EXPORT_DIR / fname
        if not path.exists():
            print(f"Aviso: arquivo não encontrado {path}")
            continue
        df = pd.read_csv(path)
        if 'Ori_vento' not in df.columns or 'Temp' not in df.columns:
            print(f"Ignorando {fname}, colunas necessárias ausentes")
            continue
        df.attrs['file_name'] = path.stem
        df.attrs['graph_name'] = (
            f"Boxplot Temp vs Ori_vento (EPW)"
            if 'epw' in fname else
            f"Boxplot Temp vs Ori_vento (INMET {fname[6:10]})"
        )
        data[path.stem] = df
    return data


def plot_boxplot(df: pd.DataFrame) -> None:
    """
    Gera e salva boxplot de Temp por Ori_vento.

    Args:
        df (pd.DataFrame): DataFrame com 'Ori_vento' e 'Temp'.
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(
        x='Ori_vento', y='Temp', data=df.dropna(subset=['Ori_vento','Temp']),
        order=ORDERED_WIND_DIRECTIONS, ax=ax, whis=(0, 100)
    )
    ax.set_title(df.attrs['graph_name'], fontsize=14)
    ax.set_xlabel('Orientação do Vento')
    ax.set_ylabel('Temperatura (°C)')
    ax.set_ylim(0, 50)
    plt.tight_layout()

    output = IMG_DIR / f"boxplot_temp_{df.attrs['file_name']}.png"
    fig.savefig(output, dpi=300)
    plt.close(fig)
    print(f"Salvo boxplot: {output}")


def main() -> None:
    # Frequências disponíveis
    freqs = ['diaria', 'semanal', 'mensal']
    years = range(2019, 2025)
    #files = [f'iguape_epw_{f}.csv' for f in freqs]
    files = [f'iguape_epw.csv'] + [f'inmet_{y}.csv' for y in years]
    #for f in freqs:
    #    files += [f'inmet_{y}_{f}.csv' for y in years]

    data = load_temperature_data(files)
    if not data:
        print("Nenhum DataFrame carregado para boxplot.")
    for df in data.values():
        plot_boxplot(df)


if __name__ == '__main__':
    main()
