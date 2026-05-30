import tkinter as tk
from tkinter import messagebox
import requests
import tkintermapview
from datetime import datetime

def calcular_recorrido():
    direccion_salida = entrada_salida.get()
    direccion_destino = entrada_destino.get()
    hora_texto = entrada_hora.get()
    
    if not direccion_salida or not direccion_destino or not hora_texto:
        messagebox.showwarning("Faltan datos", "Por favor, complete todos los campos.")
        return

    # Validacion y logica de la hora ingresada
    try:
        # Convertimos el texto ingresado a un objeto de tiempo
        hora_salida = datetime.strptime(hora_texto, "%H:%M").time()
    except ValueError:
        messagebox.showwarning("Formato invalido", "Ingrese la hora en formato HH:MM (Ejemplo: 08:30 o 17:45).")
        return

    # Calculamos la hora en formato decimal para facilitar las comparaciones (ej: 8:30 -> 8.5)
    hora_decimal = hora_salida.hour + (hora_salida.minute / 60.0)

    # Determinacion de factor de trafico segun la hora
    if 7.0 <= hora_decimal < 10.0:
        factor_trafico = 2.0
        estado_trafico = "Hora Pico (Manana) - Demora"
    elif 16.0 <= hora_decimal < 19.0:
        factor_trafico = 2.5
        estado_trafico = "Hora Pico (Tarde) - Demora Severa"
    elif 10.0 <= hora_decimal < 16.0:
        factor_trafico = 1.2
        estado_trafico = "Trafico Normal"
    else:
        factor_trafico = 1.0
        estado_trafico = "Trafico Fluido (Noche)"

    boton_calcular.config(text="Calculando...", state="disabled")
    root.update_idletasks()

    try:
        url_geo = "https://nominatim.openstreetmap.org/search"
        headers = {'User-Agent': 'LogisticaApp/1.0'} 
        
        # Geocodificacion Origen
        res_salida = requests.get(url_geo, params={"format": "json", "q": f"{direccion_salida}, CABA, Argentina"}, headers=headers)
        datos_salida = res_salida.json()
        if not datos_salida:
            raise Exception("No se encontro la direccion de salida.")
        lat_salida = float(datos_salida[0]["lat"])
        lon_salida = float(datos_salida[0]["lon"])

        # Geocodificacion Destino
        res_destino = requests.get(url_geo, params={"format": "json", "q": f"{direccion_destino}, CABA, Argentina"}, headers=headers)
        datos_destino = res_destino.json()
        if not datos_destino:
            raise Exception("No se encontro la direccion de destino.")
        lat_destino = float(datos_destino[0]["lat"])
        lon_destino = float(datos_destino[0]["lon"])

        # Peticion OSRM (Rutas)
        url_ruta = f"https://router.project-osrm.org/route/v1/driving/{lon_salida},{lat_salida};{lon_destino},{lat_destino}?overview=full&geometries=geojson"
        res_ruta = requests.get(url_ruta)
        datos_ruta = res_ruta.json()

        if "routes" not in datos_ruta:
            raise Exception("Ruta no disponible.")

        distancia_km = datos_ruta["routes"][0]["distance"] / 1000
        tiempo_min = int((datos_ruta["routes"][0]["duration"] / 60) * factor_trafico)
        coordenadas_linea = datos_ruta["routes"][0]["geometry"]["coordinates"]

        # Peticion Open-Meteo (Clima)
        url_clima = f"https://api.open-meteo.com/v1/forecast?latitude={lat_destino}&longitude={lon_destino}&current=temperature_2m,weather_code"
        res_clima = requests.get(url_clima)
        datos_clima = res_clima.json()

        temperatura = datos_clima["current"]["temperature_2m"]
        codigo_clima = datos_clima["current"]["weather_code"]

        estado_cielo = "Despejado"
        if 51 <= codigo_clima <= 67: 
            estado_cielo = "Lluvioso"
        elif codigo_clima >= 95: 
            estado_cielo = "Tormenta"

        # Actualizacion de Interfaz Grafica
        txt_resultado.config(text=f"Distancia: {distancia_km:.2f} Km\nTiempo estimado: {tiempo_min} Minutos")
        txt_clima.config(text=f"Clima en destino: {temperatura}°C ({estado_cielo})")

        # Alertas combinadas mostrando el estado del trafico detectado
        if estado_cielo == "Tormenta":
            txt_alerta.config(text=f"ALERTA: Tormenta detectada.\nTrafico: {estado_trafico}", fg="red")
        elif estado_cielo == "Lluvioso":
            txt_alerta.config(text=f"PRECAUCION: Calzada mojada.\nTrafico: {estado_trafico}", fg="orange")
        elif factor_trafico >= 2.0:
            txt_alerta.config(text=f"DEMORA: {estado_trafico}.", fg="orange")
        else:
            txt_alerta.config(text=f"Ruta segura.\nTrafico: {estado_trafico}.", fg="green")

        # Renderizado de Mapa
        mapa.delete_all_marker()
        mapa.delete_all_path()

        mapa.set_marker(lat_salida, lon_salida, text="Salida")
        mapa.set_marker(lat_destino, lon_destino, text="Destino")
        
        lista_camino = [(coord[1], coord[0]) for coord in coordenadas_linea]
        mapa.set_path(lista_camino, color="blue", width=4) 
        
        mapa.set_position((lat_salida + lat_destino) / 2, (lon_salida + lon_destino) / 2)
        mapa.set_zoom(13)

    except Exception as error:
        messagebox.showerror("Error de red", f"Se produjo un error de conexion:\n{error}")
        
    finally:
        boton_calcular.config(text="Calcular Recorrido", state="normal")

