import os
import toml

from typing import Any
from dataclasses import dataclass
from dotenv import find_dotenv, load_dotenv


@dataclass
class EnvConfig:
    AUTH_PROVIDER_X509_CERT_URL: str
    AUTH_URI: str
    AWS_S3_URL: str
    CLIENT_EMAIL: str
    CLIENT_ID: str
    CLIENT_X509_CERT_URL: str
    OPENAI_API_KEY: str
    PRIVATE_KEY: str
    PRIVATE_KEY_ID: str
    PROJECT_ID: str
    REPLICATE_API_KEY: str
    TOKEN_URI: str
    TYPE: str
    UNIVERSE_DOMAIN: str
    DATA_GOUV_URL: str

    @staticmethod
    def load_from_env() -> "EnvConfig":
        # Load environment variables from .env file
        dotenv_path = find_dotenv(".env")

        # Add them to the environment
        if dotenv_path:
            load_dotenv(dotenv_path)

        # Check if all required environment variables are set
        missing_vars = []
        env_vars = {
            "AUTH_PROVIDER_X509_CERT_URL": os.getenv("AUTH_PROVIDER_X509_CERT_URL"),
            "AUTH_URI": os.getenv("AUTH_URI"),
            "AWS_S3_URL": os.getenv("AWS_S3_URL"),
            "CLIENT_EMAIL": os.getenv("CLIENT_EMAIL"),
            "CLIENT_ID": os.getenv("CLIENT_ID"),
            "CLIENT_X509_CERT_URL": os.getenv("CLIENT_X509_CERT_URL"),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
            "PRIVATE_KEY": os.getenv("PRIVATE_KEY"),
            "PRIVATE_KEY_ID": os.getenv("PRIVATE_KEY_ID"),
            "PROJECT_ID": os.getenv("PROJECT_ID"),
            "REPLICATE_API_KEY": os.getenv("REPLICATE_API_KEY"),
            "TOKEN_URI": os.getenv("TOKEN_URI"),
            "TYPE": os.getenv("TYPE"),
            "UNIVERSE_DOMAIN": os.getenv("UNIVERSE_DOMAIN"),
            "DATA_GOUV_URL": os.getenv("DATA_GOUV_URL"),
        }

        for key, value in env_vars.items():
            if value is None:
                missing_vars.append(key)

        if missing_vars:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

        return EnvConfig(**env_vars)


def load_env_config() -> EnvConfig:
    """
    Charge uniquement les variables du fichier .env si celui-ci est présent.
    Si le fichier .env n'existe pas, charge toutes les variables d'environnement du système.
    """
    return EnvConfig.load_from_env()


def load_toml_config(file_path) -> dict[str, Any]:
    """
    Charge les configurations à partir d'un fichier .toml
    """
    try:
        with open(file_path, "r") as file:
            return toml.load(file).get("theme", {})
    except FileNotFoundError:
        return {}
