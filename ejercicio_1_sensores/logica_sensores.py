import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RUTA_SENSORES_JSON = BASE_DIR / "sensores_crudos.json"


# --- PUNTO 1.A: Normalización de Lecturas ---
def limpiar_registro_sensor(registro_raw):
    """
    Normaliza un diccionario crudo de un sensor: quita espacios del ID,
    convierte la temperatura a float (pasando de F a C si corresponde)
    y asigna una ubicación por defecto si está vacía.
    """
    registro_limpio = {}

    # Sanitización de sensor_id
    id_crudo = str(registro_raw.get("sensor_id", ""))
    registro_limpio["sensor_id"] = id_crudo.strip()

    # Estandarización de temperatura
    temp_cruda = registro_raw.get("temperatura", 0.0)

    if isinstance(temp_cruda, (int, float)):
        registro_limpio["temperatura"] = float(temp_cruda)
    else:
        texto_temp = str(temp_cruda).upper()
        es_fahrenheit = "F" in texto_temp

        texto_limpio = (
            texto_temp
            .replace("C", "")
            .replace("F", "")
            .replace("°", "")
            .replace(" ", "")
        )
        try:
            valor_temp = float(texto_limpio)
            if es_fahrenheit:
                valor_temp = (valor_temp - 32) * 5 / 9
            registro_limpio["temperatura"] = round(valor_temp, 2)
        except ValueError:
            registro_limpio["temperatura"] = 0.0

    # Tratamiento de ubicación
    ubicacion_cruda = registro_raw.get("ubicacion", "")
    if isinstance(ubicacion_cruda, str) and ubicacion_cruda.strip() != "":
        registro_limpio["ubicacion"] = ubicacion_cruda.strip()
    else:
        registro_limpio["ubicacion"] = "Área No Asignada"

    return registro_limpio


# --- PUNTO 1.B: Monitoreo y Mapeo Estadístico ---
def generar_resumen_sensores(lista_sensores_limpios, umbral_temperatura):
    """
    Retorna una tupla (lista_sensores_alerta, promedio_temperatura)
    a partir de los registros limpios y un umbral numérico.
    """
    if not lista_sensores_limpios:
        return ([], 0.0)

    acumulador_temperatura = 0.0
    lista_sensores_alerta = []

    for sensor in lista_sensores_limpios:
        temp_actual = sensor["temperatura"]
        acumulador_temperatura += temp_actual

        if temp_actual > umbral_temperatura:
            lista_sensores_alerta.append(sensor["sensor_id"])

    promedio = acumulador_temperatura / len(lista_sensores_limpios)
    return (lista_sensores_alerta, round(promedio, 2))


# --- FUNCIONES AUXILIARES CRUD PARA sensores_crudos.json ---
def leer_sensores_crudos():
    """Lee el archivo JSON de sensores o crea uno inicial si no existe."""
    if not os.path.exists(RUTA_SENSORES_JSON):
        datos_iniciales = [
            {"sensor_id": " SENSOR-001 ", "temperatura": "24.5C", "ubicacion": "Planta Norte"},
            {"sensor_id": "SENSOR-002   ", "temperatura": "35.0 c", "ubicacion": "   "},
            {"sensor_id": "  SENSOR-003", "temperatura": "31.2°c", "ubicacion": "Sector Químico"},
            {"sensor_id": "SENSOR-004 ", "temperatura": "ERROR_LECTURA", "ubicacion": ""},
            {"sensor_id": " SENSOR-005", "temperatura": "95.0F", "ubicacion": "Sala de Calderas"}
        ]
        guardar_sensores_crudos(datos_iniciales)
        return datos_iniciales

    with open(RUTA_SENSORES_JSON, mode="r", encoding="utf-8") as archivo:
        return json.load(archivo)


def guardar_sensores_crudos(lista_registros):
    """Sobrescribe el archivo sensores_crudos.json con la lista actualizada."""
    with open(RUTA_SENSORES_JSON, mode="w", encoding="utf-8") as archivo:
        json.dump(lista_registros, archivo, indent=4, ensure_ascii=False)

###################################################################################################
# BLOQUE DE EJECUCIÓN: prueba final solicitada en consola
###################################################################################################

if __name__ == "__main__":
    registros_crudos = [
        {"sensor_id": " SENSOR-001 ", "temperatura": "24.5C", "ubicacion": "Planta Norte"},
        {"sensor_id": "SENSOR-002   ", "temperatura": "35.0 C", "ubicacion": "   "},
        {"sensor_id": "  SENSOR-003", "temperatura": "31.2°c", "ubicacion": "Sector Químico"},
        {"sensor_id": "SENSOR-004 ", "temperatura": "ERROR_LECTURA", "ubicacion": ""},
        {"sensor_id": "SENSOR-005", "temperatura": 28, "ubicacion": "Almacén Central"},
    ]
    umbral = 30.0

    # Limpieza de cada registro crudo
    registros_limpios = [limpiar_registro_sensor(reg) for reg in registros_crudos]

    # Resumen estadístico
    alertas, promedio = generar_resumen_sensores(registros_limpios, umbral)

    # Reporte formateado
    print("=" * 50)
    print("REPORTE DE SENSORES - EcoTech Solutions")
    print("=" * 50)
    for sensor in registros_limpios:
        print(f"{sensor['sensor_id']:<12} {sensor['temperatura']:>6} ºC  {sensor['ubicacion']}")
    print("-" * 50)
    print(f"Umbral de alerta: {umbral} ºC")
    print(f"Promedio térmico global: {promedio} ºC")
    if alertas:
        print(f"Sensores en alerta: {', '.join(alertas)}")
    else:
        print("Sensores en alerta: Ninguno")