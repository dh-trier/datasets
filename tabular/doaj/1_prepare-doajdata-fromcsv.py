# https://doaj.org/docs/public-data-dump/

import numpy as np
import pandas as pd
import re
import json
from os.path import join, realpath, dirname
from scipy.stats import chi2_contingency as c2c


workdir = join(realpath(dirname(__file__)))
doajdata_original = join(workdir, "data", "doaj-journaldata_original.csv")
doajdata_prepared = join(workdir, "data", "doaj-journaldata_prepared.csv")


def read_csv():
    """
    Load the CSV file containing the raw data as downloaded from: 
    https://doaj.org/docs/public-data-dump/ (January 2, 2023)
    Returns: DataFrame
    """
    with open(doajdata_original, "r", encoding="utf8") as infile:
        data = pd.read_csv(infile)
    data.replace("", np.nan, inplace=True)
    #print(data.head())
    return data


def simplify_names(data): 
    """
    Shortens some of the country labels for easier treatment, 
    especially in visualizations. 
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.replace.html
    """
    data = data.replace({
        "Russian Federation" : "Russia",
        "Iran, Islamic Republic of" : "Iran", 
        "Korea, Republic of" : "Korea",
        "Bolivia, Plurinational State of" : "Bolivia",
        "Brunei Darussalam" : "Brunei",
        "Congo, The Democratic Republic of the" : "Congo",
        "Moldova, Republic of" : "Moldova",
        "Palestine, State of" : "Palestine",
        "Syrian Arab Republic" : "Syria", 
        "Taiwan, Province of China" : "Taiwan",
        "Venezuela, Bolivarian Republic of" : "Venezuela"
        })
    #print(data.head())
    return data


def select_columns(data): 
    """
    From all available columns in the data, select those to retain
    for further treatment. 
    """
    #print(list(data.columns))
    data = data[[
        "Journal title",
        "Journal EISSN (online version)",
        "Languages in which the journal accepts manuscripts",
        "Publisher",
        "Country of publisher",
        "Journal license",
        "Machine-readable CC licensing information embedded or displayed in articles",
        "Author holds copyright without restrictions",
        "Review process",
        "Average number of weeks between article submission and publication",
        "APC",
        "APC amount",
        "Journal waiver policy (for developing country authors etc)",
        "Has other fees",
        "Preservation Services",
        "Persistent article identifiers",
        "Article metadata includes ORCIDs",
        "Journal complies with I4OC standards for open citations",
        "Does the journal comply to DOAJ\'s definition of open access?",
        "LCC Codes",
        "Subjects",
        "DOAJ Seal",
        "Added on Date",
        "Number of Article Records",
        ]]
    #print(list(data.columns))
    return data


def simplify_headers(data): 
    """
    Replace long, descriptive column names with shorter names for convenience. 
    Remember to look up the long names here if unsure about the meaning. 
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.rename.html
    """
    data.rename(columns={
        "Journal title" : "title",
        "Journal EISSN (online version)" : "EISSN",
        "Languages in which the journal accepts manuscripts" : "languages",
        "Publisher" : "publisher",
        "Country of publisher" : "publisher-country",
        "Journal license" : "license",
        "Machine-readable CC licensing information embedded or displayed in articles" : "license-embedded",
        "Author holds copyright without restrictions" : "author-copyright",
        "Review process" : "review-process",
        "Average number of weeks between article submission and publication" : "publication-time",
        "APC" : "APC",
        "APC amount" : "APC-amount",
        "Journal waiver policy (for developing country authors etc)" : "APC-waiver",
        "Has other fees" : "other-fees",
        "Preservation Services" : "preservation",
        "Persistent article identifiers" : "pids",
        "Article metadata includes ORCIDs" : "ORCIDs",
        "Journal complies with I4OC standards for open citations" : "I4OC",
        "Does the journal comply to DOAJ\'s definition of open access?" : "DOAJ-OA",
        "LCC Codes" : "LCC",
        "Subjects" : "subjects",
        "DOAJ Seal" : "DOAJ-seal",
        "Added on Date" : "added-date",
        "Number of Article Records" : "article-records",
        },inplace=True)
    #print(list(data.columns))
    return data



def simplify_values(data): 
    """
    Simplify some of the values, either from exact date to year, 
    or from detailed numerical data to simple binary data. 
    Using list comprehension with if/else structure. 
    """
    # Date of creation as year
    data["added-date"] = data["added-date"].astype("string").str[0:4].astype("int")
    # Date of creation as early/late (binary)
    data["created-early"] = [True if value < np.median(data["added-date"]) else False for value in data["added-date"]]
    # Publication time fast/slow (binary)
    data["publication-time-fast"] = [True if value < np.median(data["publication-time"]) else False for value in data["publication-time"]]
    # Language of publication: English-only or not (binary)
    data["English-only"] = [True if value == "English" else False for value in data["languages"]]
    # License: CC BY or not (binary)
    data["CCBY"] = [True if value == "CC BY" else False for value in data["license"]]
    # Code all instances of "Yes" as "True" and "No" as "False"
    data.replace("Yes", "True", regex=False, inplace=True)
    data.replace("No", "False", regex=False, inplace=True)
    return data


