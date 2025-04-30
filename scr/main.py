from limpar_csv import *
from processamento_dados import *
from criar_climograma import *

# definir pasta de trabalho
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
    'Datetime', 'Temp', 'Umi', 'Vel_vento', 'Dir_vento', 'Precipitacao'
]

# adicionar orientação da ventilação
ori_vento = 'Ori_vento'
iguape_epw[ori_vento] = set_wind_direction(iguape_epw['Dir_vento'])
print(f'\n\n...\t...\t{iguape_epw[ori_vento].value_counts().sort_index()}\n')

# salvar arquivo
iguape_epw.attrs['Name'] = 'iguape_epw'
save_as_csv(iguape_epw,export_folder)
print(f'{iguape_epw.attrs["Name"]} foi salvo.')

del iguape_old_epw

# limpando os arquivos INMET
# definindo os arquivos para importação
inmet_2019 = {'inmet_2019':('a712_iguape_2019a','a712_iguape_2019b')}
inmet_2020 = {'inmet_2020':('a712_iguape_2020a','a712_iguape_2020b')}
inmet_2021 = {'inmet_2021':('a712_iguape_2021a','a712_iguape_2021b')}
inmet_2022 = {'inmet_2022':('a712_iguape_2022a','a712_iguape_2022b')}
inmet_2023 = {'inmet_2023':('a712_iguape_2023a','a712_iguape_2023b')}
inmet_2024 = {'inmet_2024':('a712_iguape_2024a','a712_iguape_2024b')}

inmet_dados = (
    inmet_2019,inmet_2020,inmet_2021,inmet_2022,inmet_2023,inmet_2024
)

# criar os dataframes
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
            'Datetime', 'Temp', 'Umi', 'Vel_vento', 'Dir_vento', 'Precipitacao'
        ]

        # adicionar orientação do vento
        df3[ori_vento] = set_wind_direction(df3['Dir_vento'])
        print(f'\n\n...\t...\t{df3[ori_vento].value_counts().sort_index()}\n')
        
        # removendo as colunas vazias
        df3 = df3[df3['Temp'].notnull()]
        
        save_as_csv(df3,export_folder)
        print(f'{df3.attrs["Name"]} foi salvo.')
        
        del df1, df2, df3

# novos dataframes com os 10% mais quente e frio
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
for df in (iguape_10p_cold, iguape_10p_hot):
    save_as_csv(df, export_folder)
    # limpando a memoria
    print(f'{df.attrs["Name"]} foi salvo.')
    print(f'\n\n...\t...\t{df[ori_vento].value_counts().sort_index()}\n')
    del df
    
# criar as medias diarias, semanal e mensal
my_csv = {'iguape_epw': 'iguape_epw',
          'inmet_2019': 'inmet_2019',
          'inmet_2020': 'inmet_2020',
          'inmet_2021': 'inmet_2021',
          'inmet_2022': 'inmet_2022',
          'inmet_2023': 'inmet_2023',
          'inmet_2024': 'inmet_2024',
         }

# calcular os valores médios por períodos
periodos = {'diaria': 'D', 'semanal': 'W', 'mensal': 'ME'}
datetime_column = 'Datetime'
ventilation_orientation = 'Ori_vento'

for key, value in my_csv.items():
    print(f'Carregando {value}.csv')
    df = pd.read_csv(f'{export_folder}{value}.csv',parse_dates=True)
    df[datetime_column] = pd.to_datetime(df[datetime_column])
    df.set_index(datetime_column, inplace=True)
    direcoes = ['N', 'NE', 'L', 'SE', 'S', 'SO', 'O', 'NO']
    df[ventilation_orientation] = df[ventilation_orientation].astype('category')
    
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
