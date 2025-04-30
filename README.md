# Projeto: Análise e Visualização de Dados Climáticos - Registro/SP

Este projeto realiza a limpeza, integração, análise estatística e visualização
exploratória de dados climáticos da cidade de Registro usando os dados da
estação climatológica de Iguape/SP, utilizando fontes como arquivos do
INMET e EPW (EnergyPlus Weather). O foco é criar uma base unificada e gerar
gráficos úteis para estudos ambientais, energéticos e urbanos.

---

## 📁 Estrutura dos Dados

Os dados estão divididos em dois conjuntos principais:

- **EPW**: Dados sintéticos representando clima típico (TMYx 2009–2023)
- **INMET**: Dados reais coletados entre 2019 e 2024 em arquivos CSV separados

Todos os dados incluem medidas horárias com as seguintes variáveis:

| Coluna           | Descrição                                  |
|------------------|---------------------------------------------|
| `Datetime`       | Data e hora da medição                     |
| `Temp`           | Temperatura do ar (°C)                     |
| `Umi`            | Umidade relativa do ar (%)                 |
| `Vel_vento`      | Velocidade do vento (m/s)                  |
| `Dir_vento`      | Direção angular do vento (graus)           |
| `Precipitacao`   | Precipitação acumulada (mm)               |
| `Ori_vento`      | Direção cardinal do vento (N, NE, etc.)    |

A partir desses dados, foram gerados CSVs agregados com frequência:
- Diária
- Semanal
- Mensal

E para cada frequência, são calculadas estatísticas como média, mediana, moda,
máximos, mínimos e desvio padrão.

---

## 📊 Visualizações Geradas

A partir dos dados processados, são gerados gráficos com Matplotlib e Seaborn,
organizados na pasta `viz/`:

- `create_climograph.py`: Climogramas (temp. vs precipitação mensal)
- `time_series_plot.py`: Séries temporais diárias, semanais e mensais
- `histogram_plot.py`: Histogramas das variáveis em todas as frequências
- `windrose_plot.py`: Rosa dos ventos para todas as frequências

As imagens são salvas na pasta `img/`.

---

## ⚙️ Como Executar

1. Clone este repositório
2. Instale as dependências com:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute os scripts desejados:
   ```bash
   python main.py                # processa e agrega os dados
   python viz/create_climograph.py
   python viz/time_series_plot.py
   python viz/histogram_plot.py
   python viz/windrose_plot.py
   ```

---

## 🤝 Como Contribuir

Você pode ajudar este projeto:

- Sugestões de novas visualizações ou análises
- Otimização e modularização do código
- Adição de dados históricos de outras fontes
- Criação de dashboards interativos com Plotly ou Streamlit
- Escrita de testes unitários com `pytest`

Para contribuir:
1. Fork o repositório
2. Crie uma branch `feature/nome`
3. Faça commits descritivos
4. Envie um Pull Request com a proposta de melhoria

---

## 📩 Contato

Para dúvidas, sugestões ou colaborações, entre em contato via Issues ou Pull Requests.

---

**Este projeto é mantido com fins educacionais e científicos.**

