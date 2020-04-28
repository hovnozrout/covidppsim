import pandas as pd
import requests
from bs4 import BeautifulSoup

from dataset import covid_timeseries_dataset, world_population_dataset


def fetch_world_population_data():
    res = requests.get(
        "https://www.worldometers.info/world-population/population-by-country/")
    soup = BeautifulSoup(res.content, "lxml")
    table = soup.find(id="example2")
    df = pd.read_html(str(table))[0]

    world_population_dataset.save_latest(df)


def fetch_covid19_timeseries_data():
    df = pd.read_json(
        "https://pomber.github.io/covid19/timeseries.json")

    covid_timeseries_dataset.save_latest(df)


fetch_world_population_data()
fetch_covid19_timeseries_data()

print("Done")
