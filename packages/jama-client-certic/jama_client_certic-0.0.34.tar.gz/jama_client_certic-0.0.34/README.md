# Jama client library

## Installation

Use pip to install:

    pip install jama-client-CERTIC

## Quick start

    from jama_client import Client, ServiceError
    client = Client("https://acme.tld/rpc/", "secretapikeyhere")
    try:
        file_id = client.upload("/path/to/some/file.jpg")
        collection_id = client.add_collection("title of the collection")
        client.add_file_to_collection(file_id, collection_id)
    except ServiceError as e:
        print(e.message)

Refer to your local Jama instance endpoint for complete API documentation.
