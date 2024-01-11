import asyncio

import aiohttp
import requests
from loguru import logger
from pydantic_settings import BaseSettings


class Environment(BaseSettings):
    PORT_API_URL: str = "https://api.getport.io/v1"
    PORT_CLIENT_ID: str
    PORT_CLIENT_SECRET: str
    # define service envs here
    # SERVICE_TOKEN: str

    class Config:
        env_file = ".env"

ENVIRONMENT = Environment()

# define blueprint ids here
SERVICE_BLUEPRINT = "serviceItem"

## Get Port Access Token
credentials = {"clientId": ENVIRONMENT.PORT_CLIENT_ID, "clientSecret": ENVIRONMENT.PORT_CLIENT_SECRET}

token_response = requests.post(f"{ENVIRONMENT.PORT_API_URL}/auth/access_token", json=credentials)
token_response.raise_for_status()
access_token = token_response.json()["accessToken"]

# You can now use the value in access_token when making further requests
headers = {"Authorization": f"Bearer {access_token}"}


async def add_entity_to_port(
    session: aiohttp.ClientSession, blueprint_id, entity_object
):
    """A function to create the passed entity in Port

    Params
    --------------
    session: aiohttp.ClientSession
        The aiohttp session object

    blueprint_id: str
        The blueprint id to create the entity in Port

    entity_object: dict
        The entity to add in your Port catalog

    Returns
    --------------
    None
    """
    logger.info(f"Adding entity to Port: {entity_object}")
    response = await session.post(
        (
            f"{ENVIRONMENT.PORT_API_URL}/blueprints/"
            f"{blueprint_id}/entities?upsert=true&merge=true"
        ),
        json=entity_object,
        headers=headers,
    )
    if not response.ok:
        logger.info("Ingesting {blueprint_id} entity to port failed, skipping...")
    logger.info(f"Added entity to Port: {entity_object}")


async def main():
    logger.info("Starting Port integration")
    async with aiohttp.ClientSession() as session:
        pass


if __name__ == "__main__":
    asyncio.run(main())