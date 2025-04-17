import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plotar_rosa_dos_ventos(df: pd.DataFrame, titulo: str = 'Rosa dos Ventos') -> None:
    """
    Gera gráfico tipo rosa dos ventos (wind rose) a partir de DataFrame com colunas específicas.
    
    Parâmetros:
        df (pd.DataFrame): DataFrame contendo colunas 'Wind Direction' e 'Wind Speed'
        titulo (str): Título do gráfico
        
    Retorno:
        None (exibe o gráfico)
    """
    # Verificação das colunas necessárias
    colunas_necessarias = {'Wind Direction', 'Wind Speed'}
    if not colunas_necessarias.issubset(df.columns):
        raise ValueError(f"DataFrame precisa conter colunas: {colunas_necessarias}")
    
    # Configuração das bins
    direcoes_bins = np.arange(0, 375, 15)  # 0-360° em passos de 15°
    velocidades_bins = [0, 5, 10, 15, 20, 25, 30]
    cores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    # Criação de categorias
    df = df.copy()
    df['Direção_Cat'] = pd.cut(
        df['Wind Direction'],
        bins=direcoes_bins,
        right=False
    )
    df['Velocidade_Cat'] = pd.cut(df['Wind Speed'], bins=velocidades_bins)
    
    # Agrupamento corrigido (observed=False para FutureWarning)
    grupos = df.groupby(
        ['Direção_Cat', 'Velocidade_Cat'], 
        observed=False  # Adicionado para suprimir warning
    ).size().unstack(fill_value=0)
    
    # Configuração do gráfico polar
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, polar=True)
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    
    # Conversão para radianos (ajuste de 7.5° para centralizar nas bins)
    angulos = np.deg2rad(direcoes_bins[:-1] + 7.5)
    
    # Plotagem das barras empilhadas
    bottom = np.zeros(len(angulos))
    for idx, velocidade in enumerate(grupos.columns):
        valores = grupos[velocidade].values
        ax.bar(
            x=angulos,
            height=valores,
            width=np.deg2rad(15),
            bottom=bottom,
            color=cores[idx],
            edgecolor='black',
            label=f'{velocidade.left}-{velocidade.right} m/s'
        )
        bottom += valores
    
    # Correção dos rótulos (24 ticks → 24 labels)
    ax.set_xticks(np.deg2rad(np.arange(0, 360, 15)))
    ax.set_xticklabels([
        'N' if i == 0 else 
        'E' if i == 90 else 
        'S' if i == 180 else 
        'O' if i == 270 else 
        '' for i in np.arange(0, 360, 15)
    ])
    
    ax.set_title(titulo, pad=35, fontsize=14)
    ax.legend(bbox_to_anchor=(1.15, 1), loc='upper left', title='Velocidade do Vento')
    
    plt.show()