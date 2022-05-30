from modules.config_utils import get_config, overwrite_config
result_cfg = {}

def add_vehicle(vehicle_dict: dict, vehicle: dict) -> dict:
    if vehicle["respawnTime"] == 0:
        return vehicle_dict
    vehicle_number = 1
    vehicle_name = vehicle["type"]
    while True:
        if vehicle_name in vehicle_dict:
            vehicle_name = f"{vehicle['type']} ({vehicle_number})"
            vehicle_number += 1
        else:
            vehicle_dict[vehicle_name] = vehicle["respawnTime"] * 60
            return vehicle_dict

cfg: dict = get_config("finished.json")
maps = cfg["Maps"]

for map in maps:
    try:
        bluefor_vehicles = map["team1"]["vehicles"]
        opfor_vehicles = map["team2"]["vehicles"]
    except KeyError:
        continue
    map_name = map["levelName"]
    map_name = map_name.replace("Lashkar_Valley_", "LashkarValley_")
    map_name = map_name.replace("Tallil_Outskirts_", "Tallil_")
    map_name = map_name.replace("Goose_Bay_", "GooseBay_")
    bluefor = map["team1"]
    faction_bluefor = bluefor["faction"]
    opfor = map["team2"]
    faction_opfor = opfor["faction"]
    vehicles_bluefor = {}
    vehicles_opfor = {}
    bluefor_dict = {}
    opfor_dict = {}
    return_dict = {}
    for vehicle in bluefor_vehicles:
        vehicles_bluefor = add_vehicle(vehicles_bluefor, vehicle)
    
    for vehicle in opfor_vehicles:
        vehicles_opfor = add_vehicle(vehicles_opfor, vehicle)

    bluefor_dict["faction"] = faction_bluefor
    bluefor_dict["vehicles"] = vehicles_bluefor
    opfor_dict["faction"] = faction_opfor
    opfor_dict["vehicles"] = vehicles_opfor
    return_dict["BLUEFOR"] = bluefor_dict
    return_dict["OPFOR"] = opfor_dict
    result_cfg[map_name] = return_dict

overwrite_config("./modules/layers.json", result_cfg)