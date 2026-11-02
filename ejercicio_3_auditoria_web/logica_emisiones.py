# --- PUNTO 3.A: Algoritmo de Emisiones ---
def calcular_emisiones_carbono(consumo_kwh, factor_emision=0.4):
    """
    Calcula las emisiones de carbono multiplicando el consumo por el factor.
    Lanza ValueError si el consumo es negativo.
    """
    if consumo_kwh < 0:
        raise ValueError("El consumo en kWh no puede ser negativo.")

    return round(consumo_kwh * factor_emision, 2)


# --- PUNTO 3.B: Procesamiento de Métricas ---
def obtener_metricas_consumo(registros):
    """
    Procesa el historial de consumos por planta para determinar el total
    global de emisiones y la planta de mayor consumo.
    """
    if not registros:
        return {"total_emisiones": 0.0, "planta_mayor_consumo": "Ninguna"}

    total_emisiones = 0.0
    mayor_consumo = -1.0
    planta_maxima = "Ninguna"

    for reg in registros:
        consumo = float(reg["consumo_kwh"])
        emision = calcular_emisiones_carbono(consumo)
        total_emisiones += emision

        if consumo > mayor_consumo:
            mayor_consumo = consumo
            planta_maxima = reg["planta"]

    return {
        "total_emisiones": round(total_emisiones, 2),
        "planta_mayor_consumo": planta_maxima
    }