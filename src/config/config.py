"""
Configuration module for the Sotis Immobilier application.
This module handles all configuration settings including page layout, data sources, and environment variables.
"""

from dataclasses import dataclass
from typing import Any, Dict, List

from src.config.config_env import load_env_config, load_toml_config
from src.config.years import AVAILABLE_YEARS


@dataclass
class PageConfig:
    """Configuration settings for the Streamlit page."""
    page_title: str
    sidebar_title: str
    base: str
    page_icon: str
    page_logo: str
    layout: str
    initial_sidebar_state: str
    author: str
    markdown: str
    page_description: str
    footer: str

@dataclass
class DataConfig:
    """Configuration settings for data sources."""
    summarized_data_url: str
    datagouv_source_url: str
    available_years_datagouv: List[int]
    scrapped_year_current: str


def get_page_config() -> PageConfig:
    """
    Get the page configuration settings.
    
    Returns:
        PageConfig: A dataclass containing all page configuration settings.
    """
    env_config = load_env_config()
    toml_config = load_toml_config(".streamlit/config.toml")

    return PageConfig(
        page_title=toml_config.get("page_title", "Sotis Immobilier"),
        sidebar_title=f"# {toml_config.get('sidebar_title', 'Sotis A.I.')}",
        base=toml_config.get("base", "dark"),
        page_icon=f"{env_config.AWS_S3_URL}/Sotis_AI_pure_darkbg_240px.ico",
        page_logo=f"{env_config.AWS_S3_URL}/Sotis_AI_pure_darkbg_240px.png",
        layout=toml_config.get("layout", "wide"),
        initial_sidebar_state=toml_config.get("initial_sidebar_state", "auto"),
        author="Sotis AI",
        markdown="""
            <style>
                .css-10pw50 {
                    visibility:hidden;
                }
            </style>
        """,
        page_description="""Rendez-vous sur https://www.sotisai.com pour en savoir plus, 
        signaler un problème, une idée ou pour me contacter. Bonne visite !""",
        footer="Sotis A.I.© 2023"
    )


def get_data_config() -> DataConfig:
    """
    Get the data configuration settings.
    
    Returns:
        DataConfig: A dataclass containing all data source configuration settings.
    """
    env_config = load_env_config()

    return DataConfig(
        summarized_data_url=f"{env_config.AWS_S3_URL}/geo_dvf_summarized_full.csv.gz",
        datagouv_source_url=env_config.DATA_GOUV_URL,
        available_years_datagouv=AVAILABLE_YEARS,
        scrapped_year_current=f"{env_config.AWS_S3_URL}/2024_merged/departements"
    )


def get_config() -> Dict[str, Any]:
    """
    Get all configuration settings.
    
    Returns:
        Dict[str, Any]: A dictionary containing all configuration settings.
    """
    return {
        "page": get_page_config(),
        "data": get_data_config()
    } 