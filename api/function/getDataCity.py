import osmnx as ox
import networkx as nx
import geopandas
import json
import re


def find_city(gdf, name_city):
    index_city = gdf.index
    # display(gdf)
    for idx, city in enumerate(gdf["name:ru"]):
        if name_city == city.lower():
            return ox.geocode_to_gdf(index_city[idx][0][0] + str(index_city[idx][1]), by_osmid=True)


def find_violations(gdf_bad, gdf_educational, point=False):
    violations = []
    gdf_bad = ox.project_gdf(gdf_bad, to_crs=3857)
    gdf_educational = ox.project_gdf(gdf_educational, to_crs=3857)
    for index, p in gdf_educational.iterrows():
        distance = p["geometry"].distance(gdf_bad["geometry"])
        index_distance = distance.index
        for idx, dist in enumerate(distance):
            if dist <= 100:
                # violations.append([index_distance[idx],dist])
                if point:
                    violations.append({"name": p["name"], "street": p["addr:street"]})
                else:
                    violations.append({"name": p["name"], "street": p["addr:street"], "bad": get_name(index_distance[idx])})
    return violations


def find_average_distance(gdf_bad, gdf_park):
    distance_array = []
    gdf_bad = ox.project_gdf(gdf_bad, to_crs=3857)
    gdf_park = ox.project_gdf(gdf_park, to_crs=3857)
    for p in gdf_park["geometry"]:
        distance = p.distance(gdf_bad["geometry"])
        index_distance = distance.index
        min = 10000000
        for idx, dist in enumerate(distance):
            if min > dist:
                min = dist
        distance_array.append([index_distance[idx], min])
        # distance.append([index_distance[idx],get_name(index_distance[idx]),dist])
    average_distance = 0
    count = 0
    for p in distance_array:
        count += 1
        average_distance += p[1]
    return average_distance / count


def find_transport_distance(gdf_transport, gdf_park):
    distance_array = []
    gdf_transport = ox.project_gdf(gdf_transport, to_crs=3857)
    gdf_park = ox.project_gdf(gdf_park, to_crs=3857)
    for index, p in gdf_park.iterrows():
        distance = p["geometry"].distance(gdf_transport["geometry"])
        #index_distance = distance.index
        min = 10000000
        for idx, dist in enumerate(distance):
            if min > dist:
                min = dist
        if min > 200:
            distance_array.append({"name": p["name"], "street": p["addr:street"]})
            # violations.append([index_distance[idx],get_name(index_distance[idx]),dist])
    return distance_array


def get_name(name):
    gdf_area_local = ox.geocode_to_gdf(name[0][0] + str(name[1]), by_osmid=True)
    return gdf_area_local["display_name"][0]


