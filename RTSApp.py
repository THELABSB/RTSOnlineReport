import streamlit as st
import numpy as np
import pandas as pd
import ReturntoSport
import athletereport
import survey
from PIL import Image
st.set_page_config(page_title='Return To Sport - The LAB', page_icon=':anger:', layout="wide", initial_sidebar_state="auto", menu_items=None)


df=pd.read_csv('returntosport.csv', encoding='UTF-8', header =(0))
logo= Image.open('Lab_FullColor.jpg')


col1, col2,col3= st.columns([1,0.5,0.5])    
col3.image(logo, width= 200)
#name=st.selectbox('Athlete Name', df['Name'])

PAGES = {
    "Athlete Report": athletereport,
    "Athlete RTS Survey": survey,
    "Assessment Data": ReturntoSport
    
}
st.sidebar.title('Navigation')
selection = st.sidebar.radio("Go to", list(PAGES.keys()))
page = PAGES[selection]
page.app()