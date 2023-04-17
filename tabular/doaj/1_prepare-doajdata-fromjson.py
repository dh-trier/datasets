"""
Script to build a CSV file from the JSON version of the DOAJ data. 
Not recommended, as the DOAJ CSV file has more information and is easier to handle. 
"""

import numpy as np
import pandas as pd
import json
from os.path import join, realpath, dirname
from scipy.stats import chi2_contingency as c2c


workdir = join(realpath(dirname(__file__)))
doajdata_original = join(workdir, "data", "doaj-journaldata_original.json")
doajdata_prepared = join(workdir, "data", "doaj-journaldata_prepared.csv")


def read_json():
    with open(doajdata_original, "r", encoding="utf8") as infile:
        data = json.loads(infile.read())
    #print(json.dumps(data, indent=2, sort_keys=True))
    data = pd.json_normalize(data)
    data.replace("", np.nan, inplace=True)
    return data


def simplify_headers(data): 
    data.rename(columns=lambda s: s.replace("bibjson.", ""), inplace=True)
    data.rename(columns={
        "editorial.review_process" : "review",
        "pid_scheme.has_pid_scheme": "pid_scheme",
        "deposit_policy.has_policy": "deposit_policy",
        "institution.country": "country",
        "apc.has_apc": "apc",
        "created_date": "created",
        "waiver.has_waiver": "waiver",
        "copyright.author_retains": "copyright",
        "plagiarism.detection": "plagiarism_detection",
        "article.orcid": "orcid",
        "publication_time_weeks" : "publication_time",
        "preservation.has_preservation" : "preservation",
        "publisher.country" : "publisher_country",
        "language" : "languages"
        },inplace=True)
    return data


def filter_data(data): 
    #print(data.columns)
    data = data[[
        "eissn",
        "title",
        "created",
        #"review",
        "copyright",
        "plagiarism_detection",
        "orcid",
        "pid_scheme",
        "deposit_policy",
        "publication_time",
        "waiver",
        "preservation",
        "publisher_country",
        "languages",
        "apc",
        ]]
    data = data.dropna(subset=["eissn"])
    return data


def simplify_values(data): 
    # Date of creation as year
    data["created"] = data["created"].astype("string").str[0:4].astype("int")
    # Date of creation as early/late (binary)
    data["created_early"] = [True if value < np.median(data["created"]) else False for value in data["created"]]
    # Publication time fast/slow (binary)
    data["publication_time_fast"] = [True if value < np.median(data["publication_time"]) else False for value in data["publication_time"]]
    # Publisher country as one-hot-variables
    pc = pd.get_dummies(data["publisher_country"], prefix="pc", columns="publisher_country")
    data = pd.concat([data, pc], axis=1)
    # Publication languages as one-hot-variables
    pl = pd.get_dummies(data["languages"].apply(pd.Series).stack(), prefix="pl").groupby(level=1).sum()
    data = pd.concat([data, pl], axis=1)
    return data


def filter_incomplete_data(data): 
    # Remove rows that don't have complete data
    # This step ensures complete and consistent data. 
    # However, it reduces the size of the dataset considerably. 
    data.replace("", np.nan, inplace=True)
    print("shape before filtering", data.shape)
    data.dropna(axis=0, how="all", inplace=True)
    print("shape after filtering", data.shape)
    return data


def save_data(data): 
    print(data.head())
    with open(doajdata_prepared, "w", encoding="utf8") as outfile: 
        data.to_csv(outfile)


def main(): 
    data = read_json()
    data = simplify_headers(data)
    data = filter_data(data)
    data = simplify_values(data)
    data = filter_incomplete_data(data) # optional
    save_data(data)

main()