def get_data_city(name_city):
    place = name_city.lower()
    gdf_country = ox.features_from_address(place, {"place": ["city", "town"]})
    gdf_city = find_city(gdf_country, place)
    tags_city = {'admin_level': ['9']}
    try:
        gdf_city_region = ox.features_from_bbox(gdf_city["bbox_north"][0], gdf_city["bbox_south"][0],
                                                gdf_city["bbox_east"][0], gdf_city["bbox_west"][0], tags_city)
    except:
        gdf_city_region = ox.features_from_bbox(gdf_city["bbox_north"][0], gdf_city["bbox_south"][0],
                                                gdf_city["bbox_east"][0], gdf_city["bbox_west"][0],
                                                {"place": ["city", "town"]})
    index_city_region = gdf_city_region.index

    areas = []
    for i in index_city_region:
        if i[0] == "relation":
            gdf_area = ox.geocode_to_gdf("R" + str(i[1]), by_osmid=True)
            areas.append(gdf_area)

    tags_good = {
        'amenity': "marketplace",
        "building": "riding_hall",
        "highway": "cycleway",
        "leisure": ["swimming_pool", "stadium", "fitness_centre", "sports_hall", "sports_centre", "pitch", "park",
                    "playground", "picnic_table",
                    "nature_reserve", "track", "fitness_centre", "fitness_station", "stadium", "outdoor_seating",
                    "golf_course", "garden", "common",
                    "sports_hall", "dog_park", "resort", "horse_riding", "fishing", "water_park", "beach_resort",
                    "miniature_golf", "ice_rink",
                    "bird_hide", "swimming_area", "bandstand", "schoolyard", "disc_golf_course", "hackerspace",
                    "summer_camp", "indoor_play", "trampoline_park",
                    "bathing_place", "wildlife_hide", "barefoot", "paddling_pool", "village_swing", "sunbathing",
                    "foot_bath", "soccer_golf", "wellness"],
        "shop": ["greengrocer", "agrarian", "farm"]}
    tags_bad = {
        'amenity': ["bar", "fast_food", "biergarten", "pub"],
        "shop": ["cigarettes", "e-cigarette", "vape", "vape_shop", "tobacco", "wine", "brewing_supplies",
                 "beverages", "alcohol", "beer", "beverages", "pizza", "fast_food", "kiosk"],
        "cuisine": ["pizza", "burger", "shawarma"]}
    tags_park = {"leisure": ["park", "wildlife_hide", "dog_park"]}
    tags_cigarettes = {"shop": ["cigarettes", "e-cigarette", "vape", "vape_shop", "tobacco", "kiosk"]}
    tags_alcohol = {'amenity': ["bar", "biergarten", "pub"],
                    "shop": ["wine", "beverages", "alcohol", "beer", "brewing_supplies", "kiosk"]}
    tags_educational = {
        'amenity': ["school", "kindergarten", "university", "college", "music_school", "language_school",
                    "dancing_school", "trade_school"]}
    tags_transport = {'highway': "bus_stop", "public_transport": ["platform", "stop_position"]}
    result = dict()
    # areas
    rating_city = 0
    average_distance_city = 0
    positive_city = 0
    for area in areas:
        gdf_good = ox.features_from_polygon(area["geometry"][0], tags_good)
        gdf_park = ox.features_from_polygon(area["geometry"][0], tags_park)
        gdf_cigarettes = ox.features_from_polygon(area["geometry"][0], tags_cigarettes)
        gdf_alcohol = ox.features_from_polygon(area["geometry"][0], tags_alcohol)
        gdf_bad = ox.features_from_polygon(area["geometry"][0], tags_bad)
        gdf_educational = ox.features_from_polygon(area["geometry"][0], tags_educational)
        gdf_transport = ox.features_from_polygon(area["geometry"][0], tags_transport)
        violations = find_violations(gdf_bad, gdf_educational.copy(deep=True))
        average_distance_region = find_average_distance(gdf_bad, gdf_park)
        average_distance_city += average_distance_region
        distance_transport_region = find_transport_distance(gdf_transport, gdf_educational.copy(deep=True))
        result[area["display_name"][0]] = dict()
        result[area["display_name"][0]]["good"] = len(gdf_good)
        result[area["display_name"][0]]["park"] = len(gdf_park)
        result[area["display_name"][0]]["cigarettes"] = len(gdf_cigarettes)
        result[area["display_name"][0]]["alcohol"] = len(gdf_alcohol)
        result[area["display_name"][0]]["educational"] = len(gdf_educational)
        result[area["display_name"][0]]["bad"] = len(gdf_bad)
        result[area["display_name"][0]]["positive"] = len(gdf_good) * 0.5 - len(gdf_bad)
        result[area["display_name"][0]]["violations"] = {"len": len(violations), "data": violations}
        result[area["display_name"][0]]["transport"] = {"len": len(distance_transport_region),
                                                        "data": distance_transport_region}
        result[area["display_name"][0]]["geometry"] = geopandas.GeoSeries(area["geometry"][0]).to_json()
        result[area["display_name"][0]]["average_distance"] = average_distance_region
        result[area["display_name"][0]]["rating"] = 0
        if result[area["display_name"][0]]["positive"] > 0:
            positive_city += 1
            result[area["display_name"][0]]["rating"] += 60
        else:
            positive_city -= 1
        if result[area["display_name"][0]]["violations"]["len"] == 0:
            result[area["display_name"][0]]["rating"] += 40
    average_distance_city = average_distance_city / len(areas)
    if average_distance_city > 200:
        rating_city += 30
    if positive_city > 0:
        rating_city += 70
    for area in areas:
        result[area["display_name"][0]]["city"] = dict()
        result[area["display_name"][0]]["city"]["rating"] = rating_city
        result[area["display_name"][0]]["city"]["average_distance"] = average_distance_city
        result[area["display_name"][0]]["city"]["positive"] = positive_city
    return re.sub("NaN", "null", json.dumps(result, ensure_ascii=False))


