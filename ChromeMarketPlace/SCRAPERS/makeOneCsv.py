# will use all of our fucntions to make a df and then display it on streamlit
# this function will return one df that is cleaned
# horizantal stack the dfs
# run every week to get the most up to date data

import os
import pandas as pd
import concurrent.futures
import sqlite3

from SCRAPERS.yp import scrapeYP
from SCRAPERS.scrapeSuns import scrapeSuns
from SCRAPERS.jReed import scrapeJR
from SUPPORT.profiler import run_weekly
from SCRAPERS.topDrwr import scrapeTD

def removeCH(df):
    #remove the words chrome hearts from the name column
    df["Name"] = df["Name"].str.replace("Chrome Hearts", "")

    return df

def cleanData(df):
    # any extra cleaning that needs to be done
    pass

def save_to_db(df, db_path="chrome_hearts.db"):
    conn = sqlite3.connect(db_path)
    df.to_sql("items", conn, if_exists="replace", index=False)
    conn.close()

@run_weekly("combined_data.csv")
def makeOneDF():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_yp = executor.submit(scrapeYP)
        future_sun = executor.submit(scrapeSuns)
        future_jr = executor.submit(scrapeJR)
        future_TD = executor.submit(scrapeTD)
        
        #result
        yp = future_yp.result()
        sun = future_sun.result()
        jr = future_jr.result()
        TD = future_TD.result()

    # Ensure all dataframes are not empty
    if yp.empty or sun.empty or jr.empty or TD.empty:
        raise ValueError("One or more dataframes are empty")

    fullDF = pd.concat([yp, TD, sun, jr], ignore_index=True)
    fullDF = removeCH(fullDF)
    cleanData(fullDF)

    # Save to database
    save_to_db(fullDF)

    return fullDF