def simplify(row):
    """
    Helper function called by simplify_subjects.
    (Could probably be simplified with a loop over a list of pairs.)
    """
    if "Social" in row["subjects"]:
        value = "SocialSciences"
    elif "Science" in row["subjects"]:
        value = "Science"
    elif "Biology" in row["subjects"]:
        value = "Science"
    elif "Chemistry" in row["subjects"]:
        value = "Science"
    elif "Medicine" in row["subjects"]:
        value = "Medicine"
    elif "History" in row["subjects"]:
        value = "Humanities"
    elif "history" in row["subjects"]:
        value = "Humanities"
    elif "Philosophy" in row["subjects"]:
        value = "Humanities"
    elif "Language" in row["subjects"]:
        value = "Humanities"
    elif "Literature" in row["subjects"]:
        value = "Humanities"
    elif "Music" in row["subjects"]:
        value = "Humanities"
    elif "Arts" in row["subjects"]:
        value = "Humanities"
    elif "Museums" in row["subjects"]:
        value = "Humanities"
    elif "Law" in row["subjects"]:
        value = "SocialSciences"
    elif "Political" in row["subjects"]:
        value = "SocialSciences"
    elif "Psychology" in row["subjects"]:
        value = "SocialSciences"
    elif "Geography" in row["subjects"]:
        value = "SocialSciences"
    elif "Technology" in row["subjects"]:
        value = "Technology"
    elif "Agriculture" in row["subjects"]:
        value = "Agriculture"
    elif "Education" in row["subjects"]:
        value = "Education"
    elif "Library" in row["subjects"]:
        value = "LIS"
    elif "Information" in row["subjects"]:
        value = "LIS"
    elif "General" in row["subjects"]:
        value = "General"
    else: 
        value = "other"
    return value


def simplify_subjects(data):
    """
    Reduce the various descriptive lists of subjects covered 
    to very rough domain categories for easier treatment. 
    Something similar could be done with countries => continents. 
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.apply.html
    """
    data["domain"] = data.apply(simplify, axis=1)
    return data


def one_hot_encoding(data): 
    """
    In order for some of the data to be available as binary data, 
    re-encode it as one-hot variables. Creates a lot of additional columns! 
    https://pandas.pydata.org/docs/reference/api/pandas.get_dummies.html
    """
    # Publisher country as one-hot-variables (all of them automatically!)
    pc = pd.get_dummies(data["publisher-country"], prefix="pc", columns="publisher-country", dtype=bool)
    data = pd.concat([data, pc], axis=1)
    # Simplified domain as one-hot-variables (all of them automatically!)
    pc = pd.get_dummies(data["domain"], prefix="d", columns="domain", dtype=bool)
    data = pd.concat([data, pc], axis=1)
    # Publication languages as one-hot-variables (selection only!)
    languages = ["English", "German", "French", "Portuguese", "Italian", "Spanish",\
                 "Chinese", "Indonesian", "Arabic", "Malay", "Swedish", "Polish",\
                 "Hungarian", "Czech", "Greek", "Danish", "Catalan", "Croatian",\
                 "Romanian", "Ukrainian", "Japanese", "Persian", "Russian", "Serbian", "Turkish"]
    for lang in languages: 
        data["lang_"+lang] = [True if lang in value else False for value in data["languages"]]
    return data



def filter_incomplete_data(data): 
    """
    Removes rows that don't have complete data for specific columns. 
    Depending on the column, this can lead to a drastic reduction in data available,
    so this needs to be used with care. 
    https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dropna.html
    """
    # Remove all rows that don't have complete data for specific columns
    #print("shape before filtering", data.shape)
    data = data.dropna(subset=["EISSN"])
    #print("shape after filtering", data.shape)
    return data


def lookup(x, countrydata, label):
    country = x["publisher-country"]
    #print(country)
    try: 
        value = int(countrydata.loc[countrydata["stateLabel"] == country, label].item())
    except: 
        value = 0
        #print("error", country)
    return value


def add_external_data(data): 
    # Get the contents of the country data CSV file
    with open(join(workdir, "data", "country-data.csv"), "r", encoding="utf8") as infile: 
        countrydata = pd.read_csv(infile)
    countrydata.drop(["year"], axis=1, inplace=True)
    #print(countrydata.head())
    data["gdp"] = data.apply(lambda x: lookup(x, countrydata, "gdp"), axis=1)
    data["population"] = data.apply(lambda x: lookup(x, countrydata, "population"), axis=1)
    #data["wdid"] = data.apply(lambda x: lookup(x, countrydata, "state"), axis=1)
    return data



def save_data(data): 
    """
    Save the resulting DataFrame to CSV. 
    Returns: CSV file on disk.
    """
    #print(data.head())
    with open(doajdata_prepared, "w", encoding="utf8") as outfile: 
        data.to_csv(outfile, sep=";")


def main(): 
    data = read_csv()
    data = simplify_names(data)
    data = select_columns(data)
    data = simplify_headers(data)
    data = simplify_values(data)
    data = simplify_subjects(data)
    data = one_hot_encoding(data) # optional
    data = filter_incomplete_data(data) # optional
    data = add_external_data(data) # optional
    save_data(data)

main()