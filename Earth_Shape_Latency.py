# Programa: Earth_Shape_Latency
# Autor: Pablo Galván
# Fecha: 16/08/2025
# Descripción: Analizar señales de internet, como tiempos de latencia a través de comandos como traceroute o ping, 
# para verificar la forma de la Tierra. Este enfoque se basa en medir los tiempos de propagación de paquetes de datos a través de 
# cables submarinos de fibra óptica, que siguen rutas geográficas reales en la superficie terrestre. Al comparar estos tiempos con 
# modelos geométricos (esférico vs. plano), se puede determinar cuál se ajusta mejor a los datos observados, y los resultados consistentes.

import subprocess
import re
import math
import matplotlib.pyplot as plt
from geopy.distance import great_circle
import platform


VELOCIDAD_FIBRA = 200_000  # km/s (aprox 2/3 de la luz)

# ------------------------------
# FUNCIONES AUXILIARES
# ------------------------------

def ejecutar_ping(host, count=4):
    """
    Ejecuta ping a un host y devuelve la menor latencia en ms.
    Compatible con Windows y Unix.
    """
    param = "-n" if platform.system().lower() == "windows" else "-c"
    try:
        resultado = subprocess.run(["ping", param, str(count), host], capture_output=True, text=True)
        # Buscar patrones de tiempo en ms
        match = re.findall(r"tiempo[=<](\d+)ms", resultado.stdout, re.IGNORECASE)
        if not match:
            match = re.findall(r"time[=<](\d+)ms", resultado.stdout, re.IGNORECASE)
        if match:
            latencias = [int(x) for x in match]
            return min(latencias)
    except Exception as e:
        print(f"Error ejecutando ping a {host}: {e}")
    return None

def distancia_esferica(coord1, coord2):
    """Distancia sobre la superficie de la esfera (Tierra)"""
    return great_circle(coord1, coord2).km

def distancia_plana(coord1, coord2):
    """Distancia plana usando coordenadas proyectadas simple"""
    lat1, lon1 = map(math.radians, coord1)
    lat2, lon2 = map(math.radians, coord2)
    x = (lon2 - lon1) * math.cos((lat1 + lat2) / 2)
    y = lat2 - lat1
    return math.sqrt(x**2 + y**2) * 6371  # radio promedio Tierra en km

def distancia_disco(coord1, coord2):
    """Distancia en modelo disco (2D) simplificado"""
    x1, y1 = coord1[1], coord1[0]
    x2, y2 = coord2[1], coord2[0]
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2) * 111  # 1° aprox 111 km

def latencia_a_distancia(latencia_ms):
    """Convierte latencia en ms a distancia estimada en km"""
    return (latencia_ms / 2000) * VELOCIDAD_FIBRA

# ------------------------------
# CIUDADES Y HOSTS
# ------------------------------

ciudades = {
    "Sídney": (-33.8688, 151.2093),
    "Buenos Aires": (-34.6037, -58.3816),
    "Londres": (51.5074, -0.1278),
    "Tokio": (35.6895, 139.6917),
    "Nueva York": (40.7128, -74.0060),
    "Johannesburgo": (-26.2041, 28.0473),
    "París": (48.8566, 2.3522),
    "Los Ángeles": (34.0522, -118.2437),
    "Singapur": (1.3521, 103.8198),
    "Moscú": (55.7558, 37.6173),
    "Toronto": (43.65107, -79.347015),
    "Beijing": (39.9042, 116.4074),
    "Delhi": (28.6139, 77.209),
    "Sao Paulo": (-23.5505, -46.6333),
    "México": (19.4326, -99.1332),
    "Estambul": (41.0082, 28.9784),
    "Seúl": (37.5665, 126.978),
    "Dubai": (25.276987, 55.296249),
    "Johor Bahru": (1.4927, 103.7414),
    "Kuala Lumpur": (3.139, 101.6869),
    "Bangkok": (13.7563, 100.5018),
    "Hong Kong": (22.3193, 114.1694),
    "Barcelona": (41.3851, 2.1734),
    "Chicago": (41.8781, -87.6298),
    "Miami": (25.7617, -80.1918),
    "San Francisco": (37.7749, -122.4194),
    "Melbourne": (-37.8136, 144.9631),
    "Rome": (41.9028, 12.4964)
}

