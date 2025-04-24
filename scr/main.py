from limpar_csv import *
from processamento_dados import *
from criar_climograma import *

epw_folder = '../epw_raw/'
inmet_folder = '../inmet_raw/'
export_folder = '../climate_csv/'

# limpando o EPW
iguape_old_epw = epw_to_pandas(
    f'{epw_folder}BRA_SP_Iguape.869230_TMYx.2009-2023.epw'
)

iguape_epw = slice_dataframe(
    dataframe=iguape_old_epw,
    columns=[
        'Datetime', 'Dry Bulb Temperature', 'Relative Humidity',
        'Wind Speed', 'Wind Direction', 'Liquid Precipitation Depth'
    ],
    name='iguape_all_hours'
)

# renomeando as colunas
iguape_epw.columns = [
    'Datetime', 'Temp', 'Umi', 'Vel_vento', 'Dir_vento', 'Chuva'
]

del iguape_old_epw

# novos dataframes com os 10% mais quente ou frio
iguape_10p_cold = slice_sorted_dataframe(
    dataframe=iguape_epw,
    sort_by='Temp',
    ascending=True,
    percent=0.1,
    name='iguape_cold_hours'
)

iguape_10p_hot = slice_sorted_dataframe(
    dataframe=iguape_epw,
    sort_by='Temp',
    ascending=False,
    percent=0.1,
    name='iguape_hot_hours'
)

# salvar os DataFrame em csv
for df in (iguape_epw, iguape_10p_cold, iguape_10p_hot):
    save_as_csv(df, export_folder)
    # limpando a memoria
    print(f'{df.attrs["Name"]} foi salvo.')
    del df

# limpando os arquivos INMET
inmet_2019 = {'inmet_2019':('a712_iguape_2019a','a712_iguape_2019b')}
inmet_2020 = {'inmet_2020':('a712_iguape_2020a','a712_iguape_2020b')}
inmet_2021 = {'inmet_2021':('a712_iguape_2021a','a712_iguape_2021b')}
inmet_2022 = {'inmet_2022':('a712_iguape_2022a','a712_iguape_2022b')}
inmet_2023 = {'inmet_2023':('a712_iguape_2023a','a712_iguape_2023b')}
inmet_2024 = {'inmet_2024':('a712_iguape_2024a','a712_iguape_2024b')}

inmet_dados = (
    inmet_2019,inmet_2020,inmet_2021,inmet_2022,inmet_2023,inmet_2024
)

# definindo as pasta de importação e exportação
for item in inmet_dados:
    for key in item.keys():
        df1 = inmet_to_pandas(f'{inmet_folder}{item[key][0]}.csv')
        df2 = inmet_to_pandas(f'{inmet_folder}{item[key][1]}.csv')
        # juntando os dataframes
        df3 = pd.concat([df1,df2])
        # dando um nome para o dataframe
        df3.attrs['Name'] = key
        # selecionando as colunas usadas
        df3 = df3[[
            'Datetime', 'Temp. Ins. (C)', 'Umi. Ins. (%)', 'Vel. Vento (m/s)',
            'Dir. Vento (m/s)', 'Chuva (mm)'
        ]]
        # renomeando as colunas
        df3.columns = [
            'Datetime', 'Temp', 'Umi', 'Vel_vento', 'Dir_vento', 'Chuva'
        ]
        # removendo as colunas vazias
        df3 = df3[df3['Temp'].notnull()]
        
        # preenchedo os valores vazios
        df3.fillna(value=0, inplace=True)
        
        save_as_csv(df3,export_folder)
        print(f'{df3.attrs["Name"]} foi salvo.')
        del df1, df2, df3

# criar as medias diarias, semanal e mensal
my_csv = {'iguape_epw': 'iguape_all_hours',
          'inmet_2019': 'inmet_2019',
          'inmet_2020': 'inmet_2020',
          'inmet_2021': 'inmet_2021',
          'inmet_2022': 'inmet_2022',
          'inmet_2023': 'inmet_2023',
          'inmet_2024': 'inmet_2024',
         }

periodos = {'diaria': 'D', 'semanal': 'W', 'mensal': 'ME'}
datetime_column = 'Datetime'

for key, value in my_csv.items():
    print(f'Carregando {value}.csv')
    df = pd.read_csv(f'{export_folder}{value}.csv',parse_dates=True)
    df[datetime_column] = pd.to_datetime(df[datetime_column])
    df.set_index(datetime_column, inplace=True)
    for name, period in periodos.items():
        print(f'Calcular média {name} de {value}.csv')
        new_df = calculate_metrics_by_period(
            df=df,
            period=period,
            df_name=f'{key}_{name}'
        )
        new_df.dropna(inplace=True)
        new_df.to_csv(f'{export_folder}{key}_{name}.csv')

# carregando o dados salvos
climate_data = load_climate_data()

# criar os climogramas
for key in climate_data.keys():
    gerar_climograma(climate_data[key])

print('\n\nEnd')
