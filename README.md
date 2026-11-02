# Trabajo Final Integrador — EcoTech Solutions

Proyecto integrador del curso **Programación con Python**, que implementa sanitización y análisis de lecturas de sensores térmicos, gestión de inventario ecológico con Programación Orientada a Objetos (POO) y persistencia en JSON, y un panel web administrativo desarrollado en **Django** con cálculo auditado de huella de carbono.

---

## Estructura del Proyecto

El código fuente se encuentra modularizado en tres carpetas independientes según las especificaciones de entrega:

```text
ecotech_tfi/
├── ejercicio_1_sensores/        # Sanitización de lecturas y monitoreo térmico
│   ├── logica_sensores.py
│   ├── sensores_crudos.json
│   └── test_sensores.py
├── ejercicio_2_productos/       # POO, excepciones personalizadas y persistencia JSON
│   ├── logica_catalogo.py
│   ├── catalogo_ecotech.json
│   └── test_catalogo.py
├── ejercicio_3_auditoria_web/   # Cálculo de emisiones e interfaz web en Django
│   ├── config/
│   ├── sustentabilidad/
│   ├── logica_emisiones.py
│   ├── manage.py
│   └── test_emisiones.py
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Instalación y Configuración

1. Clonar o descomprimir el repositorio y abrir una terminal en la carpeta raíz (`ecotech_tfi/`).
2. Crear y activar el entorno virtual:
   - **Windows (PowerShell):**
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
3. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

---

## Ejecución de Pruebas Automatizadas (`pytest`)

Desde la raíz del proyecto (con el entorno virtual activado), ejecutar:

```bash
pytest -v
```

---

## Ejecución por Consola (Ejercicios 1 y 2)

Cada módulo incluye su bloque de demostración independiente por terminal:

- **Ejercicio 1 (Reporte de sensores):**
  ```bash
  python ejercicio_1_sensores/logica_sensores.py
  ```
- **Ejercicio 2 (Ficha polimórfica, captura de `StockInvalidoError` y exportación JSON):**
  ```bash
  python ejercicio_2_productos/logica_catalogo.py
  ```

---

## Ejecución del Panel Web en Django (Ejercicio 3)

1. Aplicar las migraciones iniciales de sesiones/mensajes de Django:
   ```bash
   python ejercicio_3_auditoria_web/manage.py migrate
   ```
2. Iniciar el servidor de desarrollo:
   ```bash
   python ejercicio_3_auditoria_web/manage.py runserver
   ```
3. Abrir en el navegador: http://127.0.0.1:8000/
   - **Pestaña Sensores térmicos:** `/`
   - **Pestaña Catálogo y stock:** `/catalogo/`
   - **Pestaña Huella de carbono:** `/sustentabilidad/`