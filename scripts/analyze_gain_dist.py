import math
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

from dataset import covid_timeseries_dataset

sns.set(style="darkgrid")

df = covid_timeseries_dataset.load_latest()

i = 0
MAX_COUNT = math.inf

with PdfPages("results/hist.pdf") as export_pdf:
    for index, row in df.iterrows():
        country, timeline = row

        print("processing", country)

        confirmed_gain = list(timeline["confirmed_gain"])
        confirmed_gain_gt_zero = np.trim_zeros(confirmed_gain, "f")

        fig, axes = plt.subplots(3, 1)
        fig.suptitle(country, fontsize=16)
        fig.set_size_inches(10, 10)

        sns.distplot(confirmed_gain_gt_zero, ax=axes[0])
        timeline[["confirmed", "recovered", "deaths"]].plot(ax=axes[1])
        timeline[["confirmed_gain", "recovered_gain",
                  "deaths_gain"]].plot(ax=axes[2])
        # sns.boxplot(data=timeline[["confirmed_gain", "recovered_gain",
        #    "deaths_gain"]])
        # plt.grid(True)

        export_pdf.savefig()
        plt.close()

        i += 1

        if i == MAX_COUNT:
            break
