import requests
import zipfile
import os
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class DownloadTask:
    def __init__(self, data_dir):
        self.zip_path = Path(data_dir)
        self.extract_dir = self.zip_path.parent

        self.extract_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"Using directory: {self.extract_dir}")

    def download_file(self, url):
        logging.info(f"Starting download from: {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(self.zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        logging.info(f"File downloaded to: {self.zip_path}")

    def unzip_file(self):
        logging.info(f"Starting extraction to: {self.extract_dir}")
        with zipfile.ZipFile(self.zip_path, "r") as zip_ref:
            zip_ref.extractall(self.extract_dir)
        logging.info("Extraction completed")

    def execute(self):
        try:
            kaggle_url = "https://www.kaggle.com/api/v1/datasets/download/aungpyaeap/supermarket-sales"
            self.download_file(kaggle_url)
            self.unzip_file()
            return "Successfully downloaded and unzipped the dataset"

        except Exception as e:
            logging.error(f"Error occurred: {str(e)}")
            if os.path.exists(self.zip_path):
                os.remove(self.zip_path)
                logging.info(f"Cleaned up zip file: {self.zip_path}")
            raise e


if __name__ == "__main__":
    path = os.path.expanduser("~/Downloads/etl/archive.zip")
    task = DownloadTask(path)
    result = task.execute()
    print(result)
