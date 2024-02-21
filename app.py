from flask import Flask, render_template, request, redirect, url_for, send_file
from urllib.parse import quote
import os
from werkzeug.utils import secure_filename
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__

app = Flask(__name__)

# Replace with your Azure Storage account details
account_name = 'storageapp3375'
account_key = 'aqmoTEaB8Jt2cDs6BVCuSRg82ru6ISqU1DRNz01bGIp3txBOa94hlTWIYbtp5X1+Ybe2KYuaXql++AStb+Snlw=='
container_name = 'files'

# Initialize the Azure Blob Storage client
connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
blob_service_client = BlobServiceClient.from_connection_string(connection_string)


@app.route('/')
def index():
    files = list_files()
    return render_template('index.html', files=files)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    azure_blob_name = secure_filename(file.filename)
    upload_file_to_azure(file, container_name, azure_blob_name)

    return redirect(url_for('index'))


@app.route('/download/<file_name>')
def download_file(file_name):
    local_file_path = os.path.join('temp', quote(file_name))
    download_file_from_azure(file_name, container_name, local_file_path)
    # download_file_from_azure(file_name, container_name, local_file_path)

    return send_file(local_file_path, as_attachment=True)


def list_files():
    container_client = blob_service_client.get_container_client(container_name)
    blobs = [blob.name for blob in container_client.list_blobs()]
    return blobs


def upload_file_to_azure(file, container_name, azure_blob_name):
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(azure_blob_name)

    try:
        blob_client.upload_blob(file)
    except Exception as e:
        print(f"Error uploading file to Azure Blob Storage: {str(e)}")


def download_file_from_azure(file_name, container_name, local_file_path):
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(file_name)

    try:
        # Ensure the 'temp' directory exists
        os.makedirs('temp', exist_ok=True)

        # Use os.path.join for constructing the local file path
        local_file_path = os.path.join('temp', quote(file_name))

        with open(local_file_path, 'wb') as file:
            data = blob_client.download_blob()
            data.readinto(file)
    except Exception as e:
        print(f"Error downloading file from Azure Blob Storage: {str(e)}")


if __name__ == '__main__':
    app.run(debug=True)
