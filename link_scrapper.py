# =============================================================================
# LINK SCRAPPER - for HNI Manga Downloader
# Author: Michael Sumaya
# =============================================================================
import bs4
import io
import pathlib
import requests
import time

WRITE_BINARY = "wb"
THIS_BUFFER_SIZE = io.DEFAULT_BUFFER_SIZE * 10


class HNI_Link_Scrapper():
    """Class for downloading the links from source website\n
    Returns -> list\n
    in the following format:\n
    [\n
        {\n
            "volume": volume_number,\n
            "links":\n
                [\n
                    {\n
                        chapter_num: dl_link\n
                    },\n
                    ...\n
                ]\n
        },\n
        ...\n
    ]\n
    """

    # BS4 parsers
    BS_FEATURE = "html.parser"
    VOL_GROUP_SEP = "div[class = 'list'] > div[class = 'group']"
    VOL_SEP = "div[class='group'] > div[class = 'title']"
    LINK_SEP = "div[class='icon_wrapper fleft small'] > a"

    def __init__(
            self,
            home_url: str,
            save_folder: str = ".",
    ) -> None:
        self.home_url = home_url
        self.save_folder = save_folder
        self.local_home_file = pathlib.Path(save_folder, "hni_home.html")

    def get_links(
        self,
        download_new: bool = False
    ) -> any:
        """Returns the url list if successful"""
        if download_new:
            print(f"Downloading new file from...{self.home_url}")
            res = requests.get(self.home_url)
            try:
                res.raise_for_status()
            except Exception as error:
                print(f"{error}")
                return None

            self.dl_file(req=res, save_as_file=self.local_home_file)

        if pathlib.Path.exists(self.local_home_file):
            with open(self.local_home_file) as html_file:
                html_src = bs4.BeautifulSoup(
                    markup=html_file, features=self.BS_FEATURE)
        else:
            print("File not found. Please redownload.")
            return None

        if html_src:
            # Volume Groups
            hni_groups = html_src.select(self.VOL_GROUP_SEP)
            volume_list = []
            for group in hni_groups:
                # Volume Number
                hni_volumes = group.select(self.VOL_SEP)
                for volume in hni_volumes:
                    volume_text = str(volume.getText()).split()
                    volume_num = volume_text[1]
                # Chapter Links
                link_list = []
                hni_links = group.select(self.LINK_SEP)
                for link in hni_links:
                    dl_link = link.get("href")
                    link_split = dl_link.split("/")
                    chapter_num = str(link_split[-2]).strip()
                    link_list.append(
                        {
                            chapter_num: dl_link,
                        }
                    )
                volume_list.append(
                    {
                        "volume": volume_num,
                        "links": link_list,
                    }
                )
            return volume_list

    def dl_file(
            self,
            req: requests.Response,
            save_as_file: str,
    ) -> bool:
        """Download file from requests module to local file"""
        try:
            with open(file=save_as_file, mode=WRITE_BINARY) as downloaded_file:
                for buffer in req.iter_content(THIS_BUFFER_SIZE):
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