hosts = {
    "Cloudflare": "1.1.1.1",
    "Cloudflare Secundario": "1.0.0.1",
    "Google DNS": "8.8.8.8",
    "Google DNS Secundario": "8.8.4.4",
    "OpenDNS": "208.67.222.222",
    "OpenDNS Secundario": "208.67.220.220",
    "Quad9": "9.9.9.9",
    "Quad9 Secundario": "149.112.112.112"
}

# ------------------------------
# MENÚ DE SELECCIÓN
# ------------------------------

print("==============================")
print(" EXPERIMENTO: Verificar forma de la Tierra")
print("==============================")

ciudades_disponibles = list(ciudades.keys())
for i, ciudad in enumerate(ciudades_disponibles):
    print(f"{i+1}. {ciudad}")

seleccion = input("Seleccione las ciudades separadas por comas (ej: 1,3,5) o 'all' para todas: ").strip()
if seleccion.lower() == 'all':
    seleccionadas = ciudades_disponibles
else:
    indices = [int(x)-1 for x in seleccion.split(",") if x.strip().isdigit() and 0 < int(x) <= len(ciudades_disponibles)]
    seleccionadas = [ciudades_disponibles[i] for i in indices]

pares = [(origen, destino) for origen in seleccionadas for destino in seleccionadas if origen != destino]

labels = []
errors_esfera = []
errors_plano = []
errors_disco = []

for origen, destino in pares:
    print(f"\n--- {origen} -> {destino} ---")
    latencia = None
    for nombre_host, ip in hosts.items():
        latencia = ejecutar_ping(ip)
        if latencia:
            print(f"Latencia hacia {nombre_host} ({ip}): {latencia} ms")
            break

    if latencia:
        distancia_observada = latencia_a_distancia(latencia)
        distancia_esfera_val = distancia_esferica(ciudades[origen], ciudades[destino])
        distancia_plano_val = distancia_plana(ciudades[origen], ciudades[destino])
        distancia_disco_val = distancia_disco(ciudades[origen], ciudades[destino])

        print(f"Distancia estimada (observada): {distancia_observada:.0f} km")
        print(f"Modelo esférico: {distancia_esfera_val:.0f} km")
        print(f"Modelo plano: {distancia_plano_val:.0f} km")
        print(f"Modelo disco: {distancia_disco_val:.0f} km")

        error_esfera = abs(distancia_observada - distancia_esfera_val)
        error_plano = abs(distancia_observada - distancia_plano_val)
        error_disco = abs(distancia_observada - distancia_disco_val)

        errors_esfera.append(error_esfera)
        errors_plano.append(error_plano)
        errors_disco.append(error_disco)
        labels.append(f"{origen}->{destino}")

        min_error = min(error_esfera, error_plano, error_disco)
        if min_error == error_esfera:
            print("➡ Los datos se ajustan mejor al modelo ESFÉRICO.")
        elif min_error == error_plano:
            print("➡ Los datos se ajustan mejor al modelo PLANO.")
        else:
            print("➡ Los datos se ajustan mejor al modelo DISCO.")
    else:
        print("No se pudo obtener latencia hacia ningún host.")
        labels.append(f"{origen}->{destino}")
        errors_esfera.append(0)
        errors_plano.append(0)
        errors_disco.append(0)

# ------------------------------
# GRAFICA DE ERRORES
# ------------------------------

x = range(len(labels))
plt.bar(x, errors_esfera, width=0.25, label="Error Modelo Esférico", align='center')
plt.bar([i + 0.25 for i in x], errors_plano, width=0.25, label="Error Modelo Plano", align='center')
plt.bar([i + 0.5 for i in x], errors_disco, width=0.25, label="Error Modelo Disco", align='center')
plt.xticks([i + 0.25 for i in x], labels, rotation=90)
plt.ylabel("Error absoluto (km)")
plt.title("Comparación de errores entre modelos")
plt.legend()
plt.tight_layout()
plt.savefig("comparacion_modelos.png")
plt.show()
print("\nLa gráfica ha sido guardada como 'comparacion_modelos.png'.")
