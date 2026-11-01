import re # Para usar expresiones regulares en la limpieza de registros de sensores
from django.shortcuts import render, redirect
from django.contrib import messages # Para enviar alertas de éxito (message.success) o error (message.error) cuando el usuario realiza una acción no permitida

from .logica_sensores import (
    limpiar_registro_sensor,
    generar_resumen_sensores,
    leer_sensores_crudos,
    guardar_sensores_crudos,
)
from .logica_catalogo import (
    StockInvalidoError,
    DispositivoEcologico,
    PanelSolar,
    GestorInventario,
)
from .logica_emisiones import (
    calcular_emisiones_carbono,
    obtener_metricas_consumo,
)

# Lista en memoria para probar altas y bajas en el panel del Ejercicio 3
HISTORIAL_PLANTAS = [
    {"planta": "Planta Norte", "consumo_kwh": 1500.0},
    {"planta": "Planta Sur", "consumo_kwh": 2300.0},
    {"planta": "Planta Este", "consumo_kwh": 950.0},
]

def extraer_numero(cadena):
    """
    Convierte cadenas como '$310.50', '310,50', '50%' o '10KwH' en un float válido.
    """
    if cadena is None or str(cadena).strip() == "":
        raise ValueError("El campo está vacío.")
    
    # Cambiamos comas por puntos para los decimales
    cadena = str(cadena).replace(',', '.')
    # Extraemos solo dígitos, puntos y signos negativos
    cadena_limpia = re.sub(r'[^\d.-]', '', cadena)
    
    if not cadena_limpia:
        raise ValueError("No se detectaron valores numéricos.")
    
    return float(cadena_limpia)

# ==============================================================================
# PESTAÑA 1: SENSORES (EJERCICIO 1 - PUNTOS A Y B + CRUD JSON)
# ==============================================================================
def vista_sensores(request):
    datos_crudos = leer_sensores_crudos()
    umbral = 30.0  # Valor por defecto para el umbral de temperatura

    # Si el usuario envió un formulario (Crear, Actualizar o Borrar)
    if request.method == "POST":
        accion = request.POST.get("accion")

        # --- CREAR SENSOR ---
        if accion == "crear":
            nuevo_id = request.POST.get("sensor_id", "")
            nueva_temp = request.POST.get("temperatura", "")
            nueva_ubic = request.POST.get("ubicacion", "")

            if nuevo_id.strip() == "":
                messages.error(request, "Acción denegada: El ID del sensor no puede estar vacío.")
            else:
                datos_crudos.append({
                    "sensor_id": nuevo_id,
                    "temperatura": nueva_temp,
                    "ubicacion": nueva_ubic
                })
                guardar_sensores_crudos(datos_crudos)
                messages.success(request, f"Sensor '{nuevo_id.strip()}' registrado exitosamente.")
            return redirect("vista_sensores")

        # --- ACTUALIZAR SENSOR ---
        elif accion == "actualizar":
            try:
                indice = int(request.POST.get("indice"))
                nuevo_id = request.POST.get("sensor_id", "")
                if nuevo_id.strip() == "":
                    messages.error(request, "Acción denegada: No puedes dejar a un sensor sin ID.")
                else:
                    datos_crudos[indice] = {
                        "sensor_id": nuevo_id,
                        "temperatura": request.POST.get("temperatura", ""),
                        "ubicacion": request.POST.get("ubicacion", "")
                    }
                    guardar_sensores_crudos(datos_crudos)
                    messages.success(request, "Registro del sensor actualizado correctamente.")
            except (ValueError, IndexError):
                messages.error(request, "Error: No se encontró el registro que intentas editar.")
            return redirect("vista_sensores")

        # --- BORRAR SENSOR ---
        elif accion == "eliminar":
            try:
                indice = int(request.POST.get("indice"))
                eliminado = datos_crudos.pop(indice)
                guardar_sensores_crudos(datos_crudos)
                messages.success(request, f"Sensor '{eliminado.get('sensor_id')}' eliminado del sistema.")
            except (ValueError, IndexError):
                messages.error(request, "Error: No se pudo eliminar el registro seleccionado.")
            return redirect("vista_sensores")

    # Si el usuario cambió el umbral de temperatura por pantalla
    umbral_texto = str(umbral)  # Lo que se muestra en el campo del formulario
    if "umbral" in request.GET:
        umbral_texto = request.GET.get("umbral", "")
        try:
            umbral = extraer_numero(umbral_texto)
        except ValueError:
            umbral = None  # Umbral inválido: no se calcula el resumen
            messages.error(request, "Dato inválido: El umbral debe ser un número (ej. 30.5). Ingresa un valor válido para calcular el resumen.")

    # Ejecutamos Punto 1.A (Limpieza) y Punto 1.B (Resumen estadístico)
    sensores_limpios = [limpiar_registro_sensor(reg) for reg in datos_crudos]
    # Solo generamos el resumen si el umbral es válido
    if umbral is not None:
        alertas, promedio_global = generar_resumen_sensores(sensores_limpios, umbral)
    else:
        alertas, promedio_global = [], None

    # Combinamos datos crudos y limpios para mostrarlos lado a lado en la tabla
    tabla_comparativa = []
    for i in range(len(datos_crudos)):
        tabla_comparativa.append({
            "indice": i,
            "crudo": datos_crudos[i],
            "limpio": sensores_limpios[i],
            "en_alerta": (sensores_limpios[i]["temperatura"] > umbral) if umbral is not None else False
        })

    contexto = {
        "pestana_activa": "sensores",
        "tabla_comparativa": tabla_comparativa,
        "umbral": umbral_texto,
        "alertas": alertas,
        "promedio_global": promedio_global,
    }
    return render(request, "sustentabilidad/sensores.html", contexto)


