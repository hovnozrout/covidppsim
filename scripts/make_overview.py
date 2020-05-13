import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math
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
first_date = None

for index, row in covid_timeseries_df.iterrows():
    _, timeline = row

    if first_date == None or first_date > timeline.index[0]:
        first_date = timeline.index[0]

for index, row in covid_timeseries_df.iterrows():
    country, timeline = row

    # skip blacklisted countries
    if country in COUNTRY_BLACKLIST:
        continue

    print("processing", country)

    population_data = None
    aliases = [country]

    # check whether country has some aliases
    for a in COUNTRY_NAMES_ALIASES:
        if country in a:
            aliases = a
            break

    # match population data
    for wp_country in wp_countries:
        if wp_country in aliases:
            population_data = world_population_df[
                world_population_df["Country (or dependency)"] == wp_country].iloc[0]
            wp_countries.remove(wp_country)
            break

    # compute number of days passed to first movement
    first_confirmed = None
    first_death = None
    first_recovered = None

    for date, day_data in timeline.iterrows():
        if first_confirmed == None and day_data["confirmed"] > 0:
            first_confirmed = (date - first_date).days

        if first_recovered == None and day_data["recovered"] > 0:
            first_recovered = (date - first_date).days

        if first_death == None and day_data["deaths"] > 0:
            first_death = (date - first_date).days

    population_total = population_data["Population (2020)"]
    land_area = population_data["Land Area (Km²)"]
    migrants_count = population_data["Migrants (net)"]
    population_density = population_data["Density (P/Km²)"]
    population_net_change = population_data["Net Change"]
    fertility_rate = population_data["Fert. Rate"]
    med_age = population_data["Med. Age"]
    last_confirmed = timeline["confirmed"][-1]
    last_recovered = timeline["recovered"][-1]
    last_deaths = timeline["deaths"][-1]

    urban_population_percent = None
    if population_data["Urban Pop %"] != "N.A.":
        m = re.findall(URBAN_POP_REGEXP, population_data["Urban Pop %"])
        urban_population_percent = float(m[0])

    rows_confirmed_gt_zero = timeline[timeline["confirmed_gain"] > 0]
    rows_deaths_gt_zero = timeline[timeline["deaths_gain"] > 0]
    rows_recovered_gt_zero = timeline[timeline["recovered_gain"] > 0]

    overview_df = overview_df.append({
        "country": country,
        "max_confirmed_gain": timeline["confirmed_gain"].max(),
        "max_deaths_gain": timeline["deaths_gain"].max(),
        "max_recovered_gain": timeline["recovered_gain"].max(),
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
