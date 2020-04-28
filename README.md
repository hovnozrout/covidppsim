# COVID 19 probabilistic programming based simulation

## Usage
There are several scripts which you can utilize:
- `fetch` - fetches all base datasets, saves them in `datasets` folder
- `make_overview` - generates an overview (covid vs countries) table from basic datasets
- `analyze_overview` - analyzes generated overview (foundations for covid confirmed susceptible gain distribution)

## Overview table explained
When you generate overview table, it has these columns:
- `country` - just country name
- `max_confirmed_gain` - Max __confirmed__ daily gain value
- `max_deaths_gain` - Max __deaths__ daily gain value
- `max_recovered_gain` - Max __recovered__ daily gain value
- `avg_confirmed_gain` - Average __confirmed__ daily gain value (zeros are omitted)
- `avg_recovered_gain` - Average __recovered__ daily gain value (zeros are omitted)
- `avg_deaths_gain` - Average __deaths__ daily gain value (zeros are omitted)
- `std_confirmed_gain` - Standard deviation of daily __confirmed__ gain value (zeros are omitted)
- `std_recovered_gain` - Standard deviation of daily __recovered__ gain value (zeros are omitted)
- `std_deaths_gain` - Standard deviation of daily __deaths__ gain value (zeros are omitted)
- `first_confirmed` - Number of days passed to first confirmed patient
- `first_recovered` - Number of days passed to first recovered patient
- `first_deaths` - Number of days passed to first death occurrence
- `population_total` - Total population of country (N in SIR model)
- `confirmed_per_population_percent` - Total confirmed cases in population (percentage), in other words % of confirmed country population
- `recovered_per_population_percent` - Total recovered cases in population (percentage), in other words % of recovered country population
- `deaths_per_population_percent` - Total death cases in population (percentage), in other words % of dead country population
- `last_confirmed` - Total confirmed cases (latest value)
- `last_recovered` - Total recovered cases (latest value)
- `last_deaths` - Total death cases (latest value)
- `land_area` - Land area of country (in km^2)
- `migrants_count` - Total number of migrants
- `population_density` - Number of people per km^2
- `population_net_change` - Absolute net change of population
- `urban_population_percent`: - Percentage of urban population
