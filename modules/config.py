from dotenv import dotenv_values
import os
import numpy as np

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
    try:
        # Try to load environment variables from the .env file
        print('\n\nSearching in local environment variables (.env file)...')
        config = dotenv_values('.env')
        source = config if config else os.environ
    except Exception as e:
        # Fallback to OS environment variables if .env file is not found
        print('\n\nNo .env file was found or an error occurred:', str(e))
        print('Searching in OS environment variables...')
        source = os.environ

    # Check if all required keys exist and have a non-empty value
    try:
        for key in keys_list:
            value = source.get(key.upper())
            if not value:
                raise ValueError(f'Missing or empty value for key: {key}')
            cred_dict[key] = value

        # Add prefix and suffix for the private_key
        cred_dict['private_key'] = f'-----BEGIN PRIVATE KEY-----\n{cred_dict["private_key"]}\nv/CmHtyEa6fPS+oi/oOPureIBcFBjNLKjzdcDzdUokAPwBVhZf0z0JO4zcqc+vfi\nXQpG4gOfzzYc6xie+RtMcWKEEV/DKFhJsQXgXfqs0f/KdtzZ0LPO8AH4y7txizew\nFi1FZSJ67ZDku5fzCP9jdMsQky1ItXzUnGfFckxV9FzT+Wm0/IMu/dr4o42Ms/+d\nB5wKV62/m1M35OcKsu6lahCIMzbqok5Tu92CZIpurLrB1y+MgpJ8xVUG/yRackPV\nZit/6g2gYRo1BtdfuTc0OK+ec4hhT+zxhIb4FQuBgB5g9smKKu1SACJyheMXOBsp\nsvi0z10tAgMBAAECggEASXq1bQPR7673RnZ17f+D9/VOkipnJlki424kXVXE0Wt0\nsK0sqWtiqFCM/7ZffrQ0/67vCuvkZNYnqaeRvDsTp4Gk+JMkZrv1CA7+EjMFK3S7\nJ4jeHejyKsyyT3CQNDCyClkdo5yeQas8OhsCbJNz4w1XVNTI7FWa1eMryhtZYAZy\nNFerqANc/vS0fhBlgY852aa8ntEocbVjwv0teoJAqIT8ZVc0bYYWf6kYqT+6Ygys\ngXGCtmIyNAkOEmz/g0jBi8YJf7PoXk51cVJ4IHuJbMtoPWimyHScNC/skh0LPnZH\nwyTmuHPeadBj2z2UXRQBlUQEsLwnOEPdF9qncijmvwKBgQD2KSiN2ZPNzNsuYXlF\nx38qb13ZicBG0ynyvfG5ERK8bXOgS+ur+8+ArgBlvS0T5JNHIetDzwq9J/8A+NMj\nS/UiUHfqrhFXx7/4f+4z2vptktYQNEwYikGUaUFGdj73rswCqW+kQNd8h322CIZi\n0O5BNP5sAkgaYeBSNmf4gGSxIwKBgQDEFafXlD7JuiPtSwuCMTWvnyYPODuk3/ry\nroiDa3UXyFfkSxLWaCz+zPQAHjA5Ktf4Nq5VjaJQhNDBja/tjtjGZKXEnqq7hrmx\nqKxCaJWJaC4yrJmbQ964Cgv52lz+4NuWMR8gMfRsw+fW0ihZBnFX1vfHrlUMbTRU\nN4Th4EmlbwKBgQDPseqFxQ7wlehZOeUY+zpQk6ab5Z5WI9VA+wL5I26rja4Bkg1H\nDzAFYsrzDKr8HeAmJHhcvlRRRW3jZA7BuVUbnsmPOU9owSE4irhxCFJEIaB8C6Qp\nEH5EuopY6Ww3j0SS+mM4M32dlLR84rSAq8hbPFtuxn4PxIWA2GbhRXOwAQKBgQCG\nJFJ4VoBFvMOLOEWdQVD63iNJUizrdBbXIrNdRIwMQxBtqzYt24K8pTVfR0eyNC8f\nLTlCaexarSGq5+Us3QZLYttMkUc3lsk+UqfVnnp+T/kazZ0f7ORWfvkGam4oJ2fR\nbbVfbw1JwxO9kHPtw0ySzQshXY/tOmAMJRcQ90EqnQKBgBftpQuhKSwPL6idaYGh\n4IdKgWKLkIy2pkUagHv1y4giVp/Qk5Z9qhqk/+adu0MDKEpfKrMSRzaEC8U2HZzR\nBYaws7sGqxNojXjCjZAsAgrR/ik1dJofaWc9PcsKTlPKFSwI5RffaKl4MBJ4m/xA\nlstIbgdUbjCtpAanEi5wdMKK\n-----END PRIVATE KEY-----\n'
    except ValueError as e:
        print(f'Configuration error: {e}')
        cred_dict = {}  # Reset cred_dict if any key is missing or empty

    return cred_dict

def azure_credentials():

    cred_dict = {
        'server': 'serveur-oct-2023.database.windows.net',
        'database': 'SotisImmo_DB',
        'uid': 'root_gardy',
        'pwd': 'Tagazok123',
        'table': 'BienIci'
    }

    return cred_dict

def page_config():
    '''
    Set the page configuration (title, favicon, layout, etc.)
    '''

    page_dict = {
        'page_title': 'Sotis Immobilier',
        'subtitle': 'Prédictions de prix immobiliers',
        'description': 'Sotis Immobilier est une application web qui permet de prédire les prix immobiliers en France.',
        'author': 'Sotis AI',
        'page_icon': 'https://sotisimmo.s3.eu-north-1.amazonaws.com/Sotis_AI_pure_darkbg_240px.ico',
        'page_logo': 'https://sotisimmo.s3.eu-north-1.amazonaws.com/Sotis_AI_pure_darkbg_240px.png',
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

    data_dict = {
        'summarized_data_url': 'https://sotisimmo.s3.eu-north-1.amazonaws.com/geo_dvf_summarized_full.csv.gz',
        'data_gouv': 'https://files.data.gouv.fr/geo-dvf/latest/csv',
        'data_gouv_years': list(np.arange(2018,2023+1)),
        '2024_merged': 'https://sotisimmo.s3.eu-north-1.amazonaws.com/2024_merged/departements',
    }

    return data_dict