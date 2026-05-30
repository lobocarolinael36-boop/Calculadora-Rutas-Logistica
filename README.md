# Calculadora Dinámica de Rutas Logísticas

Aplicación de escritorio desarrollada en Python que optimiza rutas de entrega integrando datos de tráfico en tiempo real, geocodificación y condiciones meteorológicas.

## 🛠 Tecnologías y APIs utilizadas
* **Lenguaje:** Python
* **Interfaz Gráfica:** Tkinter, tkintermapview
* **Geocodificación:** Nominatim API (OpenStreetMap)
* **Enrutamiento:** Project OSRM API
* **Meteorología:** Open-Meteo API

##  Fundamentación
En el sector de la logística, el desconocimiento de las condiciones viales y climáticas genera retrasos críticos. Esta aplicación permite a los repartidores anticipar riesgos mediante:
- Cálculo de distancias y tiempos de viaje.
- Ajuste de tiempos según densidad de tráfico por franja horaria.
- Alertas visuales sobre condiciones climáticas adversas (tormentas, lluvias) en el punto de destino.


##  Cómo ejecutar
1. Asegúrate de tener instalado Python.
2. Instala las librerías necesarias:
   `pip install requests tkintermapview`
3. Ejecuta el archivo principal:
   `python nombre_de_tu_archivo.py`