# ==============================================================================
# PESTAÑA 2: CATÁLOGO E INVENTARIO (EJERCICIO 2 - PUNTOS A Y B + CRUD JSON)
# ==============================================================================
def vista_catalogo(request):
    gestor = GestorInventario()
    catalogo = gestor.leer_catalogo_json()

    if request.method == "POST":
        accion = request.POST.get("accion")

        # --- CREAR O ACTUALIZAR PRODUCTO ---
        if accion in ["crear", "actualizar"]:
            id_prod = request.POST.get("id_producto", "").strip()
            nombre = request.POST.get("nombre", "").strip()
            tipo_clase = request.POST.get("tipo_clase", "estandar")

            if not id_prod or not nombre:
                messages.error(request, "Acción denegada: El ID y el Nombre del producto son obligatorios.")
                return redirect("vista_catalogo")

            try:
                # Utilizamos la función extractora para limpiar símbolos de moneda o texto indeseado
                precio = extraer_numero(request.POST.get("precio"))
                stock = int(extraer_numero(request.POST.get("stock")))

                if precio < 0:                    
                    messages.error(request, "Dato inválido: El precio del producto no puede ser negativo.")
                    return redirect("vista_catalogo")

                # Validamos que el ID no esté repetido en otro producto
                indice_actual = int(request.POST.get("indice")) if accion == "actualizar" else None
                for i, prod in enumerate(catalogo):
                    mismo_id = prod.get("id_producto", "").strip().lower() == id_prod.lower()
                    if mismo_id and i != indice_actual:
                        messages.error(request, f"Acción denegada: Ya existe un producto con el ID '{id_prod}'.")
                        return redirect("vista_catalogo")

                # Instanciamos la clase correspondiente para que se ejecute el @stock.setter
                if tipo_clase == "panel_solar":
                    eficiencia = extraer_numero(request.POST.get("eficiencia"))
                    potencia_w = extraer_numero(request.POST.get("potencia_w"))
                    nuevo_dispositivo = PanelSolar(id_prod, nombre, precio, stock, eficiencia, potencia_w)
                else:
                    nuevo_dispositivo = DispositivoEcologico(id_prod, nombre, precio, stock)

                ficha_generada = nuevo_dispositivo.generar_ficha_tecnica()

                if accion == "crear":
                    catalogo.append(ficha_generada)
                    messages.success(request, f"Producto '{nombre}' registrado exitosamente.")
                else:
                    indice = int(request.POST.get("indice"))
                    catalogo[indice] = ficha_generada
                    messages.success(request, f"Producto '{nombre}' actualizado exitosamente.")

                gestor.guardar_catalogo_json(catalogo)

            # Capturamos nuestra excepción personalizada StockInvalidoError (Paso 2.1 y 2.2)
            except StockInvalidoError as error_stock:
                messages.error(request, f"[Error de Validación]: {error_stock}")
            except ValueError:
                messages.error(request, "Dato inválido: Los campos de precio, stock, potencia y eficiencia deben ser valores numéricos (pueden incluir símbolos como $ o % que serán limpiados).")
            except IndexError:
                messages.error(request, "Error: No se encontró el producto que intentas actualizar.")

            return redirect("vista_catalogo")

        # --- BORRAR PRODUCTO ---
        elif accion == "eliminar":
            try:
                indice = int(request.POST.get("indice"))
                eliminado = catalogo.pop(indice)
                gestor.guardar_catalogo_json(catalogo)
                messages.success(request, f"Producto '{eliminado.get('nombre')}' eliminado.")
            except (ValueError, IndexError):
                messages.error(request, "Error al intentar eliminar el producto.")
            return redirect("vista_catalogo")

    contexto = {
        "pestana_activa": "catalogo",
        "catalogo": catalogo,
    }
    return render(request, "sustentabilidad/catalogo.html", contexto)


