import pandas as pd

# lista dos arquivos
climate_monthly_files = [
    'iguape_epw_mensal.csv',
    'inmet_2019_mensal.csv',
    'inmet_2020_mensal.csv',
    'inmet_2021_mensal.csv',
    'inmet_2022_mensal.csv',
    'inmet_2023_mensal.csv',
    'inmet_2024_mensal.csv'
]

# transformar o arquivos em dataframes
climate_data = {
    file_name[:-4] : pd.read_csv(f'../climate_csv/{file_name}')
    for file_name in climate_monthly_files
}

# criar datetime index e coluna mês
for df in climate_data.keys():
    climate_data[df]['Datetime'] = pd.to_datetime(climate_data[df]['Datetime'])
    climate_data[df].set_index(climate_data[df]['Datetime'])
    climate_data[df]["Mês"] = climate_data[df]['Datetime'].dt.month.map(
        {1: 'JAN', 2: 'FEV', 3: 'MAR', 4: 'ABR', 5: 'MAI', 6: 'JUN',
         7: 'JUL', 8: 'AGO', 9: 'SET', 10: 'OUT', 11: 'NOV', 12: 'DEZ'}
    )

def gerar_climograma(df):
    # Criar figura e configurar eixos
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.set_xlabel('Meses do ano', fontsize=12)
    
    # Remover linhas verticais do grid
    ax1.xaxis.grid(False)  # <--- Linha crítica para remover grids verticais
    
    # Criar eixo de precipitação (eixo esquerdo)
    ax1.bar(
        df['Mês'], df['Chuva_tot'],
        width=0.5, alpha=0.5, color='#1f77b4', label='Precipitação'
    )
    
    ax1.yaxis.grid(False)  # <--- Linha crítica para remover grids verticais
    ax1.set_ylabel('Precipitação (mm)', fontsize=12, color='#000000')
    ax1.tick_params(axis='y', labelcolor='#000000')
    ax1.set_ylim(0, 550)
    ax1.legend(loc='upper right', frameon=True)
    
    # Criar eixo de precipitação (eixo direito)
    ax2 = ax1.twinx()
    # Plotar temperaturas (eixo esquerdo)
    ax2.plot(
        df['Mês'], df['Temp_max'],
        color='#d62728', label='Temp. Máxima'
    )
    ax2.plot(
        df['Mês'], df['Temp_med'],
        color='#2ca02c', label='Temp. Média'
    )
    ax2.plot(
        df['Mês'], df['Temp_min'],
        color='#9467bd', label='Temp. Mínima'
    )
    
    ax2.set_ylabel('Temperatura (°C)', fontsize=12, color='#000000')
    ax2.tick_params(axis='y', labelcolor='#000000')
    ax2.set_ylim(0, 45)
    ax2.legend(loc='upper left', frameon=True)
    
    
    # Ajustes finais
    plt.title('Climograma Iguape/SP', fontsize=14, pad=20)
    plt.tight_layout()
    plt.savefig('../img/climograma_iguape_epw.png')
    plt.show()