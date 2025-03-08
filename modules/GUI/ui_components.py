from modules.config import get_page_config
import streamlit as st


def init_page_config():
    """
    Set the page configuration (title, favicon, layout, etc.)
    Must be called before ANY other st. function
    """
    st.set_page_config(
        page_title=get_page_config().get("page_title"),
        page_icon=get_page_config().get("page_icon"),
        layout=get_page_config().get("layout"),
        initial_sidebar_state=get_page_config().get("initial_sidebar_state"),
    )


def display_sidebar():
    logo_path = get_page_config().get("page_logo")
    desired_width = 60

    col1, col2 = st.columns([1, 3])

    with col1:
        st.image(logo_path, width=desired_width)
    with col2:
        st.write(get_page_config().get("sidebar_title"))

    st.caption(get_page_config().get("page_description"))

    st.divider()


def init_session_state():
    if "selected_postcode_title" not in st.session_state:
        st.session_state.selected_postcode_title = None
