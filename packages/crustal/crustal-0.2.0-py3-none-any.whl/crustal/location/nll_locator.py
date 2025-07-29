import subprocess
import glob
import math
import pandas as pd
from obspy import read_events
from obspy import UTCDateTime

class NLLlocator:

    configuration = ( 
"""TRANS GLOBAL
LOCSIG Aristotle University of Thessaloniki
LOCCOM Regional 1D model for Greece
LOCPHASEID P Pg Pn
LOCPHASEID S Sg Sn
LOCQUAL2ERR 0.2 0.5 1.0 2.0 99999.9
LOCPHSTAT 9999.0 -1 9999.0 1.0 1.0
LOCANGLES ANGLES_NO 5
CONTROL 15 54321
LOCELEVCORR 1 5.0 2.81
LOCGAU 0.5 0.0
LOCGAU2 0.02 0.05 2.0
LOCGRID 121 101 301 18.0 33.0 0.0 0.1 0.1 1.0 PROB_DENSITY SAVE
LOCMETH EDT_OT_WT_ML 1.0e6 4 500 -1 -1.7 6 -1.0 1
LOCSEARCH OCT 96 48 6 0.05 50000 10000 4 0
"""
    )

#    configuration = {
#        "TRANS":"GLOBAL",
#        "LOCSIG":"Aristotle University of Thessaloniki",
#        "LOCCOM":"Regional 1D model for Greece",
#        "LOCPHASEID":"P Pg Pn",
#        "LOCPHASEID":"S Sg Sn",
#        "LOCQUAL2ERR":"0.2 0.5 1.0 2.0 99999.9",
#        "LOCPHSTAT":"9999.0 -1 9999.0 1.0 1.0",
#        "LOCANGLES":"ANGLES_NO 5",
#        "CONTROL":"15 54321",
#        "LOCELEVCORR":"1 5.0 2.81",
#        "LOCGAU":"0.5 0.0",
#        "LOCGAU2":"0.02 0.05 2.0",
#        "LOCGRID":"121 101 301 18.0 33.0 0.0 0.1 0.1 1.0 PROB_DENSITY SAVE",
#        "LOCMETH":"EDT_OT_WT_ML 1.0e6 4 500 -1 -1.7 6 -1.0 1",
#        "LOCSEARCH":"OCT 96 48 6 0.05 50000 10000 4 0"
#    }

    df_stations = []


    def __init__(self):
        pass


    def _read_stations(self, filename):
        df = pd.read_csv(filename)
        self.df_stations = df
        return df


    def _read_event(self, filename):
        event = read_events(filename, format="SC3ML")[0]
        return event


    def _build_input(self, basename, filename):
        event = self._read_event(filename)
        self._build_conf(basename, event)
        self._build_obs(basename, event)
        return filename

    def _build_conf(self, basename, event):
        self._read_stations("stations.csv")
        filename = f"{basename}.conf"
        with open(filename, "w") as f:
#            for k, v in self.configuration.items():
#                f.write(f"{k} {v}\n")
            f.write(self.configuration)
            for pick in event.picks:
                net = pick.waveform_id.network_code
                sta = pick.waveform_id.station_code
                match = self.df_stations[self.df_stations["id"]
                                         == f"{net}.{sta}."]
                if len(match) == 0:
                    continue
                lat = match.latitude.item()
                lon = match.longitude.item()
                alt = match["elevation(m)"].item()
                f.write(f"LOCSRCE {net}_{sta} "+
                        f"LATLON {lat} {lon} 0 {alt/1000.0}\n")
            #TODO do not hardcode the location of the "time" directory
#            f.write(f"LOCFILES {basename}.obs NLLOC_OBS /home/odysseus/Projects/Corfu_2024/NLL/time/greece_4_layers {basename} 1\n")
#            f.write(f"LOCFILES {basename}.obs NLLOC_OBS /home/odysseus/Projects/Lesbos_2025/processing/NLL/time/Papazachos_1998 {basename} 1\n")
#            f.write(f"LOCFILES {basename}.obs NLLOC_OBS /home/odysseus/Projects/Lesbos_2025/processing/NLL/time/Panagiotopoulos_1984 {basename} 1\n")
            f.write(f"LOCFILES {basename}.obs NLLOC_OBS /home/odysseus/Projects/Lesbos_2025/processing/NLL/time/Panagiotopoulos_1984_smooth {basename} 1\n")
            f.write("TRANS GLOBAL\n")
            f.write("LOCHYPOUT SAVE_NLLOC_ALL\n")


        return filename

    def _build_obs(self, basename, event):
        filename = f"{basename}.obs"
        with open(filename, "w") as f:
            for pick in event.picks:
                net = pick.waveform_id.network_code
                sta = pick.waveform_id.station_code
                phase_hint = pick.phase_hint
                t_str = pick.time.strftime("%Y%m%d %H%M %S.%f")
                f.write(f"{net}_{sta} ? Z ? {phase_hint} ? {t_str} GAU 1.00e-01 -1.00e+00 -1.00e+00 -1.00e+00 1.00e+00\n")
        return


    def locate_event(self, basename, input_dir, output_dir):

        filename = self._build_input(f"{output_dir}/{basename}", f"{input_dir}/{basename}.xml")
        event = self._read_event(filename)
        outp = subprocess.check_output(["NLLoc",f"{output_dir}/{basename}.conf"])

        return

    def locate_dir(self, input_dir, output_dir):

        for filename in glob.glob(f"{input_dir}/*.xml"):
            basename = filename.split(".")[-2].split("/")[-1]
            print(basename)
            self.locate_event(basename, input_dir, output_dir)

        return


    def dir_to_cat(self, input_dir, min_lat, max_lat, min_lon, max_lon,
                   with_id=False, with_errors=False):
        files = glob.glob(f"{input_dir}/*.sum.grid0.loc.hyp")  
        for file in files:
            with open(file) as input_file:
                for line in input_file:
                    if line.startswith("GEOGRAPHIC"):
                        _, _, yr, mo, dy, hr, mi, sec, _, lat, _, lon, _, dep = line.split()
                        yr = int(yr)
                        mo = int(mo)
                        dy = int(dy)
                        hr = int(hr)
                        mi = int(mi)
                        sec = float(sec)
                        lat = float(lat)
                        lon = float(lon)
                        dep = float(dep)
                        ot = UTCDateTime(yr, mo, dy, hr, mi) + sec
                        yr = ot.year
                        mo = ot.month
                        dy = ot.day
                        hr = ot.hour
                        mi = ot.minute
                        sec = ot.second + ot.microsecond / 1e6

                        evid = file.split("/")[-1].split(".")[0]

                        output_line = f"{yr:04d} {mo:02d} {dy:02d} {hr:02d} {mi:02d} {sec:09.6f} {lat} {lon} {dep} 0.0"
                        if with_id:
                            output_line += f" {evid}"

                    if line.startswith("QML_ConfidenceEllipsoid"): 
                        _, _, sigma_x_max, _, sigma_x_min, _, sigma_x_int, _, _, _, _, _, _ = line.split()
                        sigma_x = pow(float(sigma_x_min)*float(sigma_x_max)*float(sigma_x_int), 1.0/3.0)
                        if with_errors:
                            output_line += f" {sigma_x:.2f}"
                        break

                if lat >= min_lat and lat <= max_lat and lon >= min_lon and lon <= max_lon:
                    print(output_line)
        return

