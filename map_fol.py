import sys
import folium
import json
import webbrowser
import os
import random
import uuid
from shapely.geometry import Point, Polygon, shape
import pandas as pd
from datetime import datetime
from geopy.geocoders import Yandex
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                             QLabel, QLineEdit, QPushButton, QTextEdit, QSpinBox, QMessageBox,
                             QFormLayout)
from PyQt5.QtCore import Qt

geolocator = Yandex(api_key='2af9c564-6477-4c0e-93bc-bc3797d3f3a5')


class CircleMarkerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Статус персонала")
        self.setGeometry(100, 100, 800, 600)

        self.circles = []
        self.all_markers = []
        self.markers_in_circles = []
        self.circle_info = []

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Секция ввода количества точек
        points_layout = QHBoxLayout()
        points_layout.addWidget(QLabel("Количество случайных точек:"))
        self.point_count_input = QSpinBox()
        self.point_count_input.setRange(1, 1000)
        self.point_count_input.setValue(10)
        points_layout.addWidget(self.point_count_input)
        points_layout.addStretch()
        main_layout.addLayout(points_layout)

        # Секция добавления кругов (теперь с раздельными полями адреса)
        address_layout = QFormLayout()

        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Например: Донецк")
        address_layout.addRow("Город:", self.city_input)

        self.street_input = QLineEdit()
        self.street_input.setPlaceholderText("Например: Университетская")
        address_layout.addRow("Улица:", self.street_input)

        self.house_input = QLineEdit()
        self.house_input.setPlaceholderText("Например: 23")
        address_layout.addRow("Дом:", self.house_input)

        main_layout.addLayout(address_layout)

        # Радиус круга
        radius_layout = QHBoxLayout()
        radius_layout.addWidget(QLabel("Радиус зоны (метры):"))
        self.circle_radius_input = QLineEdit()
        self.circle_radius_input.setPlaceholderText("20000")
        radius_layout.addWidget(self.circle_radius_input)

        add_circle_btn = QPushButton("Добавить зону")
        add_circle_btn.clicked.connect(self.add_circle)
        radius_layout.addWidget(add_circle_btn)
        main_layout.addLayout(radius_layout)

        # Список кругов
        main_layout.addWidget(QLabel("Список зон:"))
        self.circles_list = QTextEdit()
        self.circles_list.setReadOnly(True)
        main_layout.addWidget(self.circles_list)

        # Кнопки управления
        buttons_layout = QHBoxLayout()
        generate_btn = QPushButton("Сгенерировать точки")
        generate_btn.clicked.connect(self.generate_points)
        buttons_layout.addWidget(generate_btn)

        clear_btn = QPushButton("Очистить зоны")
        clear_btn.clicked.connect(self.clear_circles)
        buttons_layout.addWidget(clear_btn)

        export_btn = QPushButton("Экспорт в Excel")
        export_btn.clicked.connect(self.export_to_excel)
        buttons_layout.addWidget(export_btn)

        exit_btn = QPushButton("Выход")
        exit_btn.clicked.connect(self.close)
        buttons_layout.addWidget(exit_btn)
        main_layout.addLayout(buttons_layout)

        # Результаты
        main_layout.addWidget(QLabel("Результаты:"))
        self.results_output = QTextEdit()
        self.results_output.setReadOnly(True)
        main_layout.addWidget(self.results_output)

        # Статус
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def add_circle(self):
        try:
            # Получаем данные из полей адреса
            city = self.city_input.text().strip()
            street = self.street_input.text().strip()
            house = self.house_input.text().strip()
            radius_text = self.circle_radius_input.text().strip()

            # Проверяем обязательные поля
            if not city:
                self.show_status("Укажите хотя бы город", "red")
                return

            if not radius_text:
                self.show_status("Укажите радиус зоны", "red")
                return

            # Формируем полный адрес
            address_parts = [city]
            if street:
                address_parts.append(street)
                if house:
                    address_parts.append(house)
            full_address = ", ".join(address_parts)

            # Геокодируем адрес
            location = geolocator.geocode(full_address)
            if not location:
                self.show_status("Не удалось определить координаты по указанному адресу", "red")
                return

            radius = int(radius_text)

            self.circles.append({
                "center": [location.latitude, location.longitude],
                "radius": radius,
                "color": "red",
                "address": full_address  # Сохраняем адрес для отображения
            })

            # Обновляем список кругов
            circles_text = "\n".join([f"Зона {i + 1}: {c['address']}, радиус: {c['radius']} м"
                                      for i, c in enumerate(self.circles)])
            self.circles_list.setPlainText(circles_text)

            # Очищаем поля ввода
            self.city_input.clear()
            self.street_input.clear()
            self.house_input.clear()
            self.circle_radius_input.clear()

            self.show_status(f"Зона добавлена по адресу: {full_address}", "green")

        except ValueError:
            self.show_status("Радиус должен быть целым числом", "red")
        except Exception as e:
            self.show_status(f"Ошибка: {str(e)}", "red")

    def clear_circles(self):
        self.circles = []
        self.circles_list.clear()
        self.show_status("Все зоны удалены", "green")

    def generate_points(self):
        try:
            point_count = self.point_count_input.value()

            if not self.circles:
                self.show_status("Добавьте хотя бы одну зону!", "red")
                return

            geojson_data = self.load_geojson("Donetska.geojson")
            polygon = shape(geojson_data['geometry'])

            self.all_markers = self.generate_random_points(polygon, point_count)
            self.markers_in_circles, self.circle_info = self.check_points_in_circles(self.all_markers, self.circles)

            report = []
            for i, circle in enumerate(self.circle_info):
                circle_address = self.circles[i]["address"]
                report.append(f"Зона {i + 1}:")
                report.append(f"Адрес: {circle_address}")
                report.append(f"Координаты: {circle['center']}, Радиус: {circle['radius']} м")
                report.append(f"Маркеров внутри: {len(circle['markers'])}")
                if circle['markers']:
                    report.append("ID маркеров:")
                    report.extend(circle['markers'])
                report.append("")

            report.append(f"Всего маркеров в зонах: {len(self.markers_in_circles)}")
            report.append(f"Всего маркеров вне зон: {len(self.all_markers) - len(self.markers_in_circles)}")

            self.results_output.setPlainText("\n".join(report))

            map_file = self.create_map(geojson_data, self.circles, self.all_markers, self.markers_in_circles)
            webbrowser.open('file://' + os.path.realpath(map_file))

            self.show_status("Точки сгенерированы и проверены", "green")

        except Exception as e:
            self.show_status(f"Ошибка: {str(e)}", "red")

    def export_to_excel(self):
        try:
            if not self.all_markers:
                self.show_status("Сначала сгенерируйте точки!", "red")
                return

            excel_path = self.save_to_excel(self.circle_info, self.all_markers)
            self.show_status(f"Данные сохранены в {excel_path}", "green")
            os.startfile(os.path.dirname(os.path.abspath(excel_path)))

        except Exception as e:
            self.show_status(f"Ошибка при экспорте: {str(e)}", "red")

    def show_status(self, message, color):
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    # Остальные методы остаются без изменений
    def load_geojson(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def create_map(self, geojson_data, circles, all_markers, markers_in_circles):
        coordinates = geojson_data['geometry']['coordinates'][0]
        lats = [coord[1] for coord in coordinates]
        lons = [coord[0] for coord in coordinates]
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)

        m = folium.Map(location=[center_lat, center_lon], zoom_start=8, tiles="CartoDB Positron")


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
                popup=f"Зона {i + 1}\nАдрес: {circle.get('address', 'Нет данных')}\nРадиус: {circle['radius']} м",
            ).add_to(m)

        markers_in_ids = {marker["id"] for marker in markers_in_circles}

        for marker in all_markers:
            if marker["id"] in markers_in_ids:
                folium.Marker(
                    location=marker["location"],
                    popup=f"ID: {marker['id']}\nВ зоне: Да",
                    icon=folium.Icon(color="green")
                ).add_to(m)
            else:
                folium.Marker(
                    location=marker["location"],
                    popup=f"ID: {marker['id']}\nВ зоне: Нет",
                    icon=folium.Icon(color="blue")
                ).add_to(m)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"map_with_circles_{timestamp}.html"
        m.save(file_path)
        return file_path

    def generate_random_points(self, polygon, count):
        points = []
        for _ in range(count):
            p = self.random_point_in_polygon(polygon)
            marker_id = str(uuid.uuid4())
            points.append({
                "id": marker_id,
                "location": [p.y, p.x],
                "point": p
            })
        return points

    def random_point_in_polygon(self, poly):
        minx, miny, maxx, maxy = poly.bounds
        while True:
            p = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
            if poly.contains(p):
                return p

    def check_points_in_circles(self, points, circles):
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

            for marker_id in circle_markers:
                if marker_id not in [m["id"] for m in markers_in_circles]:
                    marker = next(m for m in points if m["id"] == marker_id)
                    markers_in_circles.append(marker)

        return markers_in_circles, circle_info

    def save_to_excel(self, circle_info, all_markers):
        data = []

        for i, circle in enumerate(circle_info):
            circle_address = self.circles[i]["address"]
            for marker_id in circle["markers"]:
                marker = next(m for m in all_markers if m["id"] == marker_id)
                data.append({
                    "ID маркера": marker_id,
                    "Зона №": circle["circle_num"],
                    "Адрес зоны": circle_address,
                    "Координаты центра": f"{circle['center'][0]}, {circle['center'][1]}",
                    "Радиус (м)": circle["radius"],
                    "Координаты маркера": f"{marker['location'][0]}, {marker['location'][1]}",
                    "В зоне": "Да"
                })

        markers_in_circles_ids = [marker["id"] for marker in all_markers if
                                  any(marker["id"] in circle["markers"] for circle in circle_info)]

        for marker in all_markers:
            if marker["id"] not in markers_in_circles_ids:
                data.append({
                    "ID маркера": marker["id"],
                    "Зона №": "",
                    "Адрес зоны": "",
                    "Координаты центра": "",
                    "Радиус (м)": "",
                    "Координаты маркера": f"{marker['location'][0]}, {marker['location'][1]}",
                    "В зоне": "Нет"
                })

        df = pd.DataFrame(data)
        columns_order = ["ID маркера", "Зона №", "Адрес зоны", "Координаты центра",
                         "Радиус (м)", "Координаты маркера", "В зоне"]
        df = df[columns_order]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_path = f"markers_info_{timestamp}.xlsx"
        df.to_excel(excel_path, index=False)

        return excel_path


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CircleMarkerApp()
    window.show()
    sys.exit(app.exec_())