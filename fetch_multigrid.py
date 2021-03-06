
# coding: utf-8

# # Script to download NOAA wave model data

# **Date:** 25-01-2019
# 
# **Purpose:** Downloads NOAA model data for wave buoy locations

# In[1]:


import pandas as pd
import numpy as np
import datetime as dt
import requests
import io
from multiprocessing.pool import ThreadPool as Pool
import xarray as xr
import fetch_online_des_waves


# Generate a list of model run urls

# In[2]:


def build_urls():
    prevdate = dt.datetime.strftime(dt.datetime.utcnow() - dt.timedelta(days=1), "%Y%m%d")
    date = dt.datetime.strftime(dt.datetime.utcnow(), "%Y%m%d")
    baseurl = 'https://nomads.ncep.noaa.gov:9090/dods/wave/mww3/'
    runs = ['00','06','12','18']
    name = """/multi_1.glo_30mext"""
    
    yesterdays = []
    todays = []
    for t in runs:
        if (dt.datetime.utcnow().hour - 6) > int(t):
            todays.append(t)
        else:
            yesterdays.append(t)
    
    urls = []
    for r in yesterdays:
        urls.append(baseurl+prevdate+name+prevdate+'_'+str(r)+'z')
    for r in todays:
        urls.append(baseurl+date+name+date+'_'+str(r)+'z')
    return urls


# In[6]:


def get_location():
    datadf = fetch_online_des_waves.get_waves()
    sites = list(datadf.Site.unique())
    lats = []
    longs = []
    site = []
    for i in sites:
        if str(datadf['Longitude'][datadf['Site'] == i][-1]) == '-99.9':
            continue
        if str(datadf['Latitude'][datadf['Site'] == i][-1]) == '-99.9':
            continue
        longs.append(str(datadf['Longitude'][datadf['Site'] == i][-1]))
        lats.append(str(datadf['Latitude'][datadf['Site'] == i][-1]))
        site.append(i)
    coords = list(zip(lats, longs, site))
    return coords


# In[9]:


def get_data(url):
    """takes in a url and returns the data from the NOAA Multgrid wave model for each wave buoy location
    """
    dataset = xr.open_dataset(url)
    locs = get_location()
    dataframes = []
    for loc in locs:
        sitedata = dataset.sel(lon=float(loc[1]), lat=float(loc[0]), method='nearest')
        df = sitedata.htsgwsfc.to_dataframe()
        df['perpwsfc'] = sitedata.perpwsfc.data
        df['dirpwsfc'] = sitedata.dirpwsfc.data
        df['site'] = loc[-1]
        df.index = df.index + pd.Timedelta(hours = 10)
        dataframes.append(df)
    data = pd.concat(dataframes)
    return data


# In[ ]:


def main():
    pool = Pool(4) # or whatever your hardware can support
    urls = build_urls()
    dfs = pool.map(get_data,  urls)
    return dfs

if __name__ == '__main__':
    main()