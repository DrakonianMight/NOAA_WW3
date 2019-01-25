
# coding: utf-8

# # Explore DES Wave Buoy data

# In[46]:


import requests
import json
import datetime
import numpy as np
import datetime
import pandas as pd


# In[49]:

def get_waves():
    """Retrieve wave data from the Open data portal"""
    r = requests.get("https://data.qld.gov.au/api/action/datastore_search?resource_id=2bbef99e-9974-49b9-a316-57402b00609c&limit=20000")
    f = r.json()  
    
    dataraw = f['result']['records']
    data = []
    for records in dataraw:
        recs = []
        for k in records:
            recs.append(records.get(k))
        data.append(recs)


    datadf = pd.DataFrame.from_dict(data)
    datadf.columns = list(dataraw[0].keys())
    datadf.index = pd.to_datetime(datadf.DateTime)
    
    now = datetime.datetime.now()
    fewago = now - datetime.timedelta(days=2.5)
    
    datadf = datadf.loc[fewago.strftime("%Y-%m-%d"): now.strftime("%Y-%m-%d")]
    datadf = datadf[~(datadf[['Tp','Hsig','Tz']] < -1).any(axis=1)]
    
    datadf.sort_index()
    return datadf


# In[35]:


def get_location():
    datadf = get_waves()
    sites = list(datadf.Site.unique())
    lats = []
    longs = []
    for i in sites:
        if str(datadf['Longitude'][datadf['Site'] == i][-1]) == '-99.9':
            continue
        if str(datadf['Latitude'][datadf['Site'] == i][-1]) == '-99.9':
            continue
        longs.append(str(datadf['Longitude'][datadf['Site'] == i][-1]))
        lats.append(str(datadf['Latitude'][datadf['Site'] == i][-1]))
    coords = list(zip(lats, longs))
    return coords
