# =============================================================================
# LINK DOWNLOADER - for HNI Manga Downloader
# Author: Michael Sumaya
# =============================================================================
import io
import pathlib
import requests
import time
import zipfile as z


class HNI_Downloader():

    WRITE_BINARY = "w+b"
    CHAPTER_VOLUME_SEP = "_"
    ZIP_EXT = ".zip"
    THIS_BUFFER_SIZE = io.DEFAULT_BUFFER_SIZE * 10

    def __init__(
            self,
            save_folder: str = "."
    ) -> None:
        self.save_folder = save_folder
        pass

    def dl_chapter(
            self,
            url_link: str
    ):
        if url_link:
            print(f"Downloading... {url_link}")
            req = requests.get(url_link)
            try:
                req.raise_for_status()
            except Exception as error:
                print(f"{error}")
                return None

            url_split = url_link.split("/")
            filename = pathlib.Path(
                self.save_folder,
                url_split[-3]
                + self.CHAPTER_VOLUME_SEP
                + url_split[-2]
                + self.ZIP_EXT)
            self.dl_file(
                req=req,
                save_as_file=filename,
            )

    def dl_file(
            self,
            req: requests.Response,
            save_as_file: str,
    ) -> bool:
        """Download file from requests module to local file"""
        try:
            with open(file=save_as_file, mode=self.WRITE_BINARY) as downloaded_file:
                for buffer in req.iter_content(self.THIS_BUFFER_SIZE):
                    downloaded_file.write(buffer)
            # Wait for file to be saved?
            while not pathlib.Path.exists(save_as_file):
                time.sleep(0.5)
            if pathlib.Path.exists(save_as_file):
                print(f"File saved: {pathlib.Path.absolute(save_as_file)}")
                return True
            else:
                print(
                    f"Download to file failed: {pathlib.Path.absolute(save_as_file)}")
                return False
        except Exception as error:
            print(f"Download to file failed: {error}")
            return False

    def unzip_all(self):
        """Extract all ZIP files"""
        for file in pathlib.Path(self.save_folder).glob("*.zip"):
            if file.is_file():
                zipfile = str(file).split("/")[1].split(".")
                volume_folder, chapter_folder = zipfile[0].split(
                    self.CHAPTER_VOLUME_SEP
                )

                source_file = pathlib.Path(file)
                target_path = pathlib.Path(
                    self.save_folder,
                    volume_folder,
                    chapter_folder
                )
                with z.ZipFile(source_file) as zipped_file:
                    zipped_file.extractall(target_path)
                    zipped_file.close
                print("Chapter %s - %s saved in: %s" %
                      (volume_folder,
                       chapter_folder,
                       pathlib.Path.absolute(target_path)))
                # Delete file
                if pathlib.Path.exists(source_file):
                    pathlib.Path(source_file).unlink()
                    print(f"Deleted ZIP file: {source_file}")
