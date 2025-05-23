import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

EXPORT_DIR = Path(__file__).resolve().parent.parent / 'data_processed'
IMG_DIR = Path(__file__).resolve().parent.parent / 'img'
IMG_DIR.mkdir(parents=True, exist_ok=True)

MONTH_MAP = {
    1: 'JAN', 2: 'FEV', 3: 'MAR', 4: 'ABR', 5: 'MAI', 6: 'JUN',
    7: 'JUL', 8: 'AGO', 9: 'SET', 10: 'OUT', 11: 'NOV', 12: 'DEZ'
}

class ClimographGenerator:
    def __init__(self, export_dir: Path, img_dir: Path) -> None:
        self.export_dir = export_dir
        self.img_dir = img_dir
        self.img_dir.mkdir(parents=True, exist_ok=True)

    def load_climate_data(self) -> dict:
        files = ['iguape_epw_mensal.csv'] + [f'inmet_{ano}_mensal.csv' for ano in range(2019, 2025)]
        data = {}

        for file in files:
            path = self.export_dir / file
            if not path.exists():
                raise FileNotFoundError(f"Arquivo não encontrado: {path}")

            df = pd.read_csv(path)
            if 'Datetime' not in df.columns:
                raise KeyError(f"Coluna 'Datetime' ausente em {file}")

            df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
            df.dropna(subset=['Datetime'], inplace=True)
            df['Mês'] = df['Datetime'].dt.month.map(MONTH_MAP)

            name = file.replace('.csv', '')
            df.attrs['file_name'] = name
            df.attrs['graph_name'] = (
                f"Climograma Iguape/SP (TMYx 2009-2023)"
                if 'epw' in file else
                f"Climograma Iguape/SP (INMET {file[6:10]})"
            )
            data[name] = df

        return data

    def gerar_climograma(self, df: pd.DataFrame) -> None:
        if df.empty:
            raise ValueError("DataFrame fornecido está vazio.")

        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax1.set_xlabel('Meses do ano', fontsize=12)
        ax1.xaxis.grid(False)

        ax1.bar(
            df['Mês'], df['Precipitacao_tot'],
            width=0.75, alpha=1.0, color='#2385CC', label='Precipitação'
        )
        ax1.set_ylabel('Precipitação (mm)', fontsize=12, color='#000000')
        ax1.tick_params(axis='y', labelcolor='#000000')
        ax1.set_ylim(0, 600)
        ax1.legend(loc='upper right', frameon=True)
        ax1.yaxis.grid(False)

        ax2 = ax1.twinx()
        ax2.plot(df['Mês'], df['Temp_max'], color='#d62728', label='Temp. Máxima', marker='^')
        ax2.plot(df['Mês'], df['Temp_med'], color='#2ca02c', label='Temp. Média', marker='o')
        ax2.plot(df['Mês'], df['Temp_min'], color='#9467bd', label='Temp. Mínima', marker='v')

        ax2.set_ylabel('Temperatura (°C)', fontsize=12, color='#000000')
        ax2.tick_params(axis='y', labelcolor='#000000')
        ax2.set_ylim(0, 50)
        ax2.legend(loc='upper left', frameon=True)

        for i in range(len(df)):
            prec = df.iloc[i]['Precipitacao_tot']
            if pd.notna(prec):
                ax1.annotate(str(int(prec)), xy=(i, 10), color='white', ha='center')
            for col in ['Temp_max', 'Temp_med', 'Temp_min']:
                val = df.iloc[i][col]
                if pd.notna(val):
                    ax2.annotate(
                        str(int(val)),
                        xy=(i, val),
                        xytext=(0, 10),
                        textcoords='offset points',
                        ha='center'
                    )

        ax1.spines['top'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        plt.title(df.attrs['graph_name'], fontsize=14, pad=20)
        plt.tight_layout()
        
        for ext in ['png', 'svg']:
            output_path = self.img_dir / f"climograma_{df.attrs['file_name']}.{ext}"
            plt.savefig(output_path)
        plt.close()

def main() -> None:
    climogen = ClimographGenerator(EXPORT_DIR, IMG_DIR)
    dados = climogen.load_climate_data()
    for nome, df in dados.items():
        climogen.gerar_climograma(df)
    print("Climogramas gerados com sucesso.")

if __name__ == '__main__':
    main()
