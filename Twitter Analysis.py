

#importing modules
import streamlit as st
import numpy as np
import pandas as pd
from urllib.request import urlopen
import json
import plotly.express as px


# In[93]:


#variables to hold path of source files
path_to_confirmed_file = "covid_confirmed_usafacts.csv"
path_to_county_population_file = "covid_county_population_usafacts.csv"
path_to_deaths_file = "covid_deaths_usafacts.csv"


# In[94]:



#reading files
covid_confirmed = pd.read_csv(path_to_confirmed_file)
covid_county_population = pd.read_csv(path_to_county_population_file)
covid_deaths = pd.read_csv(path_to_deaths_file)
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)
    


# # Question 1

# In[101]:



#method to get data frame for weekly covid cases across USA
@st.cache
def build_confirmed_weekly_dataframe():
    df = covid_confirmed.drop(['countyFIPS','County Name','State','StateFIPS'],axis = 1).diff(axis=1)
    df = df.fillna(0)
    df = df.sum().to_frame("Cases").reset_index()
    df = df.rename(columns = {'index':'Date'})
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.drop([0,1,2,3,746,747])
    df = df.groupby( pd.Grouper(key='Date', freq='W-SUN'))['Cases'].sum().to_frame()
    return df

confirmed_weekly_cases = build_confirmed_weekly_dataframe()
st.title("COVID ANALYSIS")
st.write("Line plot of weekly new cases in US")
st.line_chart(confirmed_weekly_cases['Cases'])






#method to get dataframe for weekly covid deaths across USA

@st.cache
def build_deaths_weekly_dataframe():
    df = covid_deaths.drop(['countyFIPS','County Name','State','StateFIPS'],axis = 1).diff(axis=1)
    df = df.fillna(0)
    df = df.sum().to_frame("deaths").reset_index()
    df = df.rename(columns = {'index':'Date'})
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.drop([0,1,2,3,746,747])
    df = df.groupby( pd.Grouper(key='Date', freq='W-SUN'))['deaths'].sum().to_frame()
    return df

confirmed_weekly_deaths = build_deaths_weekly_dataframe()
st.write("Line plot of weekly new deaths in US")
st.line_chart(confirmed_weekly_deaths['deaths'])




# In[103]:


#method to get data frame for weekly covid cases across USA by county
@st.cache    
def build_confirmed_cases_df():
    case_data = covid_confirmed.loc[:,['State','countyFIPS']].join(covid_confirmed.drop(['countyFIPS','County Name','State','StateFIPS'],axis = 1).diff(axis=1).fillna(0))
    case_data = case_data.set_index(['State','countyFIPS']).join(covid_county_population.set_index(['State','countyFIPS']), on=['State','countyFIPS']).reset_index()
    cols = list(case_data.columns)
    cols.remove('State') 
    cols.remove('countyFIPS')
    cols.remove('County Name')
    cols.remove('population')
    case_data = case_data.loc[case_data.population != 0,:]
    case_data = case_data.fillna(0)
    case_data.loc[:, cols] = case_data.loc[:, cols] * 100000
    case_data.loc[:, cols] = case_data.loc[:, cols].div(case_data['population'], axis=0)
    case_data.loc[:, cols] = case_data.loc[:, cols].round()
    case_data = case_data.drop(['State','County Name','population'],axis = 1).groupby('countyFIPS').sum().T.reset_index()
    case_data = case_data.rename(columns = {'index':'Date'})
    case_data['Date'] = pd.to_datetime(case_data['Date'])
    case_data = case_data.groupby( pd.Grouper(key='Date', freq='W-SUN')).sum()
    case_data = case_data.drop(0,axis = 1)
    case_data = case_data.reset_index()
    case_data = case_data.melt(id_vars=["Date"], var_name="countyFIPS", value_name="Count")
    case_data.countyFIPS = case_data.countyFIPS.astype(str).apply(lambda x: x.zfill(5)) 
    case_data.Date = case_data.Date.astype(str)
    case_data.index = case_data.Date
    return case_data


# In[ ]:


#method to get data frame for weekly covid deaths across USA by county
@st.cache    
def build_death_cases_df():
    death_data = covid_deaths.loc[:,['State','countyFIPS']].join(covid_deaths.drop(['countyFIPS','County Name','State','StateFIPS'],axis = 1).diff(axis=1).fillna(0))
    death_data = death_data.set_index(['State','countyFIPS']).join(covid_county_population.set_index(['State','countyFIPS']), on=['State','countyFIPS']).reset_index()
    cols = list(death_data.columns)
    cols.remove('State') 
    cols.remove('countyFIPS')
    cols.remove('County Name')
    cols.remove('population')
    death_data = death_data.loc[death_data.population != 0,:]
    death_data = death_data.fillna(0)
    death_data.loc[:, cols] = death_data.loc[:, cols] * 100000
    death_data.loc[:, cols] = death_data.loc[:, cols].div(death_data['population'], axis=0)
    death_data.loc[:, cols] = death_data.loc[:, cols].round()
    death_data = death_data.drop(['State','County Name','population'],axis = 1).groupby('countyFIPS').sum().T.reset_index()
    death_data = death_data.rename(columns = {'index':'Date'})
    death_data['Date'] = pd.to_datetime(death_data['Date'])
    death_data = death_data.groupby( pd.Grouper(key='Date', freq='W-SUN')).sum()
    death_data = death_data.drop(0,axis = 1)
    death_data = death_data.reset_index()
    death_data = death_data.melt(id_vars=["Date"], var_name="countyFIPS", value_name="Count")
    death_data.countyFIPS = death_data.countyFIPS.astype(str).apply(lambda x: x.zfill(5)) 
    death_data.Date = death_data.Date.astype(str)
    death_data.index = death_data.Date
    return death_data


# In[113]:


#method to build figures for covid cases and deaths
@st.cache
def get_figures(counties, cases_data,deaths_data):
    figure = px.choropleth(cases_data, geojson=counties, 
                            locations='countyFIPS',
                            color='Count',
                            color_continuous_scale="Viridis",
                            scope="usa",
                            width=800,
                            height=500,
                           )
    figure.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    figure2 = px.choropleth(deaths_data, geojson=counties, 
                            locations='countyFIPS',
                            color='Count',
                            color_continuous_scale="Viridis",
                            scope="usa",
                            width=800,
                            height=500,
                           )
    figure2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return figure,figure2

#building dataframe of covid cases
case_data = build_confirmed_cases_df()
#building dataframe of covid deaths
death_data = build_death_cases_df()

st.write("Weekly analysis of covid cases per week by US county")


plot_spot1 = st.empty()
plot_spot2 = st.empty()

#slider for date
date = st.select_slider('Select Date',options=case_data['Date'].unique().tolist())

#Button to run through dates
if st.button("Run Through Dates"):
    for date in case_data['Date'].unique().tolist():
        cases_data = case_data[case_data['Date']==date]
        deaths_data = death_data[death_data['Date']==date]
        figure1, figure2 = get_figures(counties, cases_data, deaths_data)
        with plot_spot1:
            st.plotly_chart(figure1)
        with plot_spot2:
            st.plotly_chart(figure2)

cases_data = case_data[case_data['Date']==date]
deaths_data = death_data[death_data['Date']==date]
figure1,figure2 = get_figures(counties, cases_data,deaths_data)
with plot_spot1:
    st.plotly_chart(figure1)
with plot_spot2:
    st.plotly_chart(figure2)


