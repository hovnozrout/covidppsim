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

    result = pd.DataFrame()

    for (col_name, col_data) in df.iteritems():
        col_list = list(col_data)
        country_df = pd.DataFrame(col_list)

        country_df["date"] = pd.to_datetime(country_df["date"])
        country_df.set_index("date", inplace=True)

        confirmed_gain = [0]
        recovered_gain = [0]
        deaths_gain = [0]

        for i in range(1, len(col_list)):
            confirmed_gain.append(
                col_list[i]["confirmed"] - col_list[i - 1]["confirmed"])
            recovered_gain.append(
                col_list[i]["recovered"] - col_list[i - 1]["recovered"])
            deaths_gain.append(
                col_list[i]["deaths"] - col_list[i - 1]["deaths"])

        country_df["confirmed_gain"] = confirmed_gain
        country_df["recovered_gain"] = recovered_gain
        country_df["deaths_gain"] = deaths_gain

        result = result.append({
            "country": col_name,
            "timelime": country_df
        }, ignore_index=True)

    covid_timeseries_dataset.save_latest(result)


fetch_world_population_data()
fetch_covid19_timeseries_data()

print("Done")
