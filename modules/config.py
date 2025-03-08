import numpy as np

from typing import Any
from modules.config_env import load_env_config, load_toml_config


def get_page_config() -> dict[str, Any]:
    """
    Set the page configuration (title, favicon, layout, etc.)
    """
    env_config = load_env_config()
    toml_config = load_toml_config(".streamlit/config.toml")

    page_dict = {
        "page_title": toml_config.get("page_title", "Sotis Immobilier"),
        "sidebar_title": f"# {toml_config.get('sidebar_title', 'Sotis A.I.')}",
        "base": toml_config.get("base", "dark"),
        "page_icon": f"{env_config.AWS_S3_URL}/Sotis_AI_pure_darkbg_240px.ico",
        "page_logo": f"{env_config.AWS_S3_URL}/Sotis_AI_pure_darkbg_240px.png",
        "layout": toml_config.get("layout", "wide"),
        "initial_sidebar_state": toml_config.get("initial_sidebar_state", "auto"),
        "author": "Sotis AI",
        "markdown": """
                    <style>
                        .css-10pw50 {
                            visibility:hidden;
                        }
                    </style>
                    """,
        "page_description": """Ce prototype propose de répondre à un besoin de lecture plus claire du marché immobilier. 
                    \nRendez-vous sur https://www.sotisanalytics.com pour en savoir plus, signaler un problème, une idée ou pour me contacter. Bonne visite ! 
                    \nSotis A.I.© 2023""",
    }

    return page_dict


def get_data_URL() -> dict[str, Any]:
    """
    Set the URLs to the data sources.
    """
    env_config = load_env_config()

    data_dict = {
        "summarized_data_url": f"{env_config.AWS_S3_URL}/geo_dvf_summarized_full.csv.gz",
        "datagouv_source_URL": env_config.DATA_GOUV_URL,
        "available_years_datagouv": list(np.arange(2018, 2024 + 1)),
        "scrapped_year_current": f"{env_config.AWS_S3_URL}/2024_merged/departements",
    }

    return data_dict