def get_data_point(point, dist):
    tags_good = {
        'amenity': "marketplace",
        "building": "riding_hall",
        "highway": "cycleway",
        "leisure": ["swimming_pool", "stadium", "fitness_centre", "sports_hall", "sports_centre", "pitch", "park",
                    "playground", "picnic_table",
                    "nature_reserve", "track", "fitness_centre", "fitness_station", "stadium", "outdoor_seating",
                    "golf_course", "garden", "common",
                    "sports_hall", "dog_park", "resort", "horse_riding", "fishing", "water_park", "beach_resort",
                    "miniature_golf", "ice_rink",
                    "bird_hide", "swimming_area", "bandstand", "schoolyard", "disc_golf_course", "hackerspace",
                    "summer_camp", "indoor_play", "trampoline_park",
                    "bathing_place", "wildlife_hide", "barefoot", "paddling_pool", "village_swing", "sunbathing",
                    "foot_bath", "soccer_golf", "wellness"],
        "shop": ["greengrocer", "agrarian", "farm"]}
    tags_bad = {
        'amenity': ["bar", "fast_food", "biergarten", "pub"],
        "shop": ["cigarettes", "e-cigarette", "vape", "vape_shop", "tobacco", "wine", "brewing_supplies",
                 "beverages", "alcohol", "beer", "beverages", "pizza", "fast_food", "kiosk"],
        "cuisine": ["pizza", "burger", "shawarma"]}
    tags_park = {"leisure": ["park", "wildlife_hide", "dog_park"]}
    tags_cigarettes = {"shop": ["cigarettes", "e-cigarette", "vape", "vape_shop", "tobacco", "kiosk"]}
    tags_alcohol = {'amenity': ["bar", "biergarten", "pub"],
                    "shop": ["wine", "beverages", "alcohol", "beer", "brewing_supplies", "kiosk"]}
    tags_educational = {
        'amenity': ["school", "kindergarten", "university", "college", "music_school", "language_school",
                    "dancing_school", "trade_school"]}
    tags_transport = {'highway': "bus_stop", "public_transport": ["platform", "stop_position"]}
    result = dict()
    try:
        gdf_good = ox.features_from_point(point, tags_good, dist)
    except:
        gdf_good = []
    try:
        gdf_park = ox.features_from_point(point, tags_park, dist)
    except:
        gdf_park = []
    try:
        gdf_cigarettes = ox.features_from_point(point, tags_cigarettes, dist)
    except:
        gdf_cigarettes = []
    try:
        gdf_alcohol = ox.features_from_point(point, tags_alcohol, dist)
    except:
        gdf_alcohol = []
    try:
        gdf_bad = ox.features_from_point(point, tags_bad, dist)
    except:
        gdf_bad = []
    try:
        gdf_educational = ox.features_from_point(point, tags_educational, dist)
        try:
            gdf_transport = ox.features_from_point(point, tags_transport, dist)
            distance_transport_region = find_transport_distance(gdf_transport, gdf_educational.copy(deep=True))
        except:
            gdf_transport = []
        try:
            violations = find_violations(gdf_bad, gdf_educational.copy(deep=True))
        except:
            violations = []
    except:
        gdf_educational = []
        gdf_transport = []
    result["good"] = len(gdf_good)
    result["park"] = len(gdf_park)
    result["cigarettes"] = len(gdf_cigarettes)
    result["alcohol"] = len(gdf_alcohol)
    result["educational"] = len(gdf_educational)
    result["transport"] = len(gdf_transport)
    result["bad"] = len(gdf_bad)
    result["positive"] = len(gdf_good) * 0.5 - len(gdf_bad)
    result["violations"] = {"len": len(violations), "data": violations}
    result["transport"] = {"len": len(distance_transport_region),
                           "data": distance_transport_region}
    result["rating"] = 0
    if result["positive"] > 0:
        result["rating"] += 60
    if result["violations"]["len"] == 0:
        result["rating"] += 40
    return re.sub("NaN", "null", json.dumps(result, ensure_ascii=False))


