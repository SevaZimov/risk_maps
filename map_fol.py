import folium
from folium.plugins import Draw
import json
import webbrowser
import os
import random
import uuid
from shapely.geometry import Point, Polygon, shape
import PySimpleGUI as sg
import pandas as pd
from datetime import datetime


# Функция для загрузки GeoJSON
def load_geojson(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


# Функция для создания карты
def create_map(geojson_data, circles, all_markers, markers_in_circles):
    # Определяем центр карты
    coordinates = geojson_data['geometry']['coordinates'][0]
    lats = [coord[1] for coord in coordinates]
    lons = [coord[0] for coord in coordinates]
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)

    # Создаем карту
    m = folium.Map(location=[center_lat, center_lon], zoom_start=8, tiles="OpenStreetMap")

    # Добавляем GeoJson
    folium.GeoJson(
        geojson_data,
        name='Границы области',
        style_function=lambda feature: {
            'fillColor': 'blue',
            'color': 'blue',
            'weight': 2,
            'fillOpacity': 0.1
        }
    ).add_to(m)

    # Создаем круги с разными цветами
    colors = ['red', 'purple', 'orange', 'darkred', 'lightred', 'beige',
              'darkblue', 'darkgreen', 'cadetblue', 'darkpurple']

    for i, circle in enumerate(circles):
        color = colors[i % len(colors)]
        folium.Circle(
            location=circle["center"],
            radius=circle["radius"],
            color="black",
            weight=1,
            fill_opacity=0.3,
            opacity=1,
            fill_color=color,
            fill=True,
            popup=f"Круг {i + 1}\nРадиус: {circle['radius']} м\nКоординаты: {circle['center']}",
        ).add_to(m)

    # Добавляем все маркеры
    markers_in_ids = {marker["id"] for marker in markers_in_circles}

    for marker in all_markers:
        if marker["id"] in markers_in_ids:
            # Маркер внутри круга - зеленый
            folium.Marker(
                location=marker["location"],
                popup=f"ID: {marker['id']}\nВ круге: Да",
                icon=folium.Icon(color="green")
            ).add_to(m)
        else:
            # Маркер вне круга - синий
            folium.Marker(
                location=marker["location"],
                popup=f"ID: {marker['id']}\nВ круге: Нет",
                icon=folium.Icon(color="blue")
            ).add_to(m)

    # Сохраняем карту
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"map_with_circles_{timestamp}.html"
    m.save(file_path)
    return file_path


# Функция для генерации случайных точек
def generate_random_points(polygon, count):
    points = []
    for _ in range(count):
        p = random_point_in_polygon(polygon)
        marker_id = str(uuid.uuid4())
        points.append({
            "id": marker_id,
            "location": [p.y, p.x],
            "point": p
        })
    return points


# Функция для генерации случайной точки внутри полигона
def random_point_in_polygon(poly):
    minx, miny, maxx, maxy = poly.bounds
    while True:
        p = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if poly.contains(p):
            return p


# Функция для проверки точек в кругах
def check_points_in_circles(points, circles):
    circle_polys = []
    for circle in circles:
        circle_poly = Point(circle["center"][1], circle["center"][0]).buffer(circle["radius"] / 111320)
        circle_polys.append(circle_poly)

    markers_in_circles = []
    circle_info = []

    for i, circle_poly in enumerate(circle_polys):
        circle_markers = []
        for point in points:
            if point["point"].within(circle_poly):
                circle_markers.append(point["id"])

        circle_info.append({
            "circle_num": i + 1,
            "center": circles[i]["center"],
            "radius": circles[i]["radius"],
            "markers": circle_markers
        })

        # Добавляем маркеры в общий список (без дубликатов)
        for marker_id in circle_markers:
            if marker_id not in [m["id"] for m in markers_in_circles]:
                marker = next(m for m in points if m["id"] == marker_id)
                markers_in_circles.append(marker)

    return markers_in_circles, circle_info


# Функция для сохранения в Excel
def save_to_excel(circle_info, all_markers):
    data = []

    # Собираем данные по кругам
    for circle in circle_info:
        for marker_id in circle["markers"]:
            marker = next(m for m in all_markers if m["id"] == marker_id)
            data.append({
                "ID маркера": marker_id,
                "Круг №": circle["circle_num"],
                "Центр круга": f"{circle['center'][0]}, {circle['center'][1]}",
                "Радиус (м)": circle["radius"],
                "Координаты маркера": f"{marker['location'][0]}, {marker['location'][1]}",
                "В круге": "Да"
            })

    # Добавляем маркеры вне кругов
    markers_in_circles_ids = [marker["id"] for marker in all_markers if
                              any(marker["id"] in circle["markers"] for circle in circle_info)]

    for marker in all_markers:
        if marker["id"] not in markers_in_circles_ids:
            data.append({
                "ID маркера": marker["id"],
                "Круг №": "",
                "Центр круга": "",
                "Радиус (м)": "",
                "Координаты маркера": f"{marker['location'][0]}, {marker['location'][1]}",
                "В круге": "Нет"
            })

    # Создаем DataFrame и сохраняем в Excel
    df = pd.DataFrame(data)

    # Упорядочиваем столбцы
    df = df[["ID маркера", "Круг №", "Центр круга", "Радиус (м)", "Координаты маркера", "В круге"]]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_path = f"markers_info_{timestamp}.xlsx"
    df.to_excel(excel_path, index=False)

    return excel_path