# Interfaz Tkinter
root = tk.Tk()
root.title("Gestor de Rutas Logisticas")
root.geometry("850x550")

frame_controles = tk.Frame(root, width=320, padx=10, pady=20)
frame_controles.pack(side=tk.LEFT, fill=tk.Y)
frame_controles.pack_propagate(False)

tk.Label(frame_controles, text="Salida (Ej: Obelisco):", font=("Arial", 11, "bold")).pack(anchor="w")
entrada_salida = tk.Entry(frame_controles, font=("Arial", 11))
entrada_salida.pack(fill=tk.X, pady=(0, 10))

tk.Label(frame_controles, text="Destino (Ej: Palermo):", font=("Arial", 11, "bold")).pack(anchor="w")
entrada_destino = tk.Entry(frame_controles, font=("Arial", 11))
entrada_destino.pack(fill=tk.X, pady=(0, 10))

tk.Label(frame_controles, text="Hora de Salida (HH:MM):", font=("Arial", 11, "bold")).pack(anchor="w")
entrada_hora = tk.Entry(frame_controles, font=("Arial", 11))
entrada_hora.pack(fill=tk.X, pady=(0, 15))
entrada_hora.insert(0, "17:30") # Hora de ejemplo por defecto

boton_calcular = tk.Button(frame_controles, text="Calcular Recorrido", bg="lightblue", font=("Arial", 11, "bold"), command=calcular_recorrido)
boton_calcular.pack(fill=tk.X, pady=10)

txt_resultado = tk.Label(frame_controles, text="Distancia: -\nTiempo estimado: -", font=("Arial", 12), fg="darkblue", justify="left")
txt_resultado.pack(pady=(15, 5))

txt_clima = tk.Label(frame_controles, text="Clima en destino: -", font=("Arial", 11), fg="purple")
txt_clima.pack(pady=5)

txt_alerta = tk.Label(frame_controles, text="", font=("Arial", 11, "bold"), justify="left")
txt_alerta.pack(pady=10)

frame_mapa = tk.Frame(root)
frame_mapa.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

mapa = tkintermapview.TkinterMapView(frame_mapa, corner_radius=0)
mapa.pack(fill=tk.BOTH, expand=True)
mapa.set_position(-34.6037, -58.3816)
mapa.set_zoom(12)

root.mainloop()