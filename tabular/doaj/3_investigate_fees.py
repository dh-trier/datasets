import numpy as np
import pandas as pd
import json
from os.path import join, realpath, dirname
import seaborn as sns
from matplotlib import pyplot as plt
import re
from collections import Counter


workdir = join(realpath(dirname(__file__)))
doajdata_prepared = join(workdir, "data", "doaj-journaldata_prepared.csv")
doajdata_apcs = join(workdir, "data", "doaj-journaldata_apcs.csv")

def read_csv():
    """
    Load the CSV file with the DOAJ data. 
    Select the columns relevant to fees. 
    Returns: DataFrame
    """
    with open(doajdata_prepared, "r", encoding="utf8") as infile:
        data = pd.read_csv(infile, sep=";", index_col=0)
        #print(data.head())
        #print(list(data.columns))
        data = data.loc[:,["EISSN", "title", "publisher-country", "APC", "APC-amount", "CCBY", "domain"]]
        #print(data.head())
        #print(list(data.columns))
        return data


def identify_amount(x): 
    """
    Within a given cell, identify the first integer. 
    """
    x = re.match("\d+", str(x))
    if x: 
        x = int(x.group(0))
    else: 
        x = 0
    #print(x)
    return x


def identify_currency(x): 
    """
    Within a given cell, identify the first currency abbreviation.
    """
    # Match first occurrence of pattern
    x = re.findall("[A-Z]+", str(x))
    if x: 
        x = str(x[0])
    else: 
        x = "XXX"
    #print(x)
    return x



def calculate_eur(x): 
    """
    Within each cell, identify the numerical amount and the currency abbreviation. 
    Based on this information and the conversion rates, 
    calculate the corresponding amount in EUR for comparability. 
    """
    apc_num = identify_amount(x)
    apc_curr = identify_currency(x)
    apc_eur = 0
    if apc_num == 0: 
        apc_eur = 0
        apc_curr = "XXX"
    elif apc_curr == "EUR": 
        apc_eur = apc_num
    elif apc_curr == "USD": 
        apc_eur = apc_num * 0.8919
    elif apc_curr == "IDR":
        apc_eur = apc_num * 0.00006091
    elif apc_curr == "PLN":
        apc_eur = apc_num * 0.2147
    elif apc_curr == "GDP":
        apc_eur = apc_num * 1.1274
    elif apc_curr == "INR":
        apc_eur = apc_num * 0.0109
    elif apc_curr == "JPY":
        apc_eur = apc_num * 0.006615
    elif apc_curr == "BRL":
        apc_eur = apc_num * 0.1805
    elif apc_curr == "NOK":
        apc_eur = apc_num * 0.08439
    elif apc_curr == "CHF":
        apc_eur = apc_num * 0.9940
    elif apc_curr == "ZAR":
        apc_eur = apc_num * 0.04854
    elif apc_curr == "MXN":
        apc_eur = apc_num * 0.05019
    elif apc_curr == "ZAR":
        apc_eur = apc_num * 0.04854
    elif apc_curr == "PKR":
        apc_eur = apc_num * 0.003145
    elif apc_curr == "ARS":
        apc_eur = apc_num * 0.003942
    elif apc_curr == "RSD":
        apc_eur = apc_num * 0.008380
    elif apc_curr == "RUB":
        apc_eur = apc_num * 0.01162
    elif apc_curr == "IQD":
        apc_eur = apc_num * 0.0006807
    elif apc_curr == "CAD":
        apc_eur = apc_num * 0.6668
    elif apc_curr == "RON":
        apc_eur = apc_num * 0.1995
    elif apc_curr == "UAH":
        apc_eur = apc_num * 0.02438
    elif apc_curr == "EGP":
        apc_eur = apc_num * 0.02890
    elif apc_curr == "CNY":
        apc_eur = apc_num * 0.1290
    elif apc_curr == "IRR":
        apc_eur = apc_num * 0.00002123
    elif apc_curr == "SGD":
        apc_eur = apc_num * 0.6732
    elif apc_curr == "AUD":
        apc_eur = apc_num * 0.6021
    elif apc_curr == "CZK":
        apc_eur = apc_num * 0.04203
    elif apc_curr == "GHS":
        apc_eur = apc_num * 0.0770
    elif apc_curr == "KPW":
        apc_eur = apc_num * 0.002013
    elif apc_curr == "KZT":
        apc_eur = apc_num * 0.002013
    elif apc_curr == "KRW":
        apc_eur = apc_num * 0.0006768
    elif apc_curr == "MAD":
        apc_eur = apc_num * 0.08927
    elif apc_curr == "MDL":
        apc_eur = apc_num * 0.05021
    elif apc_curr == "NGN":
        apc_eur = apc_num * 0.001937
    elif apc_curr == "PEN":
        apc_eur = apc_num * 0.2414
    elif apc_curr == "PKR":
        apc_eur = apc_num * 0.003145
    elif apc_curr == "SYP":
        apc_eur = apc_num * 0.0003550
    elif apc_curr == "THB":
        apc_eur = apc_num * 0.02627
    elif apc_curr == "TRY":
        apc_eur = apc_num * 0.04574
    elif apc_curr == "VND":
        apc_eur = apc_num * 0.00003804
    elif apc_curr == "XAF":
        apc_eur = apc_num * 0.001524
    elif apc_curr == "XOF":
        apc_eur = apc_num * 0.001524
    elif apc_curr == "YER":
        apc_eur = apc_num * 0.003564
    else: 
        apc_eur = 0
        apc_curr = "XXX"
    #print(apc_eur, "EUR :", apc_num,  apc_curr)
    return apc_eur


