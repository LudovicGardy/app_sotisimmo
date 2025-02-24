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


### CREDENTIALS ###
def get_firebase_credentials() -> dict[str, Any]:
    """
    Load configuration from .env file or from OS environment variables
    """
    env_config = load_env_config()

    cred_dict = {
        "project_id": env_config.PROJECT_ID,
        "private_key_id": env_config.PRIVATE_KEY_ID,
        "private_key": env_config.PRIVATE_KEY.replace("/breakline/", "\n"),
        "client_email": env_config.CLIENT_EMAIL,
        "client_id": env_config.CLIENT_ID,
        "auth_uri": env_config.AUTH_URI,
        "token_uri": env_config.TOKEN_URI,
        "auth_provider_x509_cert_url": env_config.AUTH_PROVIDER_X509_CERT_URL,
        "client_x509_cert_url": env_config.CLIENT_X509_CERT_URL,
    }

    return cred_dict


def get_bigquery_credentials() -> dict[str, Any]:
    env_config = load_env_config()

    credentials_dict = {
        "type": env_config.TYPE,
        "project_id": env_config.PROJECT_ID,
        "private_key_id": env_config.PRIVATE_KEY_ID,
        "private_key": env_config.PRIVATE_KEY.replace("/breakline/", "\n"),
        "client_email": env_config.CLIENT_EMAIL,
        "client_id": env_config.CLIENT_ID,
        "auth_uri": env_config.AUTH_URI,
        "token_uri": env_config.TOKEN_URI,
        "auth_provider_x509_cert_url": env_config.AUTH_PROVIDER_X509_CERT_URL,
        "client_x509_cert_url": env_config.CLIENT_X509_CERT_URL,
    }

    return credentials_dict


def get_azure_credentials() -> dict[str, Any]:
    env_config = load_env_config()

    cred_dict = {
        "AZURE_SERVER": env_config.AZURE_SERVER,
        "AZURE_DATABASE": env_config.AZURE_DATABASE,
        "AZURE_UID": env_config.AZURE_UID,
        "AZURE_PWD": env_config.AZURE_PWD,
        "AZURE_TABLE": env_config.AZURE_TABLE,
    }

    return cred_dict


def get_AWS_credentials() -> dict[str, Any]:
    env_config = load_env_config()

    cred_dict = {
        "AWS_S3_URL": env_config.AWS_S3_URL,
    }

    return cred_dict
