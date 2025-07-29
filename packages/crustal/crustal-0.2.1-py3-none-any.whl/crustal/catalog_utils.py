from obspy import read_events
from glob import glob
import os


def _to_text1(event):
# 2023 01 03 10 24 41 39.0369 23.1708 12 0.0
    origin = event.preferred_origin()
    timestr = origin.time.strftime("%Y %m %d %H %M %S")
    lat = origin.latitude
    lon = origin.longitude
    depth = origin.depth / 1e3 # m to km
    mag = 0.0
    if event.preferred_magnitude():
        mag = event.preferred_magnitude().mag
    return f"{timestr} {lat:.4f} {lon:.4f} {depth:.0f} {mag:.1f}\n"


def dir_to_file(path="./events", filename="events.txt", format="TEXT1"):
    """
    Read all the events in a directory and write them in a file
    The events in the directory are in individual xml files

    Parameters
    ----------
    path : str
            Path to the directory
    filename : str
            Name of the output file
    format : str
            Format of the output file
    """
    
    all_files = glob(f"{path}/*.xml")
    with open(f"{filename}", "w") as output_file:
        for infile in all_files:
            event = read_events(infile)[0]
            match format:
                case "TEXT1":
                    output = _to_text1(event)
                case _:
                    raise ValueError(f"Format {format} not supported")
                
            output_file.write(output) 
           

    return


def one_to_many(filename="events.xml",
                path="./events",
                format="QUAKEML",
                P_and_S_only=True):

    """
    Read all the events from a single file and write them in
    separate files in a directory.
    The events in the directory are individual xml files

    Parameters
    ----------
    filename : str
            Name of the input file
    path : str
            Path to the directory
    format : str
            Format of all the files
    P_and_S_only : bool
            Convert all P phases ("Pn", "Pg", "PN" etc) to "P"
            and all S phases ("Sg", "Sn", "SG" etc) to "S"
    """

    catalog = read_events(filename)
    if not os.path.isdir(path):
        os.mkdir(path)

    for event in catalog:
        if P_and_S_only:
            for pick in event.picks:
                if not pick.phase_hint:
                    continue
                pick.phase_hint = pick.phase_hint[:1].upper()
            for origin in event.origins:
                for arrival in origin.arrivals:
                    arrival.phase = arrival.phase[:1].upper()
        match format:
            case "QUAKEML":
                event.write(f"{path}/{event.resource_id.id.split('/')[-1]}.xml", format="QUAKEML")
            case "SC3ML":
                event.write(f"{path}/{event.resource_id.id.split('/')[-1]}.xml", format="SC3ML")
            case _:
                raise ValueError(f"Format {format} not supported")

    return


def dir_to_ids(path="./events"):

    all_files = glob(f"{path}/*.xml")
    ids = []
    for infile in all_files:
        event = read_events(infile)[0]
        ids.append(event.resource_id.id.split("/")[-1])
    return ids

