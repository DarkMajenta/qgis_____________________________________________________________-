from qgis.core import QgsVectorLayer, QgsCategorizedSymbolRenderer, QgsRendererCategory, QgsSymbol, QgsMarkerSymbol, QgsVectorLayerSimpleLabeling
from qgis.PyQt.QtGui import QColor
import requests
from PyQt5.QtCore import QVariant
from qgis.utils import plugins

# Установка плагинов
plugins['quick_map_services'] = plugins['map_tiler'] = plugins['gis4wrf'] = plugins['nowcast_tool'] = plugins['radolan2map'] = True

# Конфигурация OpenWeatherMap API
api_key = "api_key"
cities = ["Moscow", "Murmansk", "Arkhangelsk", "Voronezh"]

# Создание нового слоя точек для погоды
layer_weather = QgsVectorLayer("Point?crs=EPSG:4326", "Погода", "memory")
provider_weather = layer_weather.dataProvider()

# Определение атрибутов слоя погоды
provider_weather.addAttributes([QgsField("Город", QVariant.String),
                               QgsField("Температура", QVariant.Double),
                               QgsField("Влажность", QVariant.Double)])
layer_weather.updateFields()

# Создание нового слоя точек для карты
layer_cities = QgsVectorLayer("Point?crs=EPSG:4326", "Города", "memory")
provider_cities = layer_cities.dataProvider()

# Определение атрибутов слоя карты
provider_cities.addAttributes([QgsField("Город", QVariant.String)])
layer_cities.updateFields()

# Перебор городов
for city in cities:
    # Получение данных о погоде
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(url)
    data = response.json()

    # Извлечение координат местоположения
    longitude = data['coord']['lon']
    latitude = data['coord']['lat']

    # Создание геометрии точки для погоды
    point_weather = QgsGeometry.fromPointXY(QgsPointXY(longitude, latitude))

    # Создание фичи с данными о погоде
    feature_weather = QgsFeature()
    feature_weather.setGeometry(point_weather)
    feature_weather.setAttributes([city,
                                   data['main']['temp'] - 273.15,  # Конвертируем из Кельвина в Цельсий
                                   data['main']['humidity']])

    # Добавление фичи в провайдер слоя погоды
    provider_weather.addFeature(feature_weather)

    # Создание геометрии точки для карты
    point_cities = QgsGeometry.fromPointXY(QgsPointXY(longitude, latitude))

    # Создание фичи с данными о городе
    feature_cities = QgsFeature()
    feature_cities.setGeometry(point_cities)
    feature_cities.setAttributes([city])

    # Добавление фичи в провайдер слоя карты
    provider_cities.addFeature(feature_cities)

# Обновление экранных границ слоев
layer_weather.updateExtents()
layer_cities.updateExtents()

# Добавление слоев в проект QGIS
QgsProject.instance().addMapLayer(layer_weather)
QgsProject.instance().addMapLayer(layer_cities)

# Нанесение стилей на слои
symbol_weather = QgsMarkerSymbol.createSimple({'name': 'circle', 'color': 'blue'})
renderer_weather = QgsCategorizedSymbolRenderer('Город', [QgsRendererCategory('category', symbol_weather)])
layer_weather.setRenderer(renderer_weather)

symbol_cities = QgsMarkerSymbol.createSimple({'name': 'circle', 'color': 'red'})
renderer_cities = QgsCategorizedSymbolRenderer('Город', [QgsRendererCategory('Moscow', symbol_cities),
                                                          QgsRendererCategory('Murmansk', symbol_cities),
                                                          QgsRendererCategory('Arkhangelsk', symbol_cities),
                                                          QgsRendererCategory('Voronezh', symbol_cities)])
layer_cities.setRenderer(renderer_cities)

# Добавление слоя OpenStreetMap в проект QGIS
osm_layer = QgsVectorLayer("https://www.openstreetmap.org", "OpenStreetMap", "osm")
QgsProject.instance().addMapLayer(osm_layer)

# Создание и настройка подписей для слоя погоды
label_settings_weather = QgsPalLayerSettings()
label_settings_weather.fieldName = "Город"
label_settings_weather.enabled = True
label_settings_weather.placement = QgsPalLayerSettings.OverPoint
label_settings_weather.textColor = QColor(0, 0, 0)
label_settings_weather.fontSize = 8
layer_weather.setLabeling(QgsVectorLayerSimpleLabeling(label_settings_weather))
layer_weather.setLabelsEnabled(True)

# Создание и настройка подписей для слоя карты
label_settings_cities = QgsPalLayerSettings()
label_settings_cities.fieldName = "Город"
label_settings_cities.enabled = True
label_settings_cities.placement = QgsPalLayerSettings.OverPoint
label_settings_cities.textColor = QColor(0, 0, 0)
label_settings_cities.fontSize = 8
layer_cities.setLabeling(QgsVectorLayerSimpleLabeling(label_settings_cities))
layer_cities.setLabelsEnabled(True)
