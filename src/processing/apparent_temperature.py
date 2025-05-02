# src/processing/apparent_temperature.py

import numpy as np
import pandas as pd

def calculate_heat_index(T, RH):
    """
    Calcula o índice de calor (Heat Index) em °C usando a fórmula completa
    da NOAA.

    T: temperatura em °C
    RH: umidade relativa em %
    """
    # Converte para Fahrenheit
    T_F = T * 1.8 + 32

    c1 = -42.379
    c2 = 2.04901523
    c3 = 10.14333127
    c4 = -0.22475541
    c5 = -6.83783e-3
    c6 = -5.481717e-2
    c7 = 1.22874e-3
    c8 = 8.5282e-4
    c9 = -1.99e-6

    HI_F = (
        c1 + c2 * T_F + c3 * RH + c4 * T_F * RH + c5 * T_F ** 2
        + c6 * RH ** 2 + c7 * T_F ** 2 * RH + c8 * T_F * RH ** 2
        + c9 * T_F ** 2 * RH ** 2
    )

    # Converte de volta para Celsius
    HI_C = (HI_F - 32) * 5 / 9
    return HI_C

def calculate_wind_chill(T, V):
    """
    Calcula o Wind Chill em °C.
    Fórmula válida para T <= 10°C e V >= 1.3 m/s.
    """
    V_kmh = V * 3.6

    WC = (
        13.12 + 0.6215 * T - 11.37 * V_kmh ** 0.16
        + 0.3965 * T * V_kmh ** 0.16
    )
    return WC

def calculate_apparent_temperature(df: pd.DataFrame) -> pd.Series:
    """
    Calcula a sensação térmica combinando índice de calor, wind chill
    ou temperatura real, conforme a condição.

    Parâmetros:
        df (pd.DataFrame): Deve ter colunas 'Temp_ar' (°C),
                           'UR' (%), 'Vel_vento' (m/s).

    Retorna:
        pd.Series: Sensação térmica em °C.
    """
    if not {'Temp', 'UR', 'Vel_vento'}.issubset(df.columns):
        raise ValueError("DataFrame precisa conter 'Temp', 'UR' e 'Vel_vento'.")

    T = df['Temp_ar']
    RH = df['UR']
    V = df['Vel_vento']

    apparent = T.copy()

    # Índice de calor
    mask_heat = (T >= 27) & (RH >= 40)
    apparent[mask_heat] = calculate_heat_index(T[mask_heat], RH[mask_heat])

    # Wind chill
    mask_chill = (T <= 10) & (V >= 1.3)
    apparent[mask_chill] = calculate_wind_chill(T[mask_chill], V[mask_chill])

    return apparent