# ==============================================================================
# PESTAÑA 3: PANEL DE SUSTENTABILIDAD (EJERCICIO 3 - PUNTOS A Y B)
# ==============================================================================
def vista_panel_sustentabilidad(request):
    """
    Función de vista exigida en el Ejercicio 3 - Punto B.
    Procesa las métricas de consumo y renderiza 'sustentabilidad/panel.html'.
    """
    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion in ["agregar_planta", "actualizar_planta"]:
            nombre_planta = request.POST.get("planta", "").strip()
            if not nombre_planta:
                messages.error(request, "Acción denegada: Debes indicar el nombre de la planta industrial.")
            else:
                try:
                    consumo = extraer_numero(request.POST.get("consumo_kwh"))
                    # Validamos el consumo llamando a la función auditada del Punto 3.A
                    emision_calculada = calcular_emisiones_carbono(consumo)

                    if accion == "agregar_planta":
                        HISTORIAL_PLANTAS.append({"planta": nombre_planta, "consumo_kwh": consumo})
                        messages.success(request, f"Planta '{nombre_planta}' registrada.")
                    else:
                        indice = int(request.POST.get("indice"))
                        HISTORIAL_PLANTAS[indice] = {"planta": nombre_planta, "consumo_kwh": consumo}
                        messages.success(request, f"Registro de '{nombre_planta}' actualizado.")

                except ValueError as error_valor:
                    mensaje_error = str(error_valor) if "negativo" in str(error_valor) else "Dato inválido: El consumo debe ser numérico."
                    messages.error(request, f"Error: {mensaje_error}")
                except IndexError:
                    messages.error(request, "Error: No se encontró el registro que intentas actualizar.")
            return redirect("vista_panel_sustentabilidad")

        elif accion == "eliminar_planta":
            try:
                indice = int(request.POST.get("indice"))
                eliminada = HISTORIAL_PLANTAS.pop(indice)
                messages.success(request, f"Registro de '{eliminada['planta']}' eliminado.")
            except (ValueError, IndexError):
                messages.error(request, "No se pudo eliminar el registro.")
            return redirect("vista_panel_sustentabilidad")

    # Calculamos las métricas globales con la función del Punto 3.B
    metricas = obtener_metricas_consumo(HISTORIAL_PLANTAS)

    # Enriquecemos la lista para mostrar la emisión individual de cada planta en la tabla
    detalle_plantas = []
    for i, reg in enumerate(HISTORIAL_PLANTAS):
        detalle_plantas.append({
            "indice": i,
            "planta": reg["planta"],
            "consumo_kwh": reg["consumo_kwh"],
            "emision": calcular_emisiones_carbono(reg["consumo_kwh"])
        })

    contexto = {
        "pestana_activa": "emisiones",
        "total_emisiones": metricas["total_emisiones"],
        "planta_mayor_consumo": metricas["planta_mayor_consumo"],
        "detalle_plantas": detalle_plantas,
    }
    return render(request, "sustentabilidad/panel.html", contexto)
