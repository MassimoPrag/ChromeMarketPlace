"""
Paid service website
would like to make a website and API

Scrapes price data from multiple websites into one database

https://ypcollective.com/collections/chrome-hearts
https://originsnyc.com/collections/chrome-hearts?filter.v.availability=1
https://topdrwr.io/brand/chrome-hearts 
https://www.grailed.com/designers/chrome-hearts

Will allow users to view the data base and search for items and provide links to the websites
Will allow users to create an account and save items to their profile

Will filter through sold and unsold items, size, price, etc

ability to recomend items

will re scrape every so often or upon request

"""
from langchain_openai import ChatOpenAI
from browser_use import Agent, Controller
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.controller.service import Controller
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, SecretStr
import pandas as pd
import json
from typing import List, Dict
import os
import streamlit as st

load_dotenv()

import asyncio

llm = ChatGoogleGenerativeAI(model='gemini-1.5-flash', api_key=SecretStr("AIzaSyDMPcsvZmoMo88v8i9oG2S6iNkJPXYGAEs"))
#llm = ChatOpenAI(model="gpt-4o")
links = [ 
    "https://ypcollective.com/collections/chrome-hearts",
    "https://topdrwr.io/brand/chrome-hearts", 
    "https://www.grailed.com/designers/chrome-hearts"
]
task_description = f"""
Visit all links provided in {links} to give me Chrome Hearts item listing data from each link. There are {len(links)} links to visit. Make sure to visit all the links. Return a sing json.

Guidelines:
1. Still collect items that are sold out or unavailable, and if not specified if available or not, then assume it is available.
2. Do not visit any other websites.
3. If any specific info is not available then return 'N/A'.
4. For the url and image url can you make sure the full url is recorded.
5. For item url, if you cannot find the url for the specific item, then return the URL for the website.
"""
class Itemm(BaseModel):
    item_name: str
    price: float
    size: str
    availability: bool
    image_url: str
    item_url: str
    
class Items(BaseModel):
    items: List[Itemm]

controller = Controller(output_model=Items)

async def agentGrailed():
    agent = Agent(
        task= task_description,
        #initial_actions=initial_actions,
        llm=llm,
        controller=controller

    )
    history = await agent.run()
    result = history.final_result()
    return result


#print(asyncio.run(agentGrailed()))



st.title("Chrome Hearts Price Scraper")

if st.button("Fetch Data"):
    result_data = asyncio.run(agentGrailed())  # Run the async function
    st.subheader("Fetched Data")

    # Dynamically display the JSON data
    if isinstance(result_data, dict):  # If the result is a dictionary
        first_key = next(iter(result_data), None)  # Get the first key
        if first_key:
            st.write(f"**{first_key}:**")
            value = result_data[first_key]
            if isinstance(value, list) and all(isinstance(item, dict) for item in value):
                st.dataframe(pd.DataFrame(value), height=1000)
            else:
                st.json(value)
        else:
            st.json(result_data)  # Fallback if the dictionary is empty
    elif isinstance(result_data, list):  # If the result is a list of dictionaries
        st.dataframe(pd.DataFrame(result_data), height=1000)
    else:  # Fallback for unexpected structures
        st.write("Unsupported data format:", result_data)

























# Front end __________________ vvvvvv

"""
st.title("Chrome Hearts Price Scraper")
if st.button("Fetch Data"):
    result = asyncio.run(agent())  # Run the async function
    #result_data = json.loads(result)  # Parse the JSON result
    st.json(result_data)  # Display the JSON result in Streamlit

    if isinstance(result_data, dict) and "items" in result_data:
        st.dataframe(pd.DataFrame(result_data["items"]), height=1000)  # Display as a table with increased height
    else:
        st.json(result_data)  # Fallback to JSON view if structure is unexpected
"""
