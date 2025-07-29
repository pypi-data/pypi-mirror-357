import json
import logging
import os
import pandas as pd
from pyproj import CRS, Transformer
from crustal.conf2str import Conf2Str
from gamma.utils import association
from obspy.core.event import (Event, Origin, QuantityError,
                              Catalog, Pick, WaveformStreamID,
                              CreationInfo, Arrival, ResourceIdentifier)
from obspy import UTCDateTime
import glob

#TODO this class is doing too much work. It should just produce events

class GaMMaAssociator:
    """Class for associating picks using GaMMa

    Attributes
    ----------
    configuration : dict
        Configuration dictionary

    Methods
    --------
    associate()
        Associate all the picks

    write_events(format)
        Write all the events in files
    """

    configuration : dict = {
                    "project_name": "example",
                    "event_dir": "./events",
                    "picks_dir": "./picks",
                    "geodetic_crs":4326,
                    "grid_crs":2100,
                    "start_time":[2023,1,1,0,0,0],
                    "end_time":[2023,1,2,0,0,0],
                    "overlap_s":60,
                    "Gamma":{
                            "dims":["x(km)", "y(km)", "z(km)"],
                            "use_dbscan":True,
                            "use_amplitude":False,
                            "vel":{
                                  "p":6.0,
                                  "s":3.4},
                            "method":"BGMM",
                            "dbscan_eps":10,
                            "dbscan_min_samples":3,
                            "min_picks_per_eq":6,
                            "max_sigma11":1.0,
                            "max_sigma22":1.0,
                            "max_sigma12":1.0
                            },
                    "pick_uncertainty":{
                            "P":0.1,
                            "S":0.15
                            },
                    "minimum_probability":{
                            "P":0.0,
                            "S":0.0
                            }
                    }

    _region_conf_file : str = "./region_conf.json"

    _conf_file : str = "./association_conf.json"

    _gamma_configuration : dict = {}

    _default_association_region : dict = {"min_lat":37.0,
                                          "max_lat":43.0,
                                          "min_lon":20.0,
                                          "max_lon":27.0,
                                          "min_dep":0.0,
                                          "max_dep":200.0
                                          }

    _default_study_region : dict = {"min_lat":39.0,
                                    "max_lat":41.0,
                                    "min_lon":22.0,
                                    "max_lon":25.0
                                    }
    _transformer = None

    _inv_transformer = None

    _all_picks = None

    _all_stations = None

    _catalog = None