def get_data_points(point, dist, resultAll, idx):
    print(f"Выполнение: {idx}")
    tags_good = {
        'amenity': "marketplace",
        "building": "riding_hall",
        "highway": "cycleway",
        "leisure": ["swimming_pool", "stadium", "fitness_centre", "sports_hall", "sports_centre", "pitch", "park",
                    "playground", "picnic_table",
                    "nature_reserve", "track", "fitness_centre", "fitness_station", "stadium", "outdoor_seating",
                    "golf_course", "garden", "common",
                    "sports_hall", "dog_park", "resort", "horse_riding", "fishing", "water_park", "beach_resort",
                    "miniature_golf", "ice_rink",
                    "bird_hide", "swimming_area", "bandstand", "schoolyard", "disc_golf_course", "hackerspace",
                    "summer_camp", "indoor_play", "trampoline_park",
                    "bathing_place", "wildlife_hide", "barefoot", "paddling_pool", "village_swing", "sunbathing",
                    "foot_bath", "soccer_golf", "wellness"],
        "shop": ["greengrocer", "agrarian", "farm"]}
    tags_bad = {
        'amenity': ["bar", "fast_food", "biergarten", "pub"],
        "shop": ["cigarettes", "e-cigarette", "vape", "vape_shop", "tobacco", "wine", "brewing_supplies",
                 "beverages", "alcohol", "beer", "beverages", "pizza", "fast_food", "kiosk"],
        "cuisine": ["pizza", "burger", "shawarma"]}
    tags_park = {"leisure": ["park", "wildlife_hide", "dog_park"]}
    tags_cigarettes = {"shop": ["cigarettes", "e-cigarette", "vape", "vape_shop", "tobacco", "kiosk"]}
    tags_alcohol = {'amenity': ["bar", "biergarten", "pub"],
                    "shop": ["wine", "beverages", "alcohol", "beer", "brewing_supplies", "kiosk"]}
    tags_educational = {
        'amenity': ["school", "kindergarten", "university", "college", "music_school", "language_school",
                    "dancing_school", "trade_school"]}
    tags_transport = {'highway': "bus_stop", "public_transport": ["platform", "stop_position"]}
    result = dict()
    try:
        gdf_good = ox.features_from_point(point, tags_good, dist)
    except:
        gdf_good = []
    try:
        gdf_park = ox.features_from_point(point, tags_park, dist)
    except:
        gdf_park = []
    try:
        gdf_cigarettes = ox.features_from_point(point, tags_cigarettes, dist)
    except:
        gdf_cigarettes = []
    try:
        gdf_alcohol = ox.features_from_point(point, tags_alcohol, dist)
    except:
        gdf_alcohol = []
    try:
        gdf_bad = ox.features_from_point(point, tags_bad, dist)
    except:
        gdf_bad = []
    try:
        gdf_educational = ox.features_from_point(point, tags_educational, dist)
        try:
            gdf_transport = ox.features_from_point(point, tags_transport, dist)
            distance_transport_region = find_transport_distance(gdf_transport, gdf_educational.copy(deep=True))
        except:
            gdf_transport = []
            distance_transport_region=[]
        try:
            violations = find_violations(gdf_bad, gdf_educational.copy(deep=True))
        except:
            violations = []
    except:
        gdf_educational = []
        gdf_transport = []
        distance_transport_region = []
        violations = []
    result["good"] = len(gdf_good)
    result["park"] = len(gdf_park)
    result["cigarettes"] = len(gdf_cigarettes)
    result["alcohol"] = len(gdf_alcohol)
    result["educational"] = len(gdf_educational)
    result["transport"] = len(gdf_transport)
    result["bad"] = len(gdf_bad)
    result["positive"] = len(gdf_good) * 0.5 - len(gdf_bad)
    result["violations"] = {"len": len(violations), "data": violations}
    result["transport"] = {"len": len(distance_transport_region),
                           "data": distance_transport_region}
    result["index"] = idx
    result["rating"] = 0
    if result["positive"] > 0:
        result["rating"] += 60
    if result["violations"]["len"] == 0:
        result["rating"] += 40
    resultAll[idx] = re.sub("NaN", "null", json.dumps(result, ensure_ascii=False))
    return True