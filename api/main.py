import osmnx as ox
import networkx as nx
ox.config(log_console=True, use_cache=True)
# define a point at the corner of California St and Mason St in SF
# location_point = (54.17911, 37.58745)
# gdf =ox.features_from_point(location_point, tags={'place': "suburb"}, dist=1000)
#
# print(gdf)
#fig, ax = ox.plot_footprints(gdf, figsize=(30, 30))
place = "Тула, Россия"
tags = {'admin_level': '9', "type": "relation"}
gdf = ox.features_from_place(place, tags)

index = gdf.index

for i in index:
    if i[0] == "relation":
        gdf_new = ox.geocode_to_gdf("R"+str(i[1]), by_osmid=True)
        #fig, ax = ox.plot_footprints(gdf_new, figsize=(3, 3))
        print(gdf_new["geometry"][0])
        with open(f"{i[1]}.txt", "w") as file:
            file.write(str(gdf_new["geometry"][0]))
#fig, ax = ox.plot_footprints(gdf, figsize=(30, 30))

"swimming_pool","stadium","fitness_centre","sports_hall","sports_centre","pitch","park","playground","picnic_table",
"nature_reserve","track","fitness_centre","fitness_station","stadium","outdoor_seating","golf_course","garden",
"common","sports_hall","dog_park","resort","horse_riding","fishing","water_park","beach_resort","dance","miniature_golf",
"ice_rink","bird_hide","swimming_area","bandstand","schoolyard","disc_golf_course","hackerspace","summer_camp","indoor_play",
"trampoline_park","bathing_place","wildlife_hide","barefoot","paddling_pool","village_swing","sunbathing","foot_bath",
"soccer_golf","wellness"




