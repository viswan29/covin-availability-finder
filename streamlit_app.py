import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from covid_availability_finder import get_availability

st.title('Covin Vaccine Availability')
st.markdown('<i style="text-align: right;"><br>--Developed by <b>[Viswa](https://github.com/viswan29)</b></i>', unsafe_allow_html=True)
st.markdown('<style>h1{color: red;}</style>', unsafe_allow_html=True)

@st.cache
def get_data():
    return pd.read_csv('all_districts.csv')

data = get_data()

districts_data=dict(data.values)

available_districts=list(districts_data.keys())
min_age_limit = st.sidebar.radio('Minimum Age Limit', [18, 45])
option = st.sidebar.multiselect('District', available_districts,default=['Prakasam'])
table_option = st.sidebar.radio('Table Type', ['Normal','DataFrame'])
available_district_ids=[districts_data[val] for val in option]

    
try:
    df=get_availability(available_district_ids,min_age_limit)
    if table_option=='DataFrame':
        st.write(df)
    else:
        st.table(df)
    
except:
    st.markdown('Unable to fetch data. Try after some time')
