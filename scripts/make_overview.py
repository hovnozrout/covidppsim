import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re
from dataset import covid_timeseries_dataset, world_population_dataset, overview_dataset

covid_timeseries_df = covid_timeseries_dataset.load_latest()
world_population_df = world_population_dataset.load_latest()

COUNTRY_NAMES_ALIASES = [
    ["US", "United States"],
    ["Czechia", "Czech Republic (Czechia)"],
    ["Taiwan*", "Taiwan"],
    ["Korea, South", "South Korea"],
    ["Cote d'Ivoire", "Côte d'Ivoire"],
    ["Saint Vincent and the Grenadines", "St. Vincent & Grenadines"],
    ["Sao Tome and Principe", "Sao Tome & Principe"],
    ["Burma", "Myanmar"]
]

COUNTRY_BLACKLIST = [
    "Congo (Brazzaville)",
    "Congo (Kinshasa)",
    "Diamond Princess",
    "West Bank and Gaza",
    "Saint Kitts and Nevis",
    "Kosovo",
    "MS Zaandam"
]

URBAN_POP_REGEXP = r'\d+'

overview_df = pd.DataFrame()

wp_countries = list(world_population_df["Country (or dependency)"])
covid_data_countries = [
    c for c in covid_timeseries_df.columns if c not in COUNTRY_BLACKLIST]
# covid_data_countries = ["Czechia"]

first_date = pd.to_datetime(covid_timeseries_df.values[0][0]["date"])

for country_name in covid_data_countries:
    print("---", country_name)

    population_data = None
    aliases = [country_name]

    # check whether country has some aliases
    for a in COUNTRY_NAMES_ALIASES:
        if country_name in a:
            aliases = a
            break

    # match population data
    for wp_country in wp_countries:
        if wp_country in aliases:
            population_data = world_population_df[
                world_population_df["Country (or dependency)"] == wp_country].iloc[0]
            wp_countries.remove(wp_country)
            break

    # if type(population_data) == "NoneType":
    #     raise Exception(
    #         "Unable to match with world_population dataset: " + country_name)

    covid_df = pd.DataFrame(list(covid_timeseries_df[country_name]))

    covid_df["date"] = pd.to_datetime(covid_df["date"])
    covid_df.set_index("date", inplace=True)

    covid_df["confirmed_gain"] = 0
    covid_df["deaths_gain"] = 0
    covid_df["recovered_gain"] = 0

    first_confirmed = None
    first_death = None
    first_recovered = None

    for i in range(1, len(covid_df)):
        current = covid_df.iloc[i]
        prev = covid_df.iloc[i - 1]

        if first_confirmed == None and current["confirmed"] > 0:
            first_confirmed = (current.name - first_date).days

        if first_death == None and current["deaths"] > 0:
            first_death = (current.name - first_date).days

        if first_recovered == None and current["recovered"] > 0:
            first_recovered = (current.name - first_date).days

        covid_df["confirmed_gain"][i] = current["confirmed"] - \
            prev["confirmed"]
        covid_df["deaths_gain"][i] = current["deaths"] - prev["deaths"]
        covid_df["recovered_gain"][i] = current["recovered"] - \
            prev["recovered"]

    population_total = population_data["Population (2020)"]
    land_area = population_data["Land Area (Km²)"]
    migrants_count = population_data["Migrants (net)"]
    population_density = population_data["Density (P/Km²)"]
    population_net_change = population_data["Net Change"]
    fertility_rate = population_data["Fert. Rate"]
    med_age = population_data["Med. Age"]
    last_confirmed = covid_df["confirmed"][-1]
    last_recovered = covid_df["recovered"][-1]
    last_deaths = covid_df["deaths"][-1]

    urban_population_percent = None
    if population_data["Urban Pop %"] != "N.A.":
        m = re.findall(URBAN_POP_REGEXP, population_data["Urban Pop %"])
        urban_population_percent = float(m[0])

    rows_confirmed_gt_zero = covid_df[covid_df["confirmed_gain"] > 0]
    rows_deaths_gt_zero = covid_df[covid_df["deaths_gain"] > 0]
    rows_recovered_gt_zero = covid_df[covid_df["recovered_gain"] > 0]

    overview_df = overview_df.append({
        "country": country_name,
        "max_confirmed_gain": covid_df["confirmed_gain"].max(),
        "max_deaths_gain": covid_df["deaths_gain"].max(),
        "max_recovered_gain": covid_df["recovered_gain"].max(),
        "avg_confirmed_gain": rows_confirmed_gt_zero["confirmed_gain"].mean(),
        "avg_deaths_gain": rows_deaths_gt_zero["deaths_gain"].mean(),
        "avg_recovered_gain": rows_recovered_gt_zero["recovered_gain"].mean(),
        "std_confirmed_gain": rows_confirmed_gt_zero["confirmed_gain"].std(),
        "std_deaths_gain": rows_deaths_gt_zero["deaths_gain"].std(),
        "std_recovered_gain": rows_recovered_gt_zero["recovered_gain"].std(),
        "first_confirmed": first_confirmed,
        "first_death": first_death,
        "first_recovered": first_recovered,
        "population_total": population_total,
        "last_confirmed": last_confirmed,
        "last_recovered": last_recovered,
        "last_deaths": last_deaths,
        "confirmed_per_population_percent":
            last_confirmed / population_total * 100 if last_confirmed else None,
        "recovered_per_population_percent":
            last_recovered / population_total * 100 if last_recovered else None,
        "deaths_per_population_percent":
            last_deaths / population_total * 100 if last_deaths else None,
        "land_area": land_area,
        "migrants_count": migrants_count,
        "population_density": population_density,
        "population_net_change": population_net_change,
        "urban_population_percent": urban_population_percent
    }, ignore_index=True)

overview_df.to_csv("results/overview.csv", index=False)
overview_dataset.save_latest(overview_df)

print("Done")
