import numpy as np
import pandas as pd
import json
from os.path import join, realpath, dirname
from scipy.stats import chi2_contingency as c2c
import seaborn as sns
from matplotlib import pyplot as plt


workdir = join(realpath(dirname(__file__)))
doajdata_prepared = join(workdir, "data", "doaj-journaldata_prepared.csv")


def read_csv():
    """
    Load the CSV file with the DOAJ data. 
    Returns: DataFrame
    """
    with open(doajdata_prepared, "r", encoding="utf8") as infile:
        data = pd.read_csv(infile, index_col=0)
        return data


def inspect_table(data):
    """
    First very simple inspection of the data. 
    """
    # Have a look at the top of the dataframe
    print(data.head())
    # Get the list of column headers
    print(list(data.columns))


def visualize_columns(data): 
    """
    Several ways to look at the distribution of values for certain categories. 
    Which values are the most frequent for domain, publisher country, language, etc.?
    """
    # See some counts for various variables
    print("publication_time_fast", dict(data["publication-time-fast"].value_counts()))
    print("apc", dict(data["APC"].value_counts()))
    print("orcid", dict(data["ORCIDs"].value_counts()))
    print("domain", dict(data["domain"].value_counts()))
    print("publisher countries", dict(data["publisher-country"].value_counts()))
    languages = ["English", "German", "French", "Portuguese", "Italian", "Spanish",\
                 "Chinese", "Indonesian", "Arabic", "Malay", "Swedish", "Polish",\
                 "Hungarian", "Czech", "Greek", "Danish", "Catalan", "Croatian",\
                 "Romanian", "Ukrainian", "Japanese", "Persian", "Russian", "Serbian", "Turkish"]
    for lang in languages: 
        print(lang, int(np.sum(data["lang_"+lang])))



def visualize_features(data): 
    """
    Creates several plots of selected data. 
    """
    sns.set_style("whitegrid")

    # Histogram of publication time: 
    # How long does it take for articles to be published, in weeks?
    sns.displot(data = data, x="publication-time")
    plt.title("DOAJ data", size=14)
    plt.suptitle("Histogram of publication time in weeks", size=10)
    plt.savefig(join(workdir, "figures", "hist_publication-time.png"), dpi=300)
    plt.close()

    # Barchart of year being added to DOAJ:
    # When was the journal ready to be indexed in DOAJ?
    from collections import Counter
    seldata = dict(Counter(data["added-date"]))
    seldata = pd.DataFrame.from_dict(seldata, orient="index", columns=["number"])
    seldata = seldata.sort_index()
    seldata.plot(kind="bar")
    plt.title("DOAJ data", size=14)
    plt.suptitle("Number of titles added per year", size=10)
    plt.savefig(join(workdir, "figures", "bar_date-added.png"), dpi=300)
    plt.close()

    # Scatterplot of publication time x added date, split by APC. 
    plot = sns.scatterplot(
        data = data, 
        x = "publication-time", 
        y = "added-date", 
        hue="APC")
    plt.title("DOAJ data", size=14)
    plt.tight_layout()
    plt.savefig(join(workdir, "figures", "scatter_pub-x-added.png"), dpi=300)
    plt.close()

    # Scatterplot of publication time x number of articles, split by APC
    data.drop(data[data["article-records"] >= 5000].index, inplace=True)
    plot = sns.scatterplot(
        data = data, 
        x = "publication-time", 
        y = "article-records", 
        hue="APC")
    plt.title("DOAJ data", size=14)
    plt.tight_layout()
    plt.savefig(join(workdir, "figures", "scatter_pub-x-articles.png"), dpi=300)
    plt.close()


    # Scatterplot of added date x number of articles, split by APC. 
    def jitter(values,j):
        return values + np.random.normal(j,0.1,values.shape)
    plot = sns.scatterplot(
        data = data, 
        x = jitter(data["added-date"], 5), 
        y = jitter(data["article-records"], 5), 
        hue="APC",
        y_jitter=10)
    plt.title("DOAJ data", size=14)
    plt.tight_layout()
    plt.savefig(join(workdir, "figures", "scatter_added-x-articles.png"), dpi=300)
    plt.close()


    # Barchart of APC proportion per country
    # This requires preparing a pivot table first. 
    seldata = data.loc[:,["publisher-country", "APC"]]
    pivoted = pd.pivot_table(
        seldata,
        index="publisher-country",
        columns="APC",
        values="APC",
        aggfunc=np.count_nonzero)
    pivoted.fillna(0, inplace=True)
    pivoted["all"] = pivoted[False] + pivoted[True]
    pivoted["apc-prop"] = round((pivoted[True] / pivoted["all"] * 100), 1)
    pivoted["noapc-prop"] = round((pivoted[False] / pivoted["all"] * 100), 1)
    pivoted.sort_values(by="apc-prop", ascending=True, inplace=True)
    pivoted.drop(pivoted[pivoted["all"] < 50].index, inplace=True)
    print(pivoted.shape)
    pivoted["apc-prop"].plot(kind="barh", figsize=(10,14))
    plt.suptitle("DOAJ data", size=14)
    plt.xlim(0,100)
    plt.xlabel("Percentage of journals that charge an APC")
    plt.title("Percentage of journals with an APC by country\
        \n(minimum number of DOAJ journals per country: 50)", size=12)
    plt.tight_layout()
    plt.savefig(join(workdir, "figures", "bar_apc-per-country.png"), dpi=300)
    plt.close()


    # Barchart of APC proportion per (rough) subject domain
    # Again, a pivot table is required. 
    seldata = data.loc[:,["domain", "APC"]]
    pivoted = pd.pivot_table(
        seldata,
        index="domain",
        columns="APC",
        values="APC",
        aggfunc=np.count_nonzero)
    pivoted.fillna(0, inplace=True)
    pivoted["all"] = pivoted[False] + pivoted[True]
    pivoted["apc-prop"] = round((pivoted[True] / pivoted["all"] * 100), 1)
    pivoted["noapc-prop"] = round((pivoted[False] / pivoted["all"] * 100), 1)
    pivoted.sort_values(by="apc-prop", ascending=True, inplace=True)
    print(pivoted.shape)
    pivoted["apc-prop"].plot(kind="barh", figsize=(10,8))
    plt.suptitle("DOAJ data", size=14)
    plt.xlim(0,100)
    plt.xlabel("Percentage of journals that charge an APC")
    plt.title("Percentage of journals with an APC by domain", size=12)
    plt.tight_layout()
    plt.savefig(join(workdir, "figures", "bar_apc-per-domain.png"), dpi=300)
    plt.close()


def main(): 
    data = read_csv()
    inspect_table(data)
    visualize_columns(data)
    visualize_features(data)

main()