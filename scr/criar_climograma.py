import pandas as pd
import matplotlib.pyplot as plt

def load_climate_data():
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
        # converter data para datetime
        climate_data[df]['Datetime'] = pd.to_datetime(climate_data[df]['Datetime'])
        # usar coluna Datetime com Index do DataFrame
        climate_data[df].set_index(climate_data[df]['Datetime'])
        # criar a coluna para os meses baseado no Datetime
        climate_data[df]["Mês"] = climate_data[df]['Datetime'].dt.month.map(
            {1: 'JAN', 2: 'FEV', 3: 'MAR', 4: 'ABR', 5: 'MAI', 6: 'JUN',
             7: 'JUL', 8: 'AGO', 9: 'SET', 10: 'OUT', 11: 'NOV', 12: 'DEZ'}
        )
        
        climate_data[df].attrs['file_name'] = df
        if 'epw' in df:
            climate_data[df].attrs['graph_name'] = 'Climograma Iguape/SP (TMYx 2009-20023)'
        else:
            for year in range(2019,2025):
                year = str(year)
                if year in df:
                    climate_data[df].attrs['graph_name'] = f'Climograma Iguape/SP (INMET {year})'
    
    return climate_data

def gerar_climograma(df):
    # Criar figura e configurar eixos
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.set_xlabel('Meses do ano', fontsize=12)
    
    # Remover linhas verticais do grid
    ax1.xaxis.grid(False)  
    
    # Criar eixo de precipitação (eixo direito)
    ax1.bar(
        df['Mês'], df['Chuva_tot'],
        width=0.75, alpha=1.0, color='#2385CC', label='Precipitação'
    )
    
    ax1.yaxis.grid(False)  # <--- Linha crítica para remover grids verticais
    ax1.set_ylabel('Precipitação (mm)', fontsize=12, color='#000000')
    ax1.tick_params(axis='y', labelcolor='#000000')
    ax1.set_ylim(0, 600)
    ax1.legend(loc='upper right', frameon=True)
    
    # Plotar temperaturas (eixo esquerdo)
    ax2 = ax1.twinx()
    ax2.plot(
        df['Mês'], df['Temp_max'],
        color='#d62728', label='Temp. Máxima', marker='^'
    )
    ax2.plot(
        df['Mês'], df['Temp_med'],
        color='#2ca02c', label='Temp. Média', marker='o'
    )
    ax2.plot(
        df['Mês'], df['Temp_min'],
        color='#9467bd', label='Temp. Mínima', marker='v'
    )
    
    ax2.set_ylabel('Temperatura (°C)', fontsize=12, color='#000000')
    ax2.tick_params(axis='y', labelcolor='#000000')
    ax2.set_ylim(0, 50)
    ax2.legend(loc='upper left', frameon=True)
    
    # colocar valores dos pontos
    colunas = ['Temp_max', 'Temp_med', 'Temp_min']
    
    for mes in range(df.shape[0]):
        ax1.annotate(
            text=str(df.at[mes,'Chuva_tot']),
            color='white',
            horizontalalignment='center',
            xy=(mes,10),
            # xy=(mes,df.at[mes,'Chuva_tot']/2),
        )
        
        for coluna in colunas:
            ax2.annotate(
                text=str(df.at[mes,coluna]),
                horizontalalignment='center',
                xy=(mes, df.at[mes,coluna]),
                xycoords='data',
                xytext=(0,10),
                textcoords='offset points'
            )
    
    # Ajustes finais
    ax1.spines['top'].set_visible(False) # tirar linha quadro superior do grafico 1
    ax2.spines['top'].set_visible(False) # tirar linha quadro superior do grafico 2
    
    plt.title(df.attrs["graph_name"], fontsize=14, pad=20)
    plt.tight_layout()
    
    plt.savefig(f'../img/{df.attrs['file_name']}.png')
    # plt.show()