# Getting started
In this example, you will create a blueprint for `gcrImage` and `gcrRepository` that ingests GCR images from your GCR account into Port. You will then use a Python script to make API calls to GCR REST API to fetch the data from your account.

## Blueprints
Create the following blueprints in Port using the schemas:

### Repository
```json
{
  "identifier": "gcrRepository",
  "description": "This blueprint represents a Container Registry Repository in our software catalog",
  "title": "GCR Repository",
  "icon": "GoogleCloudPlatform",
  "schema": {
    "properties": {
      "description": {
        "title": "Description",
        "type": "string",
        "description": "Repository Description"
      },
      "format": {
        "title": "Format",
        "type": "string",
        "description": "Package Format",
        "enum": [
          "FORMAT_UNSPECIFIED",
          "DOCKER",
          "MAVEN",
          "NPM",
          "APT",
          "YUM",
          "PYTHON",
          "KFP",
          "GO"
        ]
      },
      "labels": {
        "title": "Labels",
        "type": "object",
        "description": "Labels with user-defined metadata"
      },
      "mode": {
        "title": "Mode",
        "description": "The mode configures the repository to serve artifacts from different sources.",
        "type": "string",
        "enum": [
          "MODE_UNSPECIFIED",
          "STANDARD_REPOSITORY",
          "VIRTUAL_REPOSITORY",
          "REMOTE_REPOSITORY"
        ]
      },
      "createdAt": {
        "title": "Created At",
        "description": "Time repository was created",
        "type": "string",
        "format": "date-time"
      },
      "updatedAt": {
        "title": "Updated At",
        "description": "Last time repository was updated",
        "type": "string",
        "format": "date-time"
      },
      "kmsKeyName": {
        "title": "KMS Key Name",
        "description": "The Cloud KMS resource name of the customer managed encryption key that's used to encrypt the contents of the Repository",
        "type": "string"
      },
      "size": {
        "title": "Size",
        "description": "Repository size in bytes",
        "type": "number"
      },
      "satisfiesPhysicalZoneSeparation": {
        "title": "Satisfies Physical Zone Separation",
        "description": "Whether the repository satisfies physical zone separation.",
        "type": "boolean"
      }
    },
    "required": []
  },
  "mirrorProperties": {},
  "calculationProperties": {},
  "aggregationProperties": {},
  "relations": {}
}
```

### Image

```json
{
  "identifier": "gcrImage",
  "description": "This blueprint represents a Container Registry Image in our software catalog",
  "title": "GCR Image",
  "icon": "GoogleCloudPlatform",
  "schema": {
    "properties": {
      "uri": {
        "title": "URI",
        "type": "string",
        "description": "Image URI"
      },
      "tags": {
        "title": "Tags",
        "type": "array",
        "description": "Tags attached to this image."
      },
      "size": {
        "title": "Size",
        "description": "Image size in bytes",
        "type": "number"
      },
      "uploadedAt": {
        "title": "Uploaded At",
        "description": "Time image was uploaded",
        "type": "string",
        "format": "date-time"
      },
      "mediaType": {
        "title": "Media Type",
        "description": "Media type of this image",
        "type": "string"
      },
      "buildTime": {
        "title": "Build Time",
        "description": "Time image was built",
        "type": "string",
        "format": "date-time"
      },
      "updatedAt": {
        "title": "Updated At",
        "description": "Last time image was updated",
        "type": "string",
        "format": "date-time"
      }
    },
    "required": []
  },
  "mirrorProperties": {},
  "calculationProperties": {},
  "aggregationProperties": {},
  "relations": {
    "repository": {
      "title": "Repository",
      "description": "Repository this image is attached to",
      "target": "gcrRepository",
      "many": false,
      "required": true
    }
  }
}
```

## Running the Python script
First clone the repository and cd into the work directory with:
```bash
$ git clone https://github.com/port-labs/example-gcr-images.git
$ cd example-gcr-images
```

Install the needed dependencies within the context of a virtual environment with:
```bash
$ virtualenv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```

To ingest your data, you need to populate some environment variables. You should do that by duplicating the `.example.env` file and renaming the copy as `.env`, then edit the values as needed; or run the commands below in your terminal:

```bash
export PORT_CLIENT_ID=port_client_id
export PORT_CLIENT_SECRET=port_client_secret
export GCP_REGIONS=region1,region2,region3
export GCP_PROJECT_ID=my-project-id
```

In addition, you must set up your GCP credentials. You can do that by following the instructions on the [ADC documentation page](https://cloud.google.com/docs/authentication/provide-credentials-adc). Alternatively, you can use any of the authentication methods outlined in the [Python Client Library documentation](https://github.com/googleapis/google-api-python-client/blob/main/docs/auth.md).

Then run the script with:
```bash
$ python app.py
```

Each variable required are:
- PORT_CLIENT_ID: Port Client ID
- PORT_CLIENT_SECRET: Port Client secret
- GCP_REGIONS: Comma separated list of GCP regions to fetch images from. If not set, defaults to "us-east1,us-central1".
- GCP_PROJECT_ID: GCP project ID

List of all possible regions you can set for `GCP_REGIONS`:
- asia-east1
- asia-east2
- asia-northeast1
- asia-northeast2
- asia-northeast3
- asia-south1
- asia-south2
- asia-southeast1
- asia-southeast2
- australia-southeast1
- australia-southeast2
- europe-central2
- europe-north1
- europe-southwest1
- europe-west1
- europe-west2
- europe-west3
- europe-west4
- europe-west6
- europe-west8
- europe-west9
- europe-west10
- europe-west12
- us-west1
- us-west2
- us-west3
- us-west4
- us-central1
- us-east1
- us-east4
- us-east5
- us-south1
- northamerica-northeast1
- northamerica-northeast2
- southamerica-east1
- southamerica-east2
- me-central1
- me-central2
- me-west1