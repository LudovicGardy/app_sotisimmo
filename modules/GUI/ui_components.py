import streamlit as st
import random
import time

def init_page_config(page_config): ### Must be called before any other st. function
    st.set_page_config(page_title=page_config().get('page_title'), 
                page_icon = page_config().get('page_icon'),  
                layout = page_config().get('layout'),
                initial_sidebar_state = page_config().get('initial_sidebar_state'))

def display_sidebar(page_config):
    logo_path = page_config().get('page_logo')
    desired_width = 60

    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.image(logo_path, width=desired_width)
    with col2:
        st.write(page_config().get('sidebar_title'))

    st.caption(page_config().get('page_description'))

    st.divider()

def init_session_state():
    if 'selected_postcode_title' not in st.session_state:
        st.session_state.selected_postcode_title = None

