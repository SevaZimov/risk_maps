import folium
from folium.plugins import MarkerCluster
import pandas as pd
import json
from branca.element import Template, MacroElement

# Загрузка GeoJSON с регионами России
with open("russia_regions.geojson", "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# Загрузка данных из Excel
df_filials = pd.read_excel('filial.xlsx', engine='openpyxl')
df_cac = pd.read_excel('coin_acceptance_centers.xlsx', engine='openpyxl')

# Извлечение координат филиалов
namesf = df_filials['Unnamed: 2'][3:]
latitudesf = df_filials['Unnamed: 5'][3:]
longitudesf = df_filials['Unnamed: 6'][3:]

# Извлечение координат центров приёма монет
namesb = df_cac['Unnamed: 1'][4:]
latitudesb = df_cac['Unnamed: 4'][4:]
longitudesb = df_cac['Unnamed: 5'][4:]

# Создаем карту (центр России)
m = folium.Map(location=[60, 100], zoom_start=4, tiles="OpenStreetMap")

all_points_layer = MarkerCluster(name="Все точки").add_to(m)

# Добавляем филиалы
for x in range(3, len(namesf) + 3):
    folium.Marker(
        location=[latitudesf[x], longitudesf[x]],
        popup=f"Филиал: {namesf[x]}",
        icon=folium.Icon(color="blue", icon="bank"),
    ).add_to(all_points_layer)

# Добавляем центры приёма монет
for x in range(4, len(namesb) + 4):
    folium.Marker(
        location=[latitudesb[x], longitudesb[x]],
        popup=f"Центр приёма: {namesb[x]}",
        icon=folium.Icon(color="green", icon="coin"),
    ).add_to(all_points_layer)

m.save("map.html")
print("Карта сохранена в map.html")




