# Getting started
In this example, you will create a blueprint for `{blueprint}` that ingests {service} Packages from your {service} account into Port. You will then use a Python script to make API calls to {service} REST API to fetch the data from your account.

## Blueprints
Create the following blueprints in Port using the schemas:


### `{Blueprint}`
Python Script for Ingesting {service} {Blueprint} in Port

```json
{}
```

## Running the Python script
First clone the repository and cd into the work directory with:
```bash
$ git clone {https git repo link}
$ cd {repo folder}
```

Install the needed dependencies within the context of a virtual environment with:
```bash
$ virtualenv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```

To ingest your data, you need to populate some environment variables. You can do that by either duplicating the `.example.env` file and renaming the copy as `.env`, then edit the values as needed; or run the commands below in your terminal:

```bash
export PORT_CLIENT_ID=port_client_id
export PORT_CLIENT_SECRET=port_client_secret
export {service}_ACCESS_TOKEN={service}_access_token
```

Then run the script with:
```bash
$ python app.py
```

Each variable required are:
- PORT_CLIENT_ID: Port Client ID
- PORT_CLIENT_SECRET: Port Client secret
- {service}_ACCESS_TOKEN: {service} access token

You can get the {service} token by following the instructions on the [link](https://developer.{service}.com/docs/authentication).