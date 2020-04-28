import pandas as pd
import os
import pathlib
from datetime import datetime


class Dataset:
    def __init__(self, name):
        self.name = name

    def save_latest(self, df):
        filename = self._create_latest_path()
        path = os.path.dirname(filename)
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        df.to_pickle(filename)
        print(filename, "successfully saved")

    def load_latest(self):
        filename = self._get_latest_filename()
        print("reading", filename)
        return pd.read_pickle(filename)

    def _create_latest_path(self):
        now = datetime.now()
        return "datasets/" + self.name + "/" + now.strftime("%Y-%m-%dT%H:%M:%S") + ".pkl"

    def _get_latest_filename(self):
        path = "datasets/" + self.name + "/"
        return path + sorted(os.listdir(path))[-1]


covid_timeseries_dataset = Dataset("covid_timeseries")
world_population_dataset = Dataset("world_population")
overview_dataset = Dataset("overview")
