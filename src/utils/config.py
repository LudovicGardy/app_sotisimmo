import numpy as np
import os
from dotenv import load_dotenv, find_dotenv
from google.oauth2 import service_account

def load_configurations():
    """
    Charge uniquement les variables du fichier .env si celui-ci est présent.
    Si le fichier .env n'existe pas, charge toutes les variables d'environnement du système.
    """
    dotenv_path = find_dotenv('.env')

    if dotenv_path:
        # Le fichier .env existe, charger uniquement ses variables
        load_dotenv(dotenv_path)
        # Retourne les variables chargées depuis le .env
        return {key: os.environ[key] for key in os.environ if key in open(dotenv_path).read()}
    else:
        # Le fichier .env n'existe pas, retourne toutes les variables d'environnement du système
        return dict(os.environ)

### CONFIGURATION ###
def page_config():
    '''
    Set the page configuration (title, favicon, layout, etc.)
    '''

    env_variables = load_configurations()

    page_dict = {
        'page_title': 'Sotis Immobilier',
        'subtitle': 'Prédictions de prix immobiliers',
        'description': 'Sotis Immobilier est une application web qui permet de prédire les prix immobiliers en France.',
        'author': 'Sotis AI',
        'base': 'dark',
        'page_icon': f'{env_variables["AWS_S3_URL"]}/Sotis_AI_pure_darkbg_240px.ico',
        'page_logo': f'{env_variables["AWS_S3_URL"]}/Sotis_AI_pure_darkbg_240px.png',
        'layout': 'wide',
        'initial_sidebar_state': 'auto',
        'markdown': '''
                    <style>
                        .css-10pw50 {
                            visibility:hidden;
                        }
                    </style>
                    ''',
    }

    return page_dict

def data_URL():
    '''
    Set the URLs to the data sources.
    '''

    env_variables = load_configurations()

    data_dict = {
        'summarized_data_url': f'{env_variables["AWS_S3_URL"]}/geo_dvf_summarized_full.csv.gz',
        'data_gouv': env_variables["DATA_GOUV_URL"],
        'data_gouv_years': list(np.arange(2018,2023+1)),
        '2024_merged': f'{env_variables["AWS_S3_URL"]}/2024_merged/departements',
    }

    return data_dict

### CREDENTIALS ###
def firebase_credentials():
    '''
    Load configuration from .env file or from OS environment variables
    '''
    
    # List of required keys in lowercase
    keys_list = [
        'project_id', 'private_key_id', 'private_key', 'client_email',
        'client_id', 'auth_uri', 'token_uri', 'auth_provider_x509_cert_url',
        'client_x509_cert_url'
    ]
    
    cred_dict = {}
    env_variables = load_configurations()

    # Check if all required keys exist and have a non-empty value
    try:
        for key in keys_list:
            value = env_variables.get(key.upper())
            if not value:
                raise ValueError(f'Missing or empty value for key: {key}')
            cred_dict[key] = value

        # Add prefix and suffix for the private_key
        cred_dict['private_key'] = cred_dict["private_key"].replace("/breakline/", "\n")
    except ValueError as e:
        print(f'Configuration error: {e}')
        cred_dict = {}  # Reset cred_dict if any key is missing or empty

    return cred_dict

def bigquery_credentials():
    env_variables = load_configurations()

    # Configuration de l'authentification avec variables d'environnement
    credentials_dict = {
        "type": env_variables.get('BIGQUERY_TYPE'),
        "project_id": env_variables.get('BIGQUERY_PROJECT_ID'),
        "private_key_id": env_variables.get('BIGQUERY_PRIVATE_KEY_ID'),
        "private_key": env_variables.get('BIGQUERY_PRIVATE_KEY').replace("/breakline/", "\n"),
        "client_email": env_variables.get('BIGQUERY_CLIENT_EMAIL'),
        "client_id": env_variables.get('BIGQUERY_CLIENT_ID'),
        "auth_uri": env_variables.get('BIGQUERY_AUTH_URI'),
        "token_uri": env_variables.get('BIGQUERY_TOKEN_URI'),
        "auth_provider_x509_cert_url": env_variables.get('ABIGQUERY_UTH_PROVIDER_X509_CERT_URL'),
        "client_x509_cert_url": env_variables.get('BIGQUERY_CLIENT_X509_CERT_URL')
    }

    return credentials_dict

def azure_credentials():

    keys_list = [
        'AZURE_SERVER', 'AZURE_DATABASE', 'AZURE_UID', 'AZURE_PWD', 'AZURE_TABLE'
    ]

    cred_dict = {}
    env_variables = load_configurations()

    # Check if all required keys exist and have a non-empty value
    try:
        for key in keys_list:
            value = env_variables.get(key.upper())
            if not value:
                raise ValueError(f'Missing or empty value for key: {key}')
            cred_dict[key] = value
    except ValueError as e:
        print(f'Configuration error: {e}')
        cred_dict = {}  # Reset cred_dict if any key is missing or empty

    return cred_dict

def AWS_credentials():
    keys_list = [
        'AWS_S3_URL'
    ]

    cred_dict = {}
    env_variables = load_configurations()

    # Check if all required keys exist and have a non-empty value
    try:
        for key in keys_list:
            value = env_variables.get(key.upper())
            if not value:
                raise ValueError(f'Missing or empty value for key: {key}')
            cred_dict[key] = value
    except ValueError as e:
        print(f'Configuration error: {e}')
        cred_dict = {}  # Reset cred_dict if any key is missing or empty

    return cred_dict