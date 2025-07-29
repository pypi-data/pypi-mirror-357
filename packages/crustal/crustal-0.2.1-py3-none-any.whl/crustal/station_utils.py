import logging
import json
import pandas as pd
from obspy import read_inventory
from obspy.clients.fdsn import Client
from obspy.clients.fdsn.client import FDSNException


def json_to_csv(input_filename, output_filename):

    with open("project_conf.json") as conf_file:
        project_conf = json.load(conf_file)

    with open(input_filename) as input_file:
        station_list = json.load(input_file)

    # TODO this kind of code seems to be duplicated elsewhere
    fdsnws_clients = []
    for client_info in project_conf["metadata_sources"]:
        client_url = client_info["url"]
        try:
            client = Client(client_url)
        except FDSNException:
            logging.error(f"No FDSN web services "
                             + f"found at {client_url}")
        else:
            if (("user" in client_info) and
                ("pwd" in client_info)):
                logging.info(f"Setting credentials for {client_url}")
                client.set_credentials(client_info["user"],
                                          client_info["pwd"])
            fdsnws_clients.append(client)
            break

    station_df = []

    for station in station_list:
        net = station.split(".")[0]
        sta = station.split(".")[1]
        for client in fdsnws_clients:
            try:
                inventory = client.get_stations(network=net,
                                               station=sta,
                                               location="*",
                                               channel="*",
                                               level="station")
            except FDSNException:
                logging.warning(f"Station {net}.{sta} not "
                                     +f"found on {client.base_url}")
                continue
            else:
                #TODO fix for nonempty location code
                station_df.append({"id" : f"{net}.{sta}.",                                     
                "longitude" : inventory[0][0].longitude,                    
                "latitude" : inventory[0][0].latitude,                      
                "elevation(m)" : inventory[0][0].elevation}                    
                )

    station_df = pd.DataFrame(station_df)
    station_df.to_csv(output_filename)

    return


def xml_to_csv(input_filename, output_filename):

    inv = read_inventory(input_filename)

    station_df = []
    for net in inv:
        for sta in net:
            station_df.append({"id" : f"{net.code}.{sta.code}.",                                     
            "longitude" : sta.longitude,                    
            "latitude" : sta.latitude,                      
            "elevation(m)" : sta.elevation}                    
            )

    station_df = pd.DataFrame(station_df)
    station_df.to_csv(output_filename)

    return

def fdsn_to_json(conf_file=None, json_file=None):
    logging.info("Downloading station list from FDSN web services")
    if conf_file is None:
        conf_file = "project_conf.json"
    with open(conf_file) as conf_f:
        project_conf = json.load(conf_f)
    logging.info(f"Reading configuration from: {conf_file}")

    stations = []
    for client_info in project_conf["metadata_sources"]:
        client_url = client_info["url"]
        logging.info(f"Checking for FDSN web services "
                          + f"at {client_url}")
        try:
            client = Client(client_url)
            inventory = client.get_stations(
                   network="*",
                   station="*",
                   location="*",
                   channel="*",
                   level="station",
                   minlatitude=project_conf["station_region"]["min_lat"],
                   maxlatitude=project_conf["station_region"]["max_lat"],
                   minlongitude=project_conf["station_region"]["min_lon"],
                   maxlongitude=project_conf["station_region"]["max_lon"])

            for net in inventory:
                for sta in net:
                    stations.append(f"{net.code}.{sta.code}")

        except FDSNException:
            logging.error(f"No FDSN web services "
                             + f"found at {client_url}")

    stations=list(set(stations))

    if json_file is None:
        json_file = "station_codes.json"
    with open(json_file, "w") as output_file:
        logging.info(f"Writing station codes to {json_file}")
        json.dump(stations, output_file)

    return



