#!/usr/bin/python3

# outline_backup_tool/backup.py
import os
import time
import requests
import re
import logging
import json
import http.client # Renamed for clarity, was http in original
import html
from datetime import datetime
import argparse # Import argparse for command-line arguments

# It's better for a library not to configure global logging.
# The application using the library should configure logging.
# We use logging.getLogger(__name__) so the application can control it.
logger = logging.getLogger(__name__)

class OutlineApiClient:
    """
    Handles HTTP communication with the Outline API.
    """
    def __init__(self, hostname, headers):
        """
        Initializes the API client.
        :param hostname: The hostname of the Outline instance (e.g., "wiki.example.com" without https://).
        :param headers: Default headers for API requests, including Authorization.
        """
        self.hostname = hostname # Store hostname for http.client usage
        self.base_url = f"https://{hostname}"
        self.headers = headers
        logger.debug(f"OutlineApiClient initialized for {self.base_url}")

    def call_http_client_post(self, endpoint, payload):
        """
        Makes a POST request using http.client.
        This is specifically for cases where 'requests' might have issues (e.g., S3 redirect).
        """
        conn = None
        full_endpoint_path = endpoint # endpoint is already like /api/...
        logger.debug(f"Making http.client POST to: {self.hostname}{full_endpoint_path} with payload: {payload}")
        try:
            conn = http.client.HTTPSConnection(self.hostname)
            json_data = json.dumps(payload)
            
            # Use the headers provided during initialization
            request_headers = self.headers.copy()

            conn.request("POST", full_endpoint_path, body=json_data, headers=request_headers)
            response = conn.getresponse()
            response_body = response.read()
            logger.debug(f"http.client POST to {full_endpoint_path} - Status: {response.status}, Response snippet: {response_body[:200]}...")
            return response_body.decode('utf-8'), response.status
        except Exception as e:
            logger.error(f"Error in call_http_client_post to {full_endpoint_path} on {self.hostname}: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def request_post(self, endpoint, data):
        """Makes a POST request using the requests library."""
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"Making requests POST to: {url} with data: {data}")
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in POST request to {url}: {e}")
            if e.response is not None:
                logger.error(f"Response status: {e.response.status_code}, content: {e.response.content}")
            raise

    def request_get(self, url_or_endpoint, params=None, stream=False, timeout=30, is_full_url=False):
        """
        Makes a GET request using the requests library.
        Can accept a full URL or just an endpoint.
        """
        if is_full_url:
            url = url_or_endpoint
            # For external URLs (like S3), we might not want to send default headers (e.g., Authorization)
            # However, for direct downloads from Outline, we DO need them.
            # This logic is now handled by the caller deciding which headers to pass.
            current_headers = {} if "s3.amazonaws.com" in url or "storage.googleapis.com" in url else self.headers # Basic heuristic for S3
        else:
            url = f"{self.base_url}{url_or_endpoint}"
            current_headers = self.headers

        logger.debug(f"Making requests GET to: {url} with params: {params}, stream: {stream}, headers: {current_headers}")
        try:
            response = requests.get(url, headers=current_headers, params=params, stream=stream, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in GET request to {url}: {e}")
            if e.response is not None:
                logger.error(f"Response status: {e.response.status_code}, content: {e.response.content}")
            raise


class OutlineBackup:
    """
    A class to backup Outline Wiki instances.
    It handles exporting collections, checking status, downloading, and deleting remote backups.
    """
    def __init__(self, hostname, secret_token, export_format="json", export_dir="outline_backups"):
        """
        Initializes the OutlineBackup client.

        :param hostname: The hostname of your Outline instance (e.g., "wiki.example.com").
        :param secret_token: Your Outline API secret token.
        :param export_format: The format for export ("json" or "outline-markdown").
        :param export_dir: The local directory to save backup files.
        """
        if not hostname:
            raise ValueError("Hostname cannot be empty.")
        if not secret_token:
            raise ValueError("Secret token cannot be empty.")

        self.hostname = hostname.replace("https://", "").replace("http://", "") # Ensure clean hostname
        self.secret_token = secret_token
        self.export_format = export_format
        self.export_dir = export_dir
        
        # Common headers for API calls
        _headers = {
            "Authorization": f"Bearer {self.secret_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        # Initialize the API client
        self.api_client = OutlineApiClient(self.hostname, _headers)

        # API Endpoints (relative paths)
        self.export_endpoint = "/api/collections.export_all"
        self.status_endpoint = "/api/fileOperations.info"
        self.download_redirect_endpoint = "/api/fileOperations.redirect"
        self.delete_endpoint = "/api/fileOperations.delete"

        # Ensure export directory exists
        os.makedirs(self.export_dir, exist_ok=True)
        logger.info(f"OutlineBackup client initialized for {self.hostname}. Backups will be saved to {self.export_dir}")

    def export_all_collections(self):
        """Initiates the export of all collections."""
        logger.info(f"Requesting export for {self.hostname} in '{self.export_format}' format.")
        payload = {"format": self.export_format}
        response_data = self.api_client.request_post(self.export_endpoint, payload)
        
        if response_data and response_data.get('data') and response_data['data'].get('fileOperation'):
            file_operation_id = response_data['data']['fileOperation']['id']
            logger.info(f"Export initiated successfully. File operation ID: {file_operation_id}")
            return file_operation_id
        else:
            logger.error(f"Failed to initiate export. Unexpected response structure: {response_data}")
            raise Exception("Failed to initiate export: Unexpected response structure from API.")

    def check_export_status(self, file_operation_id):
        """Checks the status of an ongoing export operation."""
        logger.info(f"Checking status for file operation ID: {file_operation_id}")
        payload = {"id": file_operation_id}
        max_retries = 12 * 6 # e.g., 6 minutes if sleep is 10s (was 12*5)
        retries = 0
        while retries < max_retries:
            retries += 1
            try:
                response_data = self.api_client.request_post(self.status_endpoint, payload)
                state = response_data.get('data', {}).get('state')
                error_message = response_data.get('data', {}).get('error')
                
                logger.info(f"Attempt {retries}/{max_retries}: Export file ID {file_operation_id}, state: {state}.")
                
                if state == 'complete':
                    logger.info(f"Export {file_operation_id} completed successfully.")
                    return True
                elif state == 'failed':
                    logger.error(f"File export {file_operation_id} failed. Error: {error_message}")
                    raise Exception(f"File export failed: {error_message or 'Unknown reason'}")
                elif not state:
                    logger.error(f"Could not determine export state for {file_operation_id}. Response: {response_data}")
                    raise Exception("Could not determine export state from API response.")
                
                time.sleep(10)
            except Exception as e:
                logger.error(f"Error checking status for {file_operation_id} (attempt {retries}): {e}")
                if retries >= max_retries:
                    raise Exception(f"Failed to get export status for {file_operation_id} after multiple retries.") from e
                time.sleep(10)
        
        logger.error(f"Export {file_operation_id} did not complete within the allocated time.")
        raise Exception(f"Export {file_operation_id} timed out.")


    def get_s3_download_link(self, file_operation_id):
        """
        Gets the S3 download link by POSTing to the redirect endpoint and parsing the HTML response.
        Uses http.client via the API client.
        """
        logger.info(f"Getting S3 download link for file operation ID: {file_operation_id}")
        payload = {"id": file_operation_id}
        
        # This specific call uses the http.client wrapper in OutlineApiClient
        html_response, status_code = self.api_client.call_http_client_post(self.download_redirect_endpoint, payload)

        if status_code not in (200, 302):
             logger.warning(f"Unexpected status code {status_code} when trying to get S3 redirect link. Response snippet: {html_response[:500]}")
        
        logger.debug(f"Raw HTML response for S3 link retrieval (first 500 chars): {html_response[:500]}")
        
        match = re.search(r'href="(.*?)"', html_response)
        if match:
            download_link = html.unescape(match.group(1))
            logger.info(f"Successfully extracted S3 download link: {download_link}")
            return download_link
        else:
            logger.error(f"Could not extract S3 download link from response. Status: {status_code}, Response snippet: {html_response[:500]}")
            raise Exception("Could not extract S3 download link from API response.")

    def download_from_url(self, download_url, save_path):
        """Downloads a file from a given URL (e.g., an S3 link) with progress."""
        logger.info(f"Downloading from URL: {download_url} to {save_path}")
        try:
            # For S3 links, custom headers (like Authorization) are usually not needed.
            # The api_client.request_get handles this by not sending default headers for known cloud storage URLs.
            response = self.api_client.request_get(download_url, stream=True, timeout=(10, 300), is_full_url=True)
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            chunk_size = 8192

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0:
                            percentage = (downloaded_size / total_size) * 100
                            progress_msg = f"\rDownloading... {downloaded_size/1024/1024:.2f}MB / {total_size/1024/1024:.2f}MB ({percentage:.2f}%)"
                        else:
                            progress_msg = f"\rDownloading... {downloaded_size/1024/1024:.2f}MB"
                        print(progress_msg.ljust(80), end='', flush=True)
            print("\nDownload from URL complete.")
            logger.info(f"File downloaded successfully from URL to {save_path}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download from URL {download_url}: {e}")
            if os.path.exists(save_path):
                try:
                    os.remove(save_path)
                    logger.info(f"Cleaned up partially downloaded file: {save_path}")
                except OSError as oe:
                    logger.error(f"Error cleaning up partial file {save_path}: {oe}")
            raise

    def download_direct_backup_file(self, file_operation_id, save_path):
        """
        Downloads the backup file directly using a GET request to the redirect endpoint.
        """
        logger.info(f"Attempting direct download for file operation ID: {file_operation_id} to {save_path}")
        payload = {"id": file_operation_id}

        try:
            # This GET request goes to our Outline instance, so it needs Authorization.
            # The api_client.request_get will use its default headers.
            response = self.api_client.request_get(self.download_redirect_endpoint, params=payload, stream=True, timeout=(10,300))

            total_size = int(response.headers.get('content-length', 0))
            content_type = response.headers.get('Content-Type', '')
            logger.info(f"Direct download: Content-Type: {content_type}, Content-Length: {total_size}")

            if 'text/html' in content_type and total_size < 1024*10:
                html_content_snippet = response.text[:500]
                logger.warning(f"Direct download received HTML content. This might be an S3 setup. HTML snippet: {html_content_snippet}")
                raise Exception("Direct download endpoint returned HTML; this instance might be S3-backed. Try 's3' storage_type.")

            downloaded_size = 0
            chunk_size = 8192

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0:
                            percentage = (downloaded_size / total_size) * 100
                            progress_msg = f"\rDirect downloading... {downloaded_size/1024/1024:.2f}MB / {total_size/1024/1024:.2f}MB ({percentage:.2f}%)"
                        else:
                            progress_msg = f"\rDirect downloading... {downloaded_size/1024/1024:.2f}MB"
                        print(progress_msg.ljust(80), end='', flush=True)
            print("\nDirect download complete.")
            logger.info(f"File directly downloaded successfully to {save_path}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Direct download failed for {file_operation_id}: {e}")
            if e.response is not None:
                content_type = e.response.headers.get('Content-Type', '')
                if 'text/html' in content_type:
                    logger.warning("Direct download failed and received HTML. This instance might be S3-backed. Try 's3' storage_type.")
                    logger.error(f"Response content snippet: {e.response.text[:500]}")
            if os.path.exists(save_path):
                try:
                    os.remove(save_path)
                    logger.info(f"Cleaned up partially downloaded file: {save_path}")
                except OSError as oe:
                    logger.error(f"Error cleaning up partial file {save_path}: {oe}")
            raise

    def delete_remote_backup(self, file_operation_id):
        """Deletes the file operation (and associated backup file) on the Outline server."""
        logger.info(f"Requesting deletion of remote file operation ID: {file_operation_id}")
        payload = {"id": file_operation_id}
        try:
            response_data = self.api_client.request_post(self.delete_endpoint, payload)
            if response_data.get('success'):
                logger.info(f"File operation {file_operation_id} deleted successfully on server.")
                return True
            else:
                logger.warning(f"Failed to delete file operation {file_operation_id} on server. Response: {response_data}")
                return False
        except Exception as e:
            logger.error(f"Error deleting file operation {file_operation_id}: {e}")
            return False

    def run_backup(self, storage_type="direct", delete_after_download=True):
        """
        Runs the full backup process: export, check status, download, and optionally delete.
        """
        file_operation_id = None
        downloaded_file_path = None
        try:
            logger.info(f"Starting backup run for {self.hostname} with storage_type='{storage_type}'.")
            file_operation_id = self.export_all_collections()

            if self.check_export_status(file_operation_id):
                logger.info("Export process on server completed successfully.")

                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                safe_hostname = re.sub(r'[^\w.-]', '_', self.hostname)
                file_extension = ".zip" 
                filename = f'outline_{safe_hostname}_{self.export_format}_{timestamp}{file_extension}'
                save_path = os.path.join(self.export_dir, filename)

                logger.info(f"Preparing to download backup to: {save_path}")

                if storage_type == "s3":
                    logger.info("Using S3 download strategy.")
                    s3_download_link = self.get_s3_download_link(file_operation_id)
                    self.download_from_url(s3_download_link, save_path)
                elif storage_type == "direct":
                    logger.info("Using direct download strategy.")
                    self.download_direct_backup_file(file_operation_id, save_path)
                else:
                    logger.error(f"Unknown storage_type: {storage_type}. Choose 'direct' or 's3'.")
                    raise ValueError(f"Unknown storage_type: {storage_type}. Choose 'direct' or 's3'.")

                logger.info(f"Backup file successfully downloaded to {save_path}")
                downloaded_file_path = save_path
                return downloaded_file_path
            else:
                logger.error("Export did not complete successfully (status check returned False without exception).")
                raise Exception("Export did not complete successfully (unexpected status check result).")

        except Exception as e:
            logger.error(f"An error occurred during the backup process for {self.hostname}: {e}")
            return None
        finally:
            if file_operation_id and delete_after_download and downloaded_file_path:
                logger.info(f"Attempting to delete remote file operation {file_operation_id} as download was successful.")
                if self.delete_remote_backup(file_operation_id):
                    logger.info(f"Remote backup artifact {file_operation_id} cleaned up successfully.")
                else:
                    logger.warning(f"Failed to clean up remote backup artifact {file_operation_id}.")
            elif file_operation_id and delete_after_download and not downloaded_file_path:
                 logger.warning(f"Skipping deletion of remote file operation {file_operation_id} because download failed or was interrupted.")
            elif file_operation_id and not delete_after_download:
                 logger.info(f"Skipping deletion of remote file operation {file_operation_id} as per configuration (delete_after_download=False).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backup tool for Outline Wiki instances.")
    parser.add_argument(
        "--hostname",
        required=True,
        help="Hostname of your Outline instance (e.g., wiki.example.com). Can also be set via OUTLINE_HOSTNAME environment variable."
    )
    parser.add_argument(
        "--token",
        required=True,
        help="Your Outline API secret token. Can also be set via OUTLINE_TOKEN environment variable."
    )
    parser.add_argument(
        "--format",
        default="json",
        choices=["json", "html", "outline-markdown"],
        help="Export format (default: json)."
    )
    parser.add_argument(
        "--dir",
        default="outline_backups",
        help="Local directory to save backup files (default: outline_backups)."
    )
    parser.add_argument(
        "--storage-type",
        default="direct",
        choices=["direct", "s3"],
        help="Storage type of your Outline instance. 'direct' for local server storage, 's3' for S3-backed storage (default: direct)."
    )
    parser.add_argument(
        "--no-delete",
        action="store_true",
        help="Do not delete the backup from the Outline server after successful download."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging."
    )

    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    hostname = args.hostname
    token = args.token
    
    logger.info(f"Starting backup from command line for Outline instance: {hostname}")
    logger.info(f"Export format: {args.format}, Storage type: {args.storage_type}")
    logger.info(f"Backups will be saved to: {os.path.abspath(args.dir)}")
    if args.no_delete:
        logger.info("Remote backup will NOT be deleted after download.")
    else:
        logger.info("Remote backup WILL be deleted after successful download.")

    try:
        backup_client = OutlineBackup(
            hostname=hostname,
            secret_token=token,
            export_format=args.format,
            export_dir=args.dir
        )

        delete_after = not args.no_delete
        downloaded_file = backup_client.run_backup(storage_type=args.storage_type, delete_after_download=delete_after)

        if downloaded_file:
            logger.info(f"Backup process completed. File saved to: {downloaded_file}")
        else:
            logger.error("Backup process failed.")
            # import sys
            # sys.exit(1) 

    except ValueError as ve:
        logger.error(f"Configuration error: {ve}")
        # import sys
        # sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=args.debug)
        # import sys
        # sys.exit(1)

