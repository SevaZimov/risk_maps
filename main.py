import folium
from folium.plugins import MarkerCluster
import pandas as pd
import json
from branca.element import Template, MacroElement

# Загрузка GeoJSON с регионами России
with open("russia_regions.geojson", "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

import folium
from folium.plugins import Draw
import json
import webbrowser
import os
import random
import uuid
from shapely.geometry import Point, Polygon, shape

# Загрузка GeoJSON
with open("Donetska.geojson", "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# Определяем центр карты
coordinates = geojson_data['geometry']['coordinates'][0]
lats = [coord[1] for coord in coordinates]
lons = [coord[0] for coord in coordinates]
center_lat = sum(lats) / len(lats)
center_lon = sum(lons) / len(lons)

# Создаем карту
m = folium.Map(location=[center_lat, center_lon], zoom_start=8, tiles="OpenStreetMap")

# Добавляем GeoJson
geojson_layer = folium.GeoJson(
    geojson_data,
    name='Границы области',
    style_function=lambda feature: {
        'fillColor': 'blue',
        'color': 'blue',
        'weight': 2,
        'fillOpacity': 0.1
    }
).add_to(m)

# Параметры круга
circle_center = [48.0, 37.8]
radius = 300  # в метрах

# Создаем круг
folium.Circle(
    location=circle_center,
    radius=radius,
    color="black",
    weight=1,
    fill_opacity=0.6,
    opacity=1,
    fill_color="red",
    fill=False,
    popup="{} meters".format(radius),
).add_to(m)

# Создаем полигон из GeoJSON для проверки точек
polygon = shape(geojson_data['geometry'])

# Функция для генерации случайной точки внутри полигона
def random_point_in_polygon(poly):
    minx, miny, maxx, maxy = poly.bounds
    while True:
        p = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if poly.contains(p):
            return p

# Генерируем UUID для каждой метки и запоминаем те, что внутри круга
circle_poly = Point(circle_center[1], circle_center[0]).buffer(radius / 111320)
markers_inside_circle = []  # Список для хранения ID меток внутри круга

# Генерируем 3 метки внутри круга (зеленые)
for i in range(3):
    while True:
        p = random_point_in_polygon(polygon)
        if Point(p.x, p.y).within(circle_poly):
            marker_id = str(uuid.uuid4())  # Генерируем случайный UUID
            folium.Marker(
                location=[p.y, p.x],
                popup=f"ID: {marker_id} (внутри круга)",
                icon=folium.Icon(color="green")
            ).add_to(m)
            markers_inside_circle.append(marker_id)  # Запоминаем ID
            break

# Генерируем 3 метки вне круга, но внутри полигона (синие)
for i in range(3):
    while True:
        p = random_point_in_polygon(polygon)
        if not Point(p.x, p.y).within(circle_poly):
            marker_id = str(uuid.uuid4())  # Генерируем случайный UUID
            folium.Marker(
                location=[p.y, p.x],
                popup=f"ID: {marker_id} (вне круга)",
                icon=folium.Icon(color="blue")
            ).add_to(m)
            break

# Выводим список ID меток внутри круга
print("Метки внутри круга (ID):")
for marker_id in markers_inside_circle:
    print(f"- {marker_id}")

# Сохраняем карту в HTML файл
file_path = "map.html"
m.save(file_path)

# Открываем HTML файл в браузере
webbrowser.open('file://' + os.path.realpath(file_path))


