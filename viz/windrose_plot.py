import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

EXPORT_DIR = Path(__file__).resolve().parent.parent / 'data_processed'
IMG_DIR = Path(__file__).resolve().parent.parent / 'img'
IMG_DIR.mkdir(parents=True, exist_ok=True)

ORDERED_WIND_DIRECTIONS = ['N', 'NE', 'E', 'SE', 'S', 'SO', 'O', 'NO']
DIRECTION_BINS = np.arange(0, 361, 45)  # 8 bins de 45°

# Mapeamento para abreviações dos meses
MONTH_MAP = {
    1: 'JAN', 2: 'FEV', 3: 'MAR', 4: 'ABR', 5: 'MAI', 6: 'JUN',
    7: 'JUL', 8: 'AGO', 9: 'SET', 10: 'OUT', 11: 'NOV', 12: 'DEZ'
}


def load_wind_data(files: list[str]) -> dict:
    data = {}
    for file in files:
        path = EXPORT_DIR / file
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if 'Vel_vento' not in df.columns or 'Dir_vento' not in df.columns:
            continue
        name = path.stem
        df.attrs['file_name'] = name
        df.attrs['graph_name'] = (
            f"Rosa dos Ventos - Iguape/SP (EPW)"
            if 'epw' in file else
            f"Rosa dos Ventos - Iguape/SP ({file[6:10]})"
        )
        data[name] = df
    return data


def plot_windrose(df: pd.DataFrame) -> None:
    directions = df['Dir_vento'].dropna().values % 360
    if directions.size == 0:
        return
    counts, _ = np.histogram(directions, bins=DIRECTION_BINS)
    angles = np.deg2rad(DIRECTION_BINS[:-1])
    width = np.deg2rad(45)

    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(111, projection='polar')
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.bar(angles, counts, width=width, bottom=0.0, color='skyblue', edgecolor='black')
    ax.set_xticks(np.deg2rad(DIRECTION_BINS[:-1]))
    ax.set_xticklabels(ORDERED_WIND_DIRECTIONS)
    ax.set_title(df.attrs['graph_name'], va='bottom', fontsize=12)

    output = IMG_DIR / f"windrose_{df.attrs['file_name']}.png"
    plt.savefig(output, dpi=300, bbox_inches='tight')
    plt.close(fig)


def plot_windrose_categorical(df: pd.DataFrame) -> None:
    if 'Ori_vento' not in df.columns:
        return
    counts = df['Ori_vento'].value_counts().reindex(
        ORDERED_WIND_DIRECTIONS, fill_value=0
    )
    angles = np.deg2rad(DIRECTION_BINS[:-1])
    width = np.deg2rad(45)

    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(111, projection='polar')
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)

    ax.bar(angles, counts.values, width=width, bottom=0.0, color='skyblue', edgecolor='black')
    ax.set_xticks(np.deg2rad(DIRECTION_BINS[:-1]))
    ax.set_xticklabels(ORDERED_WIND_DIRECTIONS)
    ax.set_title(df.attrs['graph_name'] + ' (categorical)', va='bottom', fontsize=12)

    output = IMG_DIR / f"windrose_cat_{df.attrs['file_name']}.png"
    plt.savefig(output, dpi=300, bbox_inches='tight')
    plt.close(fig)


def plot_monthly_windrose(df: pd.DataFrame) -> None:
    if 'Dir_vento' not in df.columns or 'Vel_vento' not in df.columns or 'Datetime' not in df.columns:
        return
    df['Month'] = pd.to_datetime(df['Datetime']).dt.month
    fig, axes = plt.subplots(3, 4, subplot_kw={'projection':'polar'}, figsize=(12, 9))
    for month in range(1, 13):
        ax = axes.flatten()[month-1]
        sub = df[df['Month'] == month]
        dirs = sub['Dir_vento'].dropna().values % 360
        if dirs.size == 0:
            ax.set_title(MONTH_MAP.get(month, str(month)))
            continue
        counts, _ = np.histogram(dirs, bins=DIRECTION_BINS)
        angles = np.deg2rad(DIRECTION_BINS[:-1])
        width = np.deg2rad(45)
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.bar(angles, counts, width=width, bottom=0.0, color='skyblue', edgecolor='black')
        ax.set_xticks(np.deg2rad(DIRECTION_BINS[:-1]))
        ax.set_xticklabels(ORDERED_WIND_DIRECTIONS)
        ax.set_title(MONTH_MAP.get(month, str(month)), y=1.1)
    plt.tight_layout()
    output = IMG_DIR / f"windrose_monthly_{df.attrs['file_name']}.png"
    plt.savefig(output, dpi=300)
    plt.close(fig)


def main() -> None:
    freq_types = ['horaria', 'diaria', 'semanal', 'mensal']
    years = range(2019, 2025)
    files = [f'iguape_epw_{f}.csv' for f in freq_types]
    for freq in freq_types:
        files += [f'inmet_{ano}_{freq}.csv' for ano in years]
    data = load_wind_data(files)
    for df in data.values():
        plot_windrose(df)
        plot_windrose_categorical(df)
        plot_monthly_windrose(df)

if __name__ == '__main__':
    main()
