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

# Параметры кругов (теперь передаем массив центров и радиусов)
circles = [
    {"center": [48.0, 37.8], "radius": 20000, "color": "red"},
    {"center": [47.8, 38.2], "radius": 20000, "color": "red"},
    {"center": [48.2, 37.6], "radius": 20000, "color": "red"}
]

# Создаем круги и собираем их полигоны для проверки
circle_polys = []
for circle in circles:
    folium.Circle(
        location=circle["center"],
        radius=circle["radius"],
        color="black",
        weight=1,
        fill_opacity=0.6,
        opacity=1,
        fill_color=circle["color"],
        fill=False,
        popup=f"Радиус: {circle['radius']} метров",
    ).add_to(m)

    # Создаем полигон круга для проверки точек
    circle_poly = Point(circle["center"][1], circle["center"][0]).buffer(circle["radius"] / 111320)
    circle_polys.append(circle_poly)

# Создаем полигон из GeoJSON для проверки точек
polygon = shape(geojson_data['geometry'])


# Функция для генерации случайной точки внутри полигона
def random_point_in_polygon(poly):
    minx, miny, maxx, maxy = poly.bounds
    while True:
        p = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if poly.contains(p):
            return p


# Создаем список всех меток
all_markers = []

# Генерируем 10 меток внутри полигона
for i in range(10):
    p = random_point_in_polygon(polygon)
    marker_id = str(uuid.uuid4())
    marker_data = {
        "id": marker_id,
        "location": [p.y, p.x],
        "point": p  # Объект Point для проверки
    }
    all_markers.append(marker_data)

# Проверяем, какие метки находятся внутри хотя бы одного круга
markers_in_any_circle = []

for marker in all_markers:
    in_circle = False
    for circle_poly in circle_polys:
        if marker["point"].within(circle_poly):
            in_circle = True
            break

    if in_circle:
        markers_in_any_circle.append(marker["id"])
        # Добавляем на карту с зеленым маркером (внутри круга)
        folium.Marker(
            location=marker["location"],
            popup=f"ID: {marker['id']} (внутри круга)",
            icon=folium.Icon(color="green")
        ).add_to(m)
    else:
        # Добавляем на карту с синим маркером (снаружи всех кругов)
        folium.Marker(
            location=marker["location"],
            popup=f"ID: {marker['id']} (вне кругов)",
            icon=folium.Icon(color="blue")
        ).add_to(m)

# Выводим список ID меток внутри кругов
print("Метки внутри кругов (ID):")
for marker_id in markers_in_any_circle:
    print(f"- {marker_id}")

# Сохраняем карту в HTML файл
file_path = "map_with_multiple_circles.html"
m.save(file_path)

# Открываем HTML файл в браузере
webbrowser.open('file://' + os.path.realpath(file_path))