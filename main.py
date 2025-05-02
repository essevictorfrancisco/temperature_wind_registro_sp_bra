import sys
from pathlib import Path
import pandas as pd

# Adiciona a pasta 'src' ao sys.path
sys.path.append(str(Path(__file__).resolve().parent / 'src'))

from loaders.epw_loader import load_epw
from loaders.inmet_loader import load_inmet
from processing.aggregation import aggregate_climate_data
from src.processing.apparent_temperature import calculate_apparent_temperature
from utils import save_dataframe
from config import EXPORT_DIR, RAW_INMET_DIR

def main() -> None:
    """Executa o pipeline principal de processamento e agregação climática."""

    # Processa dados do EPW
    epw_df = load_epw('BRA_SP_Iguape.869230_TMYx.2009-2023.epw')
    if epw_df is None or epw_df.empty:
        raise ValueError("Falha ao carregar dados do EPW.")
    save_dataframe(epw_df, 'iguape_epw', EXPORT_DIR)

    # Processa dados do INMET por ano
    inmet_anos = range(2019, 2025)
    for ano in inmet_anos:
        df = load_inmet(f'a712_iguape_{ano}a', f'a712_iguape_{ano}b', RAW_INMET_DIR)
        if df is None or df.empty:
            raise ValueError(f"Falha ao carregar dados do INMET {ano}.")
        save_dataframe(df, f'inmet_{ano}_horaria', EXPORT_DIR)

    # Agregações por período
    periods = {'horaria':'H', 'diaria': 'D', 'semanal': 'W', 'mensal': 'ME'}
    all_files = ['iguape_epw'] + [f'inmet_{ano}' for ano in inmet_anos]

    for file in all_files:
        csv_path = EXPORT_DIR / f"{file}.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Arquivo CSV não encontrado: {csv_path}")

        df = pd.read_csv(csv_path)
        if 'Datetime' not in df.columns:
            raise KeyError(f"Coluna 'Datetime' ausente no arquivo: {file}.csv")

        df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
        df.dropna(subset=['Datetime'], inplace=True)
        df.set_index('Datetime', inplace=True)
        df['Sensacao_termica'] = calculate_apparent_temperature(df)

        for period_name, freq in periods.items():
            agg_df = aggregate_climate_data(df, freq, f"{file}_{period_name}")
            if agg_df.empty:
                raise ValueError(f"DataFrame agregado vazio: {file}_{period_name}")
            save_dataframe(agg_df.reset_index(), agg_df.attrs['Name'], EXPORT_DIR)

if __name__ == '__main__':
    main()
