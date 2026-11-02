from ejercicio_1_sensores.logica_sensores import (
    limpiar_registro_sensor,
    generar_resumen_sensores,
)


def test_limpieza_registro_normal():
    crudo = {"sensor_id": " SENSOR-001 ", "temperatura": "24.5C", "ubicacion": "Planta Norte"}
    limpio = limpiar_registro_sensor(crudo)
    assert limpio == {"sensor_id": "SENSOR-001", "temperatura": 24.5, "ubicacion": "Planta Norte"}


def test_limpieza_no_modifica_el_original():
    crudo = {"sensor_id": " S-1 ", "temperatura": "20C", "ubicacion": ""}
    limpiar_registro_sensor(crudo)
    assert crudo["sensor_id"] == " S-1 "


def test_temperatura_con_formatos_distintos():
    assert limpiar_registro_sensor({"sensor_id": "A", "temperatura": "35.0 c"})["temperatura"] == 35.0
    assert limpiar_registro_sensor({"sensor_id": "A", "temperatura": "31.2°c"})["temperatura"] == 31.2
    assert limpiar_registro_sensor({"sensor_id": "A", "temperatura": 28})["temperatura"] == 28.0


def test_temperatura_corrupta_da_cero():
    assert limpiar_registro_sensor({"sensor_id": "A", "temperatura": "ERROR_LECTURA"})["temperatura"] == 0.0


def test_ubicacion_por_defecto():
    assert limpiar_registro_sensor({"sensor_id": "A", "temperatura": 1, "ubicacion": "   "})["ubicacion"] == "Área No Asignada"
    assert limpiar_registro_sensor({"sensor_id": "A", "temperatura": 1})["ubicacion"] == "Área No Asignada"


def test_resumen_alertas_y_promedio():
    sensores = [
        {"sensor_id": "S1", "temperatura": 24.5, "ubicacion": "X"},
        {"sensor_id": "S2", "temperatura": 35.0, "ubicacion": "X"},
        {"sensor_id": "S3", "temperatura": 31.2, "ubicacion": "X"},
        {"sensor_id": "S4", "temperatura": 0.0, "ubicacion": "X"},
        {"sensor_id": "S5", "temperatura": 28.0, "ubicacion": "X"},
    ]
    alertas, promedio = generar_resumen_sensores(sensores, 30.0)
    assert alertas == ["S2", "S3"]
    assert promedio == 23.74


def test_umbral_es_estricto():
    sensores = [{"sensor_id": "S1", "temperatura": 30.0, "ubicacion": "X"}]
    alertas, _ = generar_resumen_sensores(sensores, 30.0)
    assert alertas == []


def test_resumen_lista_vacia():
    assert generar_resumen_sensores([], 30.0) == ([], 0.0)