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

region_colors = {
    "Москва": "red",
    "Иркутская область": "red",
    "Магаданская область": "red",
    "Амурская область": "red",
    "Томская область": "red",
    "Костромская область": "red",
    "Приморский край": "#FF8000",
    "Еврейская автономная область": "#FF8000",
    "Забайкальский край": "#FF8000",
    "Республика Бурятия": "#FF8000",
    "Республика Тыва": "#FF8000",
    "Республика Алтай": "#FF8000",
    "Тюменская область": "#FF8000",
    "Республика Башкортостан": "#FF8000",
    "Челябинская область": "#FF8000",
    "Республика Коми": "#FF8000",
    "Архангельская область": "#FF8000",
    "Республика Карелия": "#FF8000",
    "Мурманская область": "#FF8000",
    "Республика Марий Эл": "#FF8000",
    "Чувашская Республика": "#FF8000",
    "Чукотский автономный округ": "#d77d31",
    "Ханты-Мансийский автономный округ — Югра": "#d77d31",
    "Омская область": "#d77d31",
    "Кировская область": "#d77d31",
    "Республика Ингушетия": "#d77d31",
"Вологодская область": "#d77d31",
"Нижегородская область": "#d77d31",
"Республика Мордовия": "#d77d31",
"Пензенская область": "#d77d31",
"Ростовская область": "#d77d31",
"Астраханская область": "#d77d31",
"Республика Дагестан": "#d77d31",
"Карачаево-Черскесская Республика": "#d77d31",
"Камчатский край": "#d77d31",
"Республика Хакасия": "#ffff01",
"Кемеровская область": "#ffff01",
"Алтайский край": "#ffff01",
"Новосибирская область": "#ffff01",
"Ямало-Ненецкий автономный округ": "#ffff01",
"Курганская область": "#ffff01",
"Свердловская область": "#ffff01",
"Оренбургская область": "#ffff01",
"Пермский край": "#ffff01",
"Ульяновская область": "#ffff01",
"Республика Татарстан": "#ffff01",
"Саратовская область": "#ffff01",
"Тамбовская область": "#ffff01",
"Волгоградская область": "#ffff01",
"Липецкая область": "#ffff01",
"Тульская область": "#ffff01",
"Рязанская область": "#ffff01",
"Орловская область": "#ffff01",
"Московская область": "#ffff01",
"Владимирская область": "#ffff01",
"Ивановская область": "#ffff01",
"Ярославская область": "#ffff01",
"Тверская область": "#ffff01",
"Ленинградская область": "#ffff01",
"Псковская область": "#ffff01",
"Новгородская область": "#ffff01",
"Смоленская область": "#ffff01",
"Республика Калмыкия": "#ffff01",
"Ставропольский край": "#ffff01",
"Краснодарский край": "#ffff01",
"Кабардино-Балкарская Республика": "#ffff01",
"Белгородская область": "#ffff01",
"Республика Крым": "#ffff01",

    "Санкт-Петербург": "#ffff01",
    "Красноярский край": "#7c1b1e",
    "Республика Саха (Якутия)": "#7c1b1e",
    "Хабаровский край": "#7c1b1e",
    "Сахалинская область": "#7c1b1e",
    "Чеченская Республика": "#7c1b1e",

}


# Функция для определения цвета региона
def get_region_color(feature):
    region_name = feature['properties']['region']
    return region_colors.get(region_name, "white")  # Серый для неуказанных регионов

# Создаем слой с кластерами маркеров
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

# Создаем слой регионов с упрощенной подсказкой
regions_layer = folium.FeatureGroup(name="Регионы").add_to(m)
folium.GeoJson(
    geojson_data,
    style_function=lambda feature: {
        "fillColor": get_region_color(feature),
        "color": "black",
        "weight": 1,
        "fillOpacity": 0.5,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["region"],  # Только название региона
        aliases=[""],  # Убираем префикс
        localize=True,
        style=("font-weight: bold; font-size: 14px;")  # Стиль подсказки
    ),
).add_to(regions_layer)

# Добавляем управление слоями
folium.LayerControl().add_to(m)

# Создаем HTML-шаблон для легенды
template = """
{% macro html(this, kwargs) %}
<div style="
    position: fixed; 
    bottom: 20px;
    left: 50px;
    width: 250px;
    height: auto;
    z-index:9999;
    font-size:14px;
    background-color:white;
    padding:10px;
    border-radius:5px;
    border:2px solid grey;
">
    <p style="font-weight:bold; margin-top:0; margin-bottom:10px;">Легенда карты</p>
    <div style="display: flex; align-items: center; margin-bottom: 5px;">
        <div style="width:20px; height:20px; background:green; margin-right:10px; border:1px solid black;"></div>
        <span>Филиалы и банкоматы Сбера</span>
    </div>
    <div style="display: flex; align-items: center;">
        <div style="width:20px; height:20px; background:#7c1b1e; margin-right:10px; border:1px solid black;"></div>
        <span>Чрезвычайная степень пожарной опасности</span>
    </div>
    <div style="display: flex; align-items: center; margin-bottom: 5px;">
        <div style="width:20px; height:20px; background:red; margin-right:10px; border:1px solid black;"></div>
        <span>Высокая степень пожарной опасности</span>
    </div>
    <div style="display: flex; align-items: center; margin-bottom: 5px;">
        <div style="width:20px; height:20px; background:#FF8000; margin-right:10px; border:1px solid black;"></div>
        <span>Степень пожарной опасности выше среднего</span>
    </div>
    <div style="display: flex; align-items: center; margin-bottom: 5px;">
        <div style="width:20px; height:20px; background:#d77d31; margin-right:10px; border:1px solid black;"></div>
        <span>Средняя степень пожарной опасности</span>
    </div>
    <div style="display: flex; align-items: center; margin-bottom: 5px;">
        <div style="width:20px; height:20px; background:#ffff01; margin-right:10px; border:1px solid black;"></div>
        <span>Степень пожарной опасности ниже среднего</span>
    </div>
    <div style="display: flex; align-items: center;">
        <div style="width:20px; height:20px; background:#FFFFFF; margin-right:10px; border:1px solid black;"></div>
        <span>Низкая степень пожарной опасности</span>
    </div>
</div>
{% endmacro %}
"""

# Добавляем легенду на карту
macro = MacroElement()
macro._template = Template(template)
m.get_root().add_child(macro)

# Сохраняем карту
m.save("index.html")
print("Карта сохранена в index.html")