#    _event_file_extensions : dict = {
#        "SC3ML": "xml",
#        "NLLOC_OBS": "obs"
#    }

    def _configure_projections(self) -> None:
        """Configure projections"""
        geodetic_crs = CRS.from_epsg(self.configuration["geodetic_crs"])
        grid_crs = CRS.from_epsg(self.configuration["grid_crs"])
        self._transformer = Transformer.from_crs(geodetic_crs,grid_crs)
        self._inv_transformer = Transformer.from_crs(grid_crs,geodetic_crs)
        return


    def _configure_gamma(self):
        """Configure Gamma"""
        self._gamma_configuration = self.configuration["Gamma"]
        x=[]
        y=[]
        min_lat = self.configuration["association_region"]["min_lat"]
        max_lat = self.configuration["association_region"]["max_lat"]
        min_lon = self.configuration["association_region"]["min_lon"]
        max_lon = self.configuration["association_region"]["max_lon"]
        for lat in (min_lat, max_lat):
            for lon in (min_lon, max_lon):
                x0, y0 = self._transformer.transform(lat, lon)
                x.append(x0)
                y.append(y0)
        min_x = min(x) / 1000 # m to km
        max_x = max(x) / 1000
        min_y = min(y) / 1000
        max_y = max(y) / 1000
        self._gamma_configuration["x(km)"] = (min_x, max_x)
        self._gamma_configuration["y(km)"] = (min_y, max_y)
        self._gamma_configuration["z(km)"] = (
                self.configuration["association_region"]["min_dep"],
                self.configuration["association_region"]["max_dep"])
        if self._gamma_configuration["method"] == "BGMM":
            self._gamma_configuration["oversample_factor"] = 4
        if self._gamma_configuration["method"] == "GMM":
            self._gamma_configuration["oversample_factor"] = 1
        self._gamma_configuration["bfgs_bounds"] = (
            (self._gamma_configuration["x(km)"][0] - 1,
            self._gamma_configuration["x(km)"][1] + 1),
            (self._gamma_configuration["y(km)"][0] - 1,
            self._gamma_configuration["y(km)"][1] + 1),
            (0, self._gamma_configuration["z(km)"][1] + 1),
            (None, None))
        return


    def _get_picks(self, respect_filename_times = True):
        """Get all the picks"""
        picks_dir = self.configuration["picks_dir"]
        logging.info(f"Trying to get pick info from {picks_dir}")
        if not os.path.isdir(picks_dir):
            logging.error(f"Directory {picks_dir} not found.")
            return
        all_files_in_dir = glob.glob(f"{picks_dir}/*")

        if respect_filename_times:
            t0 = (UTCDateTime(*self.configuration["start_time"])
                 - self.configuration["overlap_s"])
            t1 = (UTCDateTime(*self.configuration["end_time"])
                 + self.configuration["overlap_s"])
            all_files = []

            for infile in all_files_in_dir:
                t_start = UTCDateTime(infile.split("/")[-1].split(".")[-2].split("-")[0])
                t_end = UTCDateTime(infile.split("/")[-1].split(".")[-2].split("-")[1])
                if not (t_end < t0 or t_start > t1):
                    all_files.append(infile)
        else:
            all_files = all_files_in_dir

        logging.info(f"{len(all_files)} files found")
        pick_dfs = []
        for infile in all_files:
            pick_df = pd.read_csv(infile, usecols=["id",
                                                   "timestamp",
                                                   "prob",
                                                   "type",
                                                   "channel"])

            pick_df = pick_df[ ((pick_df["type"] == "p")
                              & (pick_df["prob"] >= self.configuration["minimum_probability"]["P"]))
                              | ((pick_df["type"] == "s")
                              & (pick_df["prob"] >= self.configuration["minimum_probability"]["S"])) ]


            pick_dfs.append(pick_df)
        self._all_picks = pd.concat(pick_dfs, ignore_index=True)
        n_picks = len(self._all_picks.index)
        logging.info(f"{n_picks} picks found")
        return


    def _get_stations(self):
        """Get all the stations"""
        logging.info("Trying to get station info from stations.csv")
        self._all_stations = pd.read_csv("stations.csv", usecols=[
                                              "id",
                                              "longitude",
                                              "latitude",
                                              "elevation(m)"])
        n_stations = len(self._all_stations.index)
        logging.info(f"{n_stations} stations found")
        logging.debug(f"Transforming coordinates")
        self._all_stations["x(km)"] = self._all_stations.apply(
            lambda x: self._transformer.transform(x["latitude"],
            x["longitude"])[0] / 1e3, axis=1)
        self._all_stations["y(km)"] = self._all_stations.apply(
            lambda x: self._transformer.transform(x["latitude"],
            x["longitude"])[1] / 1e3, axis=1)
        self._all_stations["z(km)"] = - self._all_stations[
                                        "elevation(m)"] / 1e3
        return


    def __init__(self, 
                 conf_file="./association_conf.json"):
        """
        Parameters
        ----------
        conf_file : str
            Path to the configuration file
        """
        
        logging.info("Trying to read configuration from file " +
                     f"{conf_file}")
        try:
            with open(conf_file) as input_file:
                file_conf = json.load(input_file)
        except json.JSONDecodeError:
            logging.warning(f"File {conf_file} does not contain "+
                  "valid JSON data. Using default configuration:")
            logging.warning(self.configuration)
            file_conf = self.configuration 
        merged_conf = self.configuration | file_conf
        for key in merged_conf:
            if key not in file_conf:
                logging.warning(f"Using default value for " +
                                f"parameter {key}: {merged_conf[key]}")
        self.configuration = merged_conf
        if "association_region" not in self.configuration:
            logging.info("No region defined. Using global" +
                         " configuration file region_conf.json")
            self.configuration["association_region"] = (
                                             self._default_association_region)
            try:
                with open("region_conf.json") as input_file:
                    region_conf = json.load(input_file)
                self.configuration["association_region"] = (
                                            region_conf["association_region"])
            except:
                logging.warning("Failed to read region configuration file. " + 
                                "Using default")
        logging.info("Current configuration:")
        logging.info(Conf2Str(self.configuration).get_conf_str())
        self._configure_projections()
        self._configure_gamma()
        self._get_picks()
        self._get_stations()
        return

    # This method has to be split up to smaller ones

    def associate(self):
        """Associate all the picks"""

        gamma_cat, assignments = association(
                     self._all_picks[["id",
                                      "timestamp",
                                      "prob",
                                      "type"]],
                     self._all_stations,
                     self._gamma_configuration,
                     method = self._gamma_configuration["method"])
        assignments = pd.DataFrame(assignments,
                                   columns=["pick_index",
                                            "event_index",
                                            "gamma_score"])
        # save raw results
        gamma_cat_df = pd.DataFrame(gamma_cat)
        gamma_cat_df.to_csv("gamma_cat.csv")
        assignments.to_csv("assignments.csv")
        self._catalog = Catalog()

        study_region = self._default_study_region
        try:
            with open("region_conf.json") as input_file:
                region_conf = json.load(input_file)
            study_region = region_conf["study_region"]
        except:
            logging.warning("Failed to read region configuration file. " + 
                            "Using default")

        event_dir = self.configuration["event_dir"]
        project = self.configuration["project_name"]
        if not os.path.isdir(event_dir):
            logging.info(f"Creating directory {event_dir}")
            os.mkdir(event_dir)
            event_id : int = 0
        if not os.path.isfile(event_dir+"/last_event_id.txt"):
            event_id : int = 0
            with open(event_dir+"/last_event_id.txt", "w") as output_file:
                output_file.write(str(event_id))
        else:
            with open(event_dir+"/last_event_id.txt") as input_file:
                event_id = int(input_file.read())

        for record in gamma_cat:
            x = record["x(km)"]
            y = record["y(km)"]
            z = record["z(km)"]
            lat, lon  = self._transformer.transform(x*1000, y*1000,
                                                    direction = "INVERSE")
            dep = 1000 * z
            t = record["time"]

            if lat < study_region["min_lat"] or lat > study_region["max_lat"]:
                continue
            if lon < study_region["min_lon"] or lon > study_region["max_lon"]:
                continue
            if UTCDateTime(t) < UTCDateTime(*self.configuration["start_time"]):
                continue
            if UTCDateTime(t) > UTCDateTime(*self.configuration["end_time"]):
                continue

            event_id += 1
            sigma_t = record["sigma_time"]
            idx = record["event_index"]
            origin = Origin()
            origin.time = UTCDateTime(t)
            origin.time_errors = QuantityError(uncertainty=sigma_t)
            origin.longitude = lon
            origin.latitude = lat
            origin.depth = dep
            origin.evaluation_mode = "automatic"
            origin.creation_info = CreationInfo(author="GaMMA",
                                               creation_time=UTCDateTime())
            event = Event(
                    resource_id=ResourceIdentifier(
                         id=f"{project}{event_id:010}"),
                         origins=[origin])
            event.preferred_origin_id = origin.resource_id
            event.creation_info = CreationInfo(author="GaMMA",
                                               creation_time=UTCDateTime())
            picks_assoc = assignments.loc[
                          assignments["event_index"]==idx]
            pick_indices = picks_assoc["pick_index"].tolist()
            for pick_index in pick_indices:
                i_row = self._all_picks.index.get_loc(pick_index)
                pick_row = self._all_picks.loc[i_row].to_dict()
                pick = Pick()
                pick.time = UTCDateTime(pick_row["timestamp"])
                pick.phase_hint = pick_row["type"].upper()
                if pick.phase_hint in self.configuration["pick_uncertainty"]:
                    sigma = self.configuration["pick_uncertainty"][
                            pick.phase_hint]
                    pick.time_errors = QuantityError(uncertainty=sigma)
                pick.waveform_id = WaveformStreamID(
                               network_code=pick_row["id"].split(".")[0],
                               station_code = pick_row["id"].split(".")[1],
                               channel_code = pick_row["channel"]+"Z")
                pick.evaluation_mode = "automatic"
                pick.creation_info = CreationInfo(author="SeisBench",
                                               creation_time=UTCDateTime())
                arrival = Arrival()
                arrival.pick_id = pick.resource_id
                arrival.phase = pick.phase_hint
                arrival.time_weight = 1.0
                arrival.creation_info = CreationInfo(author="SeisBench",
                                               creation_time=UTCDateTime())
                origin.arrivals.append(arrival)
                event.picks.append(pick)

            self._catalog.append(event)

        #TODO don't forget the last_event_id thing
        for event in self._catalog:
             filename = f"{event_dir}/{event.resource_id.id}.xml"
             event.write(filename, format="SC3ML")

        with open("catalog.dat", "w") as output_file:
            for event in self._catalog:
                origin = event.preferred_origin()
                output_file.write(f"{origin.time} {origin.longitude} " +
                               f"{origin.latitude} {origin.depth / 1000.0}\n")
        with open(event_dir+"/last_event_id.txt", "w") as output_file:
            output_file.write(str(event_id))
        return


# This has to go to a class that manipulates catalogs
#    def write_events(self, format):
#        """Write all the events in files
#
#        Parameters
#        ----------
#        format : string
#            Format of the output files. See obspy write method for more
#            information.
#        """
#        
#        event_dir = self.configuration["event_dir"]
#        project = self.configuration["project_name"]
#        ext = self._event_file_extensions[format]
#
#        if not os.path.isdir(event_dir):
#            logging.info(f"Creating directory {event_dir}")
#            os.mkdir(event_dir)
#            event_id : int = 0
#        if not os.path.isfile(event_dir+"/last_event_id.txt"):
#            event_id = 0
#            with open(event_dir+"/last_event_id.txt", "w") as output_file:
#                output_file.write(str(event_id))
#        else:
#            with open(event_dir+"/last_event_id.txt") as input_file:
#                event_id = int(input_file.read())
#        print(self._catalog.__str__(print_all=True))
#        for event in self._catalog:
#             event_id += 1
#             filename = f"{event_dir}/{project}{event_id:010}.{ext}"
#             event.write(filename, format=format)
#        with open(event_dir+"/last_event_id.txt", "w") as output_file:
#            output_file.write(str(event_id))
#        return



