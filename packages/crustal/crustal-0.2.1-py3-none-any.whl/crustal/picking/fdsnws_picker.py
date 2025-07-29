"""Module fdsnws_picker

This module provides a class for picking waveforms from FDSNWS
"""

#import threading
from multiprocessing import Pool
from itertools import product
import logging
import json
import os.path
from os import mkdir
from obspy import UTCDateTime
from obspy.core.stream import Stream
from obspy.clients.fdsn import Client
from obspy.clients.fdsn.client import FDSNException
import seisbench.models as sbm
import pandas as pd
from crustal.conf2str import Conf2Str


class FDSNWSPicker:


    configuration = {"channel_priority":["HH"],
                    "waveform_sources":[{"url":"EIDA"}],
                    "start_time":[2023,1,1,0,0,0],
                    "end_time":[2023,1,2,0,0,0],
                    "wf_chunk_s":86400,
                    "overlap_s":60,
                    "processors":[{"picker":"EQTransformer",
                                   "pretrained":"instance",
                                   "batch_size":256,
                                   "P_threshold":0.2,
                                   "S_threshold":0.1,
                                   "detections":True
                                   }]
                    }

    station_codes = []

    _conf_file = "./picking_conf.json"

#    _log_file = "./FDSNWS_picker.log"

    #TODO include this in the configuration
    _picks_dir = "./picks"

#    _logger = None

    _fdsnws_clients = []

    _processors = {}

    _station_df = []

    def _setup_logger(self):
        self._logger = logging.getLogger("FDSNWS_log")
        self._logger.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(logging.Formatter("%(message)s"))
        file_handler = logging.FileHandler(filename=self._log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
                     logging.Formatter(
                         "%(asctime)s %(levelname)s %(message)s",
                         datefmt="%Y-%m-%d %H:%M:%S"))
        self._logger.addHandler(file_handler)
        self._logger.addHandler(stream_handler)
        return


    def _check_fdsnws_clients(self):
        for client_info in self.configuration["waveform_sources"]:
            client_url = client_info["url"]
            logging.info(f"Checking for FDSN web services "
                              + f"at {client_url}")
            try:
                client = Client(client_url)
            except FDSNException:
                logging.error(f"No FDSN web services "
                                   + f"found at {client_url}")
            else:
                self._fdsnws_clients.append(client)
                if (("user" in client_info) and
                    ("pwd" in client_info)):
                    logging.info(f"Setting credentials for {client_url}")
                    client.set_credentials(client_info["user"],
                                           client_info["pwd"])

        return


    def _init_processors(self):
        self._processors = {}
        for proc in self.configuration["processors"]:
            processor_parameters = {}
            if proc["picker"] == "EQTransformer":
                processor_parameters["picker"] = (
                sbm.EQTransformer.from_pretrained(proc["pretrained"]))
            elif proc["picker"] == "PhaseNet":
                processor_parameters["picker"] = (
                sbm.PhaseNet.from_pretrained(proc["pretrained"]))
            processor_parameters["batch_size"] = proc["batch_size"]
            processor_parameters["P_threshold"] = proc["P_threshold"]
            processor_parameters["S_threshold"] = proc["S_threshold"]
            processor_parameters["detections"] = proc["detections"]
            self._processors[proc["picker"]] = processor_parameters
        return


    def __init__(self,
                 conf_file="./picking_conf.json",
                 log_file="./FDSNWS_picker.log"):

        self._conf_file = conf_file
#        self._log_file = log_file
#        self._setup_logger()

        logging.info("Starting")
        logging.info(f"Trying to read configuration from file {conf_file}")
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
        logging.info("Current configuration:")
        logging.info(Conf2Str(self.configuration).get_conf_str())
        self._check_fdsnws_clients()
        self._init_processors()
        return

    def add_stations(self, stations="./station_codes.json"):
        if os.path.isfile(stations):
            try:
                with open(stations) as input_file:
                    station_list = json.load(input_file)
            except json.JSONDecodeError:
                logging.error(f"File {stations} does not contain "+
                                    "valid JSON. No stations were added "+
                                    "to the list.")
                return
        else:
            try:
                station_list = json.loads(stations)
            except json.JSONDecodeError:
                logging.error("Input is not valid JSON. "+
                                   "No stations were added to the list.")
                return
        self.station_codes.extend(station_list)
        return


    def _get_time_windows(self):
        starttime = UTCDateTime(*self.configuration["start_time"])
        endtime = UTCDateTime(*self.configuration["end_time"])
        dt = self.configuration["wf_chunk_s"]
        t0 = starttime
        t1 = min(endtime, t0 + dt)
        time_windows = [[t0, t1]]
        if t1 + 0.1 > endtime:
            return time_windows
        while True:
            t0 = t0 + dt
            t1 = t1 + dt
            time_windows.append([t0, min(t1, endtime)])
            if t1 + 0.1  > endtime:
                break
        return time_windows


    def _get_station_metadata(self, net, sta):
        """
        Get metadata for a station
        Parameters
        ----------
        net : str
            Network code
        sta : str
            Station code
        Returns
        -------
        metadata : dict or None
            Metadata for the station
        """
        metadata = {"clients":[],"channels":[]}
        inventory = None
        for client in self._fdsnws_clients:
            try:
                inventory = client.get_stations(network=net,
                                               station=sta,
                                               location="*",
                                               channel="*",
                                               starttime=UTCDateTime(
                                                 *self.configuration["start_time"]),
                                               endtime=UTCDateTime(
                                                 *self.configuration["end_time"]),
                                               level="channel")
            except FDSNException:
                logging.warning(f"Station {net}.{sta} not "
                                     +f"found on {client.base_url}")
                continue
            else:
                channels = [c.code[0:2] for c in inventory[0][0]]
                channels = list(set(channels))
                metadata["clients"].append(client)
                metadata["channels"].extend(channels)
        if not inventory:
            return metadata
        metadata["channels"] = list(set(metadata["channels"]))
#        self._station_df.append({
        location ={"id" : f"{net}.{sta}.",
                   "longitude" : inventory[0][0].longitude,
                   "latitude" : inventory[0][0].latitude,
                   "elevation(m)" : inventory[0][0].elevation}
        return metadata, location


    def _download_wf(self, net, sta, metadata, time_window) -> Stream:
        """
        Download waveforms for a station
        Parameters
        ----------
        net 
        sta 
        metadata 
        time_window 
        """
        channels = []
        for cha in self.configuration["channel_priority"]:
            if cha in metadata["channels"]:
                channels.append(cha)
        if not channels:
            logging.warning(f"No useful channels found"
                                 + f" for station {net}.{sta}")
            logging.warning(f"Channels found for {net}.{sta}:")
            logging.warning(",".join(metadata["channels"]))
            return(None)
        t0, t1 =  time_window
        stream = None
        t0 = t0 - self.configuration["overlap_s"]
        t1 = t1 + self.configuration["overlap_s"]
        logging.debug(f"Trying to get data for time window" +
                           f" {t0} - {t1}")
        for cha in channels:
            logging.debug(f"Trying to get {net}.{sta}.*.{cha}?")
            for client in metadata["clients"]:
                logging.debug(f"Trying client {client.base_url}")
                try:
                    stream = client.get_waveforms(net,
                             sta, "*", f"{cha}?", t0, t1)
                except FDSNException:
                    continue
                if stream:
                    break
            if stream:
                break
        return stream


    def _save_picks(self, picks, net, sta, cha, time_window):
        pick_df = []
        t0, t1 = time_window
        start_str = t0.strftime("%Y%m%d%H%M%S")
        end_str = t1.strftime("%Y%m%d%H%M%S")
        filename = f"{self._picks_dir}/{net}.{sta}.{start_str}-{end_str}.picks"
        for pick in picks:
            pick_df.append({
                    "id": pick.trace_id,
                    "timestamp": pick.peak_time.datetime,
                    "prob": pick.peak_value,
                    "type": pick.phase.lower(),
                    "channel": cha
                    })
        pick_df = pd.DataFrame(pick_df)
        if len(pick_df.index) == 0:
            return
        pick_df.sort_values("timestamp")
        if not os.path.isdir(self._picks_dir):
            os.mkdir(self._picks_dir)
        pick_df.to_csv(filename)
        return


    def _cleanup_stream(self, stream, t_window):
        clean_traces = []
        for trace in stream.traces:
            dt = trace.meta["endtime"] - trace.meta["starttime"]
            if dt > t_window:
                clean_traces.append(trace)
        stream.traces = clean_traces
        return stream

    def _save_detections(self):
        pass
        return


    def _save_waveforms(self, picks, net, sta, cha, stream, time_window):
        traces = []
        for pick in picks:
            t1 = UTCDateTime(pick.peak_time.datetime)
            t0 = t1 - 60.0
            t2 = t1 + 60.0
            traces.extend(stream.slice(starttime=t0, endtime=t2).traces)
        new_stream = Stream(traces)
        start_t, end_t = time_window
        start_str = start_t.strftime("%Y%m%d%H%M%S")
        end_str = end_t.strftime("%Y%m%d%H%M%S")
        filename = f"waveforms/{net}.{sta}.{start_str}-{end_str}.mseed"
        if not os.path.isdir("waveforms"):
            os.mkdir("waveforms")
        if new_stream:
            new_stream.write(filename)
        return


    def _process_station(self, all_args):

        station, time_window = all_args
        logging.info(f"Processing station {station}")

        try:
            net, sta = station.split(".")
        except ValueError:
            logging.error(f"'{station}' is not a valid station code")
            return 1
        metadata, location = self._get_station_metadata(net, sta)
        if not metadata["clients"]:
            logging.warning(f"'{station}' was not found on any client")
            return 1
#        for time_window in time_windows:

        stream = self._download_wf(net, sta, metadata, time_window)
        if stream:
            stream = self._cleanup_stream(stream, 60.0)
        if stream:
            logging.debug("Data were found")
            cha = stream[0].get_id().split(".")[-1][0:2]
            for proc in self._processors: 
                logging.debug(f"Processing with {proc}")
                classify_output = self._processors[proc]["picker"].classify(
                              stream,
                              batch_size=self._processors[proc]["batch_size"],
                              P_threshold=self._processors[proc]["P_threshold"],
                              S_threshold=self._processors[proc]["S_threshold"])
                picks = classify_output.picks
                self._save_picks(picks, net, sta, cha, time_window)
                station_df = pd.DataFrame(self._station_df)
                station_df.to_csv("stations.csv")
                self._save_waveforms(picks, net, sta, cha, stream, time_window)
        else:
            logging.debug("No data were found")

        return location


    def pick(self) -> None:
        """
        Main function
        """
        time_windows = self._get_time_windows()

        all_args = list(product(self.station_codes, time_windows))

#        print(list(product(self.station_codes, time_windows)))
        with Pool(3) as pool:
#            results = pool.imap_unordered(self._process_station, all_args)
            for result in pool.imap_unordered(self._process_station, all_args):
                if result["id"] not in [ x["id"] for x in self._station_df ]:
                    self._station_df.append(result)

#        time_windows = self._get_time_windows()
#        for station in self.station_codes:
#            if self._process_station(station, time_windows):
#                continue
        self._station_df = pd.DataFrame(self._station_df)
        self._station_df.to_csv("stations.csv")
        return



def main() -> None:
    pass

if __name__ == "__main__":
    main()





