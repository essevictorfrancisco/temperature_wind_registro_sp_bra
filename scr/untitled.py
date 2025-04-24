# climograma_seaborn.py
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from typing import Dict, Optional

def verificar_estrutura_dados(df: pd.DataFrame) -> None:
    """Valida a estrutura do DataFrame conforme requisitos do climograma."""
    colunas_necessarias = ['Mês', 'Chuva_tot', 'Temp_med', 'Temp_max', 'Temp_min']
    if not all(col in df.columns for col in colunas_necessarias):
        missing = [col for col in colunas_necessarias if col not in df.columns]
        raise ValueError(f"Colunas faltantes: {', '.join(missing)}")

def configurar_estilo() -> None:
    """Configura o estilo visual dos gráficos usando Seaborn."""
    sns.set_theme(
        style="whitegrid",
        rc={
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10
        }
    )

def plot_climograma(
    dados_climaticos: Dict[str, pd.DataFrame],
    locale: str = 'pt_BR',
    tamanho: Optional[tuple[int, int]] = None
) -> None:
    """
    Gera um climograma profissional combinando precipitação e temperaturas.
    
    Parâmetros:
        dados_climaticos (dict): Dicionário com DataFrames climáticos mensais
        locale (str): Localização para formatação de datas (padrão: pt_BR)
        tamanho (tuple): Dimensões da figura (largura, altura)
    
    Retorna:
        None
    """
    df = dados_climaticos['iguape_epw_mensal'].copy()
    verificar_estrutura_dados(df)
    
    # Configuração regional e ordenação
    meses_ordenados = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril',
        'Maio', 'Junho', 'Julho', 'Agosto',
        'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    df['Mês'] = pd.Categorical(df['Mês'], categories=meses_ordenados, ordered=True)
    df = df.sort_values('Mês')

    # Configuração do estilo
    configurar_estilo()
    plt.figure(figsize=tamanho if tamanho else (12, 6))
    ax_precip = plt.gca()

    # Paleta de cores otimizada
    cores = {
        'precipitacao': '#1f77b4',
        'temp_media': '#2ca02c',
        'temp_maxima': '#d62728',
        'temp_minima': '#9467bd'
    }

    # Gráfico de barras para precipitação
    sns.barplot(
        x='Mês',
        y='Chuva_tot',
        data=df,
        color=cores['precipitacao'],
        alpha=0.7,
        ax=ax_precip,
        edgecolor='none'
    )

    # Configuração do eixo de precipitação
    ax_precip.set_ylabel('Precipitação (mm)', color=cores['precipitacao'])
    ax_precip.tick_params(axis='y', colors=cores['precipitacao'])
    ax_precip.set_ylim(0, df['Chuva_tot'].max() * 1.15)

    # Eixo secundário para temperaturas
    ax_temp = ax_precip.twinx()

    # Plotagem das temperaturas com Seaborn
    for tipo_temp, cor in zip(['Temp_med', 'Temp_max', 'Temp_min'],
                            [cores['temp_media'], cores['temp_maxima'], cores['temp_minima']]):
        sns.lineplot(
            x='Mês',
            y=tipo_temp,
            data=df,
            color=cor,
            marker='o' if tipo_temp == 'Temp_med' else '^' if tipo_temp == 'Temp_max' else 'v',
            markersize=8,
            linewidth=2.5,
            ax=ax_temp,
            label=tipo_temp.replace('_', ' ').title().replace('Temp', 'T.')
        )

    # Configuração do eixo de temperatura
    ax_temp.set_ylabel('Temperatura (°C)', color=cores['temp_media'])
    ax_temp.tick_params(axis='y', colors=cores['temp_media'])
    ax_temp.set_ylim(0, df[['Temp_max', 'Temp_med', 'Temp_min']].max().max() * 1.15)

    # Customização final
    plt.title('Climograma - Iguape/SP\nPrecipitação e Temperaturas Mensais', pad=20)
    ax_precip.set_xlabel('Mês', labelpad=15)
    plt.xticks(rotation=45, ha='right')

    # Legenda unificada
    handles, labels = ax_precip.get_legend_handles_labels()
    handles += ax_temp.get_legend_handles_labels()[0]
    labels += ax_temp.get_legend_handles_labels()[1]
    
    sns.move_legend(
        ax_temp,
        loc="upper left",
        bbox_to_anchor=(0.01, 0.97),
        title=None,
        frameon=True
    )

    plt.tight_layout()
    plt.show()

# Exemplo de uso
if __name__ == "__main__":
    # Dados de exemplo (simulação)
    meses = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril',
        'Maio', 'Junho', 'Julho', 'Agosto',
        'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    dados = {
        'Mês': meses,
        'Chuva_tot': [220, 180, 150, 90, 70, 50, 40, 50, 80, 120, 150, 200],
        'Temp_med': [25.5, 25.8, 24.9, 23.2, 21.1, 19.8, 19.5, 20.1, 21.3, 22.7, 23.5, 24.2],
        'Temp_max': [29.1, 29.4, 28.5, 26.8, 24.7, 23.4, 23.1, 23.8, 25.0, 26.4, 27.2, 28.1],
        'Temp_min': [22.1, 22.4, 21.5, 19.8, 17.7, 16.4, 16.1, 16.8, 18.0, 19.4, 20.2, 21.1]
    }
    
    climate_data = {'iguape_epw_mensal': pd.DataFrame(dados)}
    
    plot_climograma(
        climate_data,
        tamanho=(14, 7)
    )