# GUI Layout
layout = [
    [sg.Text("Количество случайных точек:")],
    [sg.Input(default_text="10", size=(10, 1), key="-POINT_COUNT-")],

    [sg.Text("Координаты круга (широта,долгота):")],
    [sg.Input(size=(20, 1), key="-CIRCLE_COORD-")],
    [sg.Text("Радиус круга (метры):")],
    [sg.Input(size=(10, 1), key="-CIRCLE_RADIUS-")],
    [sg.Button("Добавить круг")],

    [sg.Text("Список кругов:")],
    [sg.Multiline(size=(40, 5), key="-CIRCLES_LIST-", disabled=True)],

    [sg.Button("Сгенерировать точки"), sg.Button("Очистить круги"), sg.Button("Экспорт в Excel"), sg.Button("Выход")],

    [sg.Text("Результаты:")],
    [sg.Multiline(size=(40, 10), key="-OUTPUT-", disabled=True)],

    [sg.Text("", size=(40, 1), key="-STATUS-")]
]

# Создаем окно
window = sg.Window("Генератор кругов и точек", layout)

# Переменные для хранения данных
circles = []
all_markers = []
markers_in_circles = []
circle_info = []

# Основной цикл
while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == "Выход":
        break

    elif event == "Добавить круг":
        try:
            coord_text = values["-CIRCLE_COORD-"].strip()
            radius = int(values["-CIRCLE_RADIUS-"].strip())

            lat, lon = map(float, coord_text.split(','))
            circles.append({
                "center": [lat, lon],
                "radius": radius,
                "color": "red"
            })

            # Обновляем список кругов
            circles_list = "\n".join([f"Круг {i + 1}: {c['center']}, радиус: {c['radius']} м"
                                      for i, c in enumerate(circles)])
            window["-CIRCLES_LIST-"].update(circles_list)
            window["-STATUS-"].update("Круг успешно добавлен", text_color="green")

            # Очищаем поля ввода
            window["-CIRCLE_COORD-"].update("")
            window["-CIRCLE_RADIUS-"].update("")

        except Exception as e:
            window["-STATUS-"].update(f"Ошибка: {str(e)}", text_color="red")

    elif event == "Очистить круги":
        circles = []
        window["-CIRCLES_LIST-"].update("")
        window["-STATUS-"].update("Все круги удалены", text_color="green")

    elif event == "Сгенерировать точки":
        try:
            point_count = int(values["-POINT_COUNT-"])

            if not circles:
                window["-STATUS-"].update("Добавьте хотя бы один круг!", text_color="red")
                continue

            # Загружаем GeoJSON
            geojson_data = load_geojson("Donetska.geojson")
            polygon = shape(geojson_data['geometry'])

            # Генерируем случайные точки
            all_markers = generate_random_points(polygon, point_count)

            # Проверяем, какие точки в кругах
            markers_in_circles, circle_info = check_points_in_circles(all_markers, circles)

            # Формируем отчет
            report = []
            for i, circle in enumerate(circle_info):
                report.append(f"Круг {i + 1}:")
                report.append(f"Центр: {circle['center']}, Радиус: {circle['radius']} м")
                report.append(f"Маркеров внутри: {len(circle['markers'])}")
                if circle['markers']:
                    report.append("ID маркеров:")
                    report.extend(circle['markers'])
                report.append("")

            report.append(f"Всего маркеров в кругах: {len(markers_in_circles)}")
            report.append(f"Всего маркеров вне кругов: {len(all_markers) - len(markers_in_circles)}")

            window["-OUTPUT-"].update("\n".join(report))

            # Создаем и открываем карту
            map_file = create_map(geojson_data, circles, all_markers, markers_in_circles)
            webbrowser.open('file://' + os.path.realpath(map_file))

            window["-STATUS-"].update("Точки сгенерированы и проверены", text_color="green")

        except Exception as e:
            window["-STATUS-"].update(f"Ошибка: {str(e)}", text_color="red")

    elif event == "Экспорт в Excel":
        if not all_markers:
            window["-STATUS-"].update("Сначала сгенерируйте точки!", text_color="red")
            continue

        try:
            excel_path = save_to_excel(circle_info, all_markers)
            window["-STATUS-"].update(f"Данные сохранены в {excel_path}", text_color="green")
            # Открываем папку с файлом
            os.startfile(os.path.dirname(os.path.abspath(excel_path)))
        except Exception as e:
            window["-STATUS-"].update(f"Ошибка при экспорте: {str(e)}", text_color="red")

window.close()