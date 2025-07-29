import logging
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from glob import glob
from obspy import read
from obspy import UTCDateTime
from obspy.core.event import read_events
from obspy.core.stream import Stream
from obspy.geodetics import locations2degrees
from obspy.clients.fdsn import Client


class PlainSeismogram:

    _project_configuration : dict = {
        "project_name": "example",
        }

    _seismogram_configuration : dict = {
        "wf_sources" : [
                {
                "type": "fdsnws",
                "url" : "NOA"
                }
            ]
        }

    _file_extensions : dict = {
        "SC3ML" : "xml",
        "CSV" : "csv",
        "NLLOC": "obs",
        }

    _station_df : pd.DataFrame = pd.DataFrame() 


    def _get_station_data(self):
        self._station_df = pd.read_csv("stations.csv", usecols=[
                                          "id",
                                          "longitude",
                                          "latitude",
                                          "elevation(m)"])
        return

    def __init__(self,
                 eventid,
                 max_sta = 10,
                 conf_file="./seismogram_conf.json"):

        logging.info("Trying to read project configuration from file " +
                     f"project_conf.json")
        try:
            with open("project_conf.json") as input_file:
                file_conf = json.load(input_file)
        except json.JSONDecodeError:
            logging.warning(f"File project_conf.json does not contain "+
                      "valid JSON data. Using default configuration:")
            logging.warning(self._project_configuration)
            file_conf = self._project_configuration
        merged_conf = self._project_configuration | file_conf
        for key in merged_conf:
            if key not in file_conf:
                logging.warning(f"Using default value for " +
                                f"parameter {key}: {merged_conf[key]}")
        self._project_configuration = merged_conf


        logging.info("Trying to read seismogram configuration from file " +
                     f"{conf_file}")
        try:
            with open(conf_file) as input_file:
                file_conf = json.load(input_file)
        except json.JSONDecodeError:
            logging.warning(f"File {conf_file} does not contain "+
                      "valid JSON data. Using default configuration:")
            logging.warning(self._seismogram_configuration)
            file_conf = self._seismogram_configuration
        merged_conf = self._seismogram_configuration | file_conf
        for key in merged_conf:
            if key not in file_conf:
                logging.warning(f"Using default value for " +
                                f"parameter {key}: {merged_conf[key]}")
        self._seismogram_configuration = merged_conf

        self._get_station_data()

        self.plain(eventid, max_sta)
        return None


    def _get_event_from_file(self, event_source, event_id):
        event = None
        ext = self._file_extensions[event_source["format"]]
        path = f"{event_source['path']}/{event_id}.{ext}"
        try:
            event = read_events(path)[0]
        except:
            logging.warning(f"Event {event_id} not found")
        return event


    def _get_event(self, event_id):

        event = None
        for event_source in self._seismogram_configuration["event_sources"]:
            if event_source["type"] == "file":
                event = self._get_event_from_file(event_source, event_id)
                if event is not None:
                    break
        # TODO add more sources such as FDSN
        return event

    def _get_stations_by_distance(self, picks, max_sta, lat, lon):
        stations=[]
        distances = None
        for pick in picks:
            stations.append(f"{pick.waveform_id.network_code}."
                           +f"{pick.waveform_id.station_code}.")
        stations = pd.DataFrame(list(set(stations)), columns=["id"])
        stations["lat"] = stations.apply(lambda x: self._station_df[
            self._station_df["id"] == x.iloc[0]].latitude.item(), axis=1)
        stations["lon"] = stations.apply(lambda x: self._station_df[
            self._station_df["id"] == x.iloc[0]].longitude.item(), axis=1)
        stations["dist"] = stations.apply(lambda x: locations2degrees(
            lat, lon, x["lat"], x["lon"]), axis=1)
        stations = stations.sort_values(by="dist")
        stations = stations[0:max_sta]["id"].tolist()
        return stations


    def _get_stream_fdsnws(self, wf_source, net, sta, cha,
                           starttime, endtime):
        stream = None
        try:
            logging.info(f"Trying to get {net}.{sta}.{cha} from " +
                          f"{wf_source['url']}")
            wf_client = Client(wf_source["url"])
            stream = wf_client.get_waveforms(net, sta, "*", cha,
                                             starttime=starttime,
                                             endtime=endtime)
            print(stream)
        except:
            logging.warning(f"Waveform {net}.{sta}.{cha} not found"+
                            f" on {wf_source['url']}")
            return None
        return stream

     
    def _get_stream_seed_dir(self, wf_source, net, sta, cha,
                              starttime, endtime):
        stream = None
        try:
            logging.info(f"Trying to get {net}.{sta}.{cha} from " +
                          f"{wf_source['path']}")
            filenames = glob(f"{wf_source['path']}/{net}.{sta}.*.mseed")
            for fn in filenames:
                t0 = UTCDateTime(fn.split("/")[-1].split(".")[2].split("-")[0])
                t1 = UTCDateTime(fn.split("/")[-1].split(".")[2].split("-")[1])
                if starttime >= t0 and starttime <= t1:
                    filename = fn
                    break
            stream = read(filename,
                          starttime=starttime,
                          endtime=endtime,
                          format="mseed")
        except Exception as message:
            logging.warning(f"Waveform {net}.{sta}.{cha} not found"+
                            f" in {wf_source['path']}")
            logging.warning(message)
            return None
        return stream


    def _get_waveforms(self, event, max_sta):
        waveforms = []
        origin = event.preferred_origin()
        lat = origin.latitude
        lon = origin.longitude
        stations = self._get_stations_by_distance(event.picks,
                                                  max_sta,
                                                  lat,
                                                  lon)
        pick_times = []
        for station in stations:
            waveform = {}
            net = station.split(".")[0]
            sta = station.split(".")[1]
            waveform["net"] = net
            waveform["sta"] = sta
            cha = None
            for pick in event.picks:
                if (pick.waveform_id.station_code == sta and
                  pick.waveform_id.network_code == net):
                    cha = pick.waveform_id.channel_code
                    waveform["cha"] = cha
                    if pick.phase_hint == "P":
                        waveform["P"] = pick.time
                        pick_times.append(pick.time)
                    elif pick.phase_hint == "S":
                        waveform["S"] = pick.time
                        pick_times.append(pick.time)
            waveforms.append(waveform)
        starttime = min(pick_times)-10.0
        endtime = max(pick_times)+30.0
        for waveform in waveforms:
            stream = None
            for wf_source in (
              self._seismogram_configuration["wf_sources"]):
                if (wf_source["type"] == "fdsnws"):
                    stream = self._get_stream_fdsnws(wf_source,
                                                  waveform["net"],
                                                  waveform["sta"],
                                                  waveform["cha"],
                                                  starttime,
                                                  endtime)
                    if stream:
                        break
                if (wf_source["type"] == "seed_dir"):
                    stream = self._get_stream_seed_dir(wf_source,
                                                  waveform["net"],
                                                  waveform["sta"],
                                                  waveform["cha"],
                                                  starttime,
                                                  endtime)
                    if stream:
                        break
                #TODO add more source types
            if stream is None:
                stream = Stream()
            waveform["stream"] = stream
        return waveforms

    def _wf_figure(self, event, waveforms):

        event_id = event.resource_id.id.split("/")[-1]
        fig, axs = plt.subplots(len(waveforms), 1,
                                sharex=True, figsize=(16,9))
        fig.subplots_adjust(hspace=0)
        fig.suptitle(f"Event {event_id}")
        for i, waveform in enumerate(waveforms):
            stream = waveform["stream"]
            stream.taper(max_percentage=0.05)
            stream.filter("bandpass", freqmin=1.0, freqmax=10.0)
            stream.merge(method=1)
            trace = stream[0]
            axs[i].plot(trace.times("matplotlib"), trace.data, "k")
            if "P" in waveform:
                axs[i].vlines(waveform["P"].matplotlib_date,
                              axs[i].get_ylim()[0],
                              axs[i].get_ylim()[1],
                              colors="r")
            if "S" in waveform:
                axs[i].vlines(waveform["S"].matplotlib_date,
                              axs[i].get_ylim()[0],
                              axs[i].get_ylim()[1],
                              colors="b")
            axs[i].set_yticklabels([])
            axs[i].get_yaxis().set_ticks([])
            axs[i].text(0.01, 0.99, f"{trace.id}",
                        horizontalalignment="left",
                        verticalalignment="top",
                        transform=axs[i].transAxes)
        axs[i].xaxis_date()
        axs[i].xaxis.set_major_locator(mdates.AutoDateLocator())
        axs[i].xaxis.set_minor_locator(mdates.SecondLocator(interval=1))
        axs[i].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))

        plt.show()

        return fig, axs


    def plain(self, event_id, max_sta = 10):
        """Make a plain seismogram"""
        event = self._get_event(event_id)
        waveforms = self._get_waveforms(event, max_sta)

        fig, axs = self._wf_figure(event, waveforms)

        return None


#   def plain_tk(self, event_id, max_sta = 10):
#        """Make a tkinter seismogram"""
#        event = self._get_event(event_id)
#        waveforms = self._get_waveforms(event, max_sta)
#
#        fig, axs = self._wf_figure(event, waveforms)
#
#        
#        return None