def apc_in_eur(data): 
    data["APC-EUR"] = data["APC-amount"].apply(lambda x: calculate_eur(x))
    data = data.sort_values(by="APC-EUR", ascending=False)
    print(data.head(10))
    print("min:", np.min(data["APC-EUR"]))
    print("median:", np.median(data["APC-EUR"]))
    print("mean:", np.mean(data["APC-EUR"]))
    print("max:", np.max(data["APC-EUR"]))
    print("stdev:", np.std(data["APC-EUR"]))
    return data


def make_histogram0(data): 
    n = len(data)
    plot = sns.histplot(data,
                        x="APC-EUR",
                        bins=100,
                        kde=False,
                        stat="percent"
                        )
    plt.title("Distribution of all APCs in DOAJ (including 0, n=" + str(n) + ")")
    plt.savefig("APC-histogram_all.png", dpi=300)
    plt.close()


def make_histogram1(data): 
    data = data[data["APC-EUR"] > 0]
    n = len(data)
    plot = sns.histplot(data,
                        x="APC-EUR",
                        bins=100,
                        kde=False,
                        stat="percent"
                        )
    plt.title("Distribution of non-zero APCs in DOAJ (1-8000 EUR, n=" + str(n) + ")")
    plt.savefig("APC-histogram_nonzero.png", dpi=300)
    plt.close()

def make_histogram2(data): 
    data = data.loc[(data["APC-EUR"] > 500) & (data["APC-EUR"] < 3000)]
    n = len(data)
    plot = sns.histplot(data,
                        x="APC-EUR",
                        bins=100,
                        kde=False,
                        #stat="percent"
                        )
    plt.title("Distribution of midrange APCs in DOAJ (500-3000 EUR, n=" + str(n) + ")")
    plt.savefig("APC-histogram_midrange.png", dpi=300)
    plt.close()


def make_histogram3(data): 
    data = data.loc[(data["APC-EUR"] > 10) & (data["APC-EUR"] < 500)]
    n = len(data)
    plot = sns.histplot(data,
                        x="APC-EUR",
                        bins=100,
                        kde=False,
                        stat="percent"
                        )
    plt.title("Distribution of low APCs in DOAJ (10-500 EUR, n=" + str(n) + ")")
    plt.savefig("APC-histogram_low.png", dpi=300)
    plt.close()


def make_histogram4(data): 
    data = data.loc[(data["APC-EUR"] > 3000) & (data["APC-EUR"] < 8000)]
    n = len(data)
    plot = sns.histplot(data,
                        x="APC-EUR",
                        bins=100,
                        kde=False,
                        stat="percent"
                        )
    plt.title("Distribution of high APCs in DOAJ (3000-8000 EUR, n=" + str(n) + ")")
    plt.savefig("APC-histogram_high.png", dpi=300)
    plt.close()


def save_data(data): 
    """
    Save the resulting DataFrame to CSV. 
    Returns: CSV file on disk.
    """
    #print(data.head())
    with open(doajdata_apcs, "w", encoding="utf8") as outfile: 
        data.to_csv(outfile, sep=";")



def main(): 
    data = read_csv()
    data = apc_in_eur(data)
    save_data(data)
    make_histogram0(data)
    make_histogram1(data)
    make_histogram2(data)
    make_histogram3(data)
    make_histogram4(data)

main()