import asyncio

import aiohttp
import requests
import dotenv
from loguru import logger
from google.cloud import artifactregistry_v1
from pydantic_settings import BaseSettings

dotenv.load_dotenv()

class Environment(BaseSettings):
    PORT_API_URL: str = "https://api.getport.io/v1"
    PORT_CLIENT_ID: str
    PORT_CLIENT_SECRET: str
    GCP_REGIONS: str
    GCP_PROJECT_ID: str

ENVIRONMENT = Environment()
GCP_REGIONS = ENVIRONMENT.GCP_REGIONS.split(",")

REPOSITORY_BLUEPRINT = "gcrRepository"
IMAGE_BLUEPRINT = "gcrImage"
ALL_GCR_REGIONS = {
    "asia-east1",
    "asia-east2",
    "asia-northeast1",
    "asia-northeast2",
    "asia-northeast3",
    "asia-south1",
    "asia-south2",
    "asia-southeast1",
    "asia-southeast2",
    "australia-southeast1",
    "australia-southeast2",
    "europe-central2",
    "europe-north1",
    "europe-southwest1",
    "europe-west1",
    "europe-west2",
    "europe-west3",
    "europe-west4",
    "europe-west6",
    "europe-west8",
    "europe-west9",
    "europe-west10",
    "europe-west12",
    "us-west1",
    "us-west2",
    "us-west3",
    "us-west4",
    "us-central1",
    "us-east1",
    "us-east4",
    "us-east5",
    "us-south1",
    "northamerica-northeast1",
    "northamerica-northeast2",
    "southamerica-east1",
    "southamerica-east2",
    "me-central1",
    "me-central2",
    "me-west1",
}

## Get Port Access Token
credentials = {"clientId": ENVIRONMENT.PORT_CLIENT_ID, "clientSecret": ENVIRONMENT.PORT_CLIENT_SECRET}

token_response = requests.post(f"{ENVIRONMENT.PORT_API_URL}/auth/access_token", json=credentials)
token_response.raise_for_status()
access_token = token_response.json()["accessToken"]

# You can now use the value in access_token when making further requests
headers = {"Authorization": f"Bearer {access_token}"}

artifact_registry_client = artifactregistry_v1.ArtifactRegistryClient()


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

async def ingest_repositories(session: aiohttp.ClientSession, repository: artifactregistry_v1.Repository):
    class_format = {
        artifactregistry_v1.Repository.Format.DOCKER: "DOCKER",
        artifactregistry_v1.Repository.Format.MAVEN: "MAVEN",
        artifactregistry_v1.Repository.Format.NPM: "NPM",
        artifactregistry_v1.Repository.Format.APT: "APT",
        artifactregistry_v1.Repository.Format.YUM: "YUM",
        artifactregistry_v1.Repository.Format.GO: "GO",
        artifactregistry_v1.Repository.Format.PYTHON: "PYTHON",
        artifactregistry_v1.Repository.Format.FORMAT_UNSPECIFIED: "FORMAT_UNSPECIFIED",
        artifactregistry_v1.Repository.Format.KFP: "KFP",
    }
    mode_format = {
        artifactregistry_v1.Repository.Mode.MODE_UNSPECIFIED: "MODE_UNSPECIFIED",
        artifactregistry_v1.Repository.Mode.REMOTE_REPOSITORY: "REMOTE_REPOSITORY",
        artifactregistry_v1.Repository.Mode.STANDARD_REPOSITORY: "STANDARD_REPOSITORY",
        artifactregistry_v1.Repository.Mode.VIRTUAL_REPOSITORY: "VIRTUAL_REPOSITORY",
    }
    repository_object = {
        "identifier": repository.name,
        "title": repository.name.split("/")[-1],
        "properties": {
            "description": repository.description,
            "format": class_format.get(repository.format_),
            "labels": dict(repository.labels),
            "mode": mode_format.get(repository.mode),
            "createdAt": repository.create_time.isoformat(),
            "updatedAt": repository.update_time.isoformat(),
            "kmsKey": repository.kms_key_name,
            "size": repository.size_bytes,
            "satisfiesPhysicalZoneSeparation": repository.satisfies_pzs,
        },
    }
    logger.info(f"Adding repository to Port: {repository_object}")
    await add_entity_to_port(session, REPOSITORY_BLUEPRINT, repository_object)


async def ingest_images(session: aiohttp.ClientSession, image: artifactregistry_v1.DockerImage, repository: artifactregistry_v1.Repository):
    image_object = {
        "identifier": image.name,
        "title": image.name.split("/")[-1],
        "properties": {
            "uri": image.uri,
            "tags": list(image.tags),
            "size": image.image_size_bytes,
            "uploadedAt": image.upload_time.isoformat(),
            "mediaType": image.media_type,
            "buildTime": image.build_time.isoformat(),
            "updatedAt": image.update_time.isoformat(),
        },
        "relations": {
            "repository": repository.name
        }
    }
    logger.info(f"Adding image to Port: {image_object}")
    await add_entity_to_port(session, IMAGE_BLUEPRINT, image_object)

async def fetch_repositories(session: aiohttp.ClientSession, gcp_client: artifactregistry_v1.ArtifactRegistryClient, project_id: str, region: str):
    """A function to fetch repositories from GCR

    Params
    --------------
    session: aiohttp.ClientSession
        The aiohttp session object

    region: str
        The GCR region to fetch repositories from

    Returns
    --------------
    None
    """
    logger.info(f"Fetching repositories from GCR: {region}")
    repository_request = artifactregistry_v1.ListRepositoriesRequest(
        parent=f"projects/{project_id}/locations/{region}",
        page_size=1
    )
    response = gcp_client.list_repositories(request=repository_request)
    for page in response.pages:
        logger.info(f"Fetching page of repositories from GCR: {region}")
        for repository in page.repositories:
            yield repository


async def fetch_images(session: aiohttp.ClientSession, gcp_client: artifactregistry_v1.ArtifactRegistryClient, project_id: str, region: str, repository: artifactregistry_v1.Repository):
    """
    Fetch images from GCR
    """
    logger.info(f"Fetching images from GCR: {region} for repository: {repository.name}")
    image_request = artifactregistry_v1.ListDockerImagesRequest(
        parent=repository.name,
        page_size=1
    )
    response = gcp_client.list_docker_images(request=image_request)
    for page in response.pages:
        logger.info(f"Fetching page of images for repository: {repository.name}")
        for image in page.docker_images:
            yield image

async def main():
    logger.info("Validating GCP regions")
    for region in GCP_REGIONS:
        if region not in ALL_GCR_REGIONS:
            raise ValueError(f"Invalid GCP region: {region}")
    logger.info("Starting Port integration")
    async with aiohttp.ClientSession() as session:
        for region in GCP_REGIONS:
            logger.info(f"Fetching repositories from GCR: {region}")
            async for repository in fetch_repositories(session, artifact_registry_client, ENVIRONMENT.GCP_PROJECT_ID, region):
                await ingest_repositories(session, repository)
                async for image in fetch_images(session, artifact_registry_client, ENVIRONMENT.GCP_PROJECT_ID, region, repository):
                    await ingest_images(session, image, repository)
    logger.info("Finished Port integration")

    


if __name__ == "__main__":
    asyncio.run(main())