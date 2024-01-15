# =============================================================================
# Project: HNI Manga Downloader
# Author: Michael Sumaya
# Manga Source - https://hni-scantrad.com/lel/series/hajime-no-ippo/
# =============================================================================
import link_scrapper
import link_downloader
import pathlib
import threading
import time

CHAPTER_VOLUME_SEP = "_"
MAX_THREADS = 10

HOME_URL = "https://hni-scantrad.com/lel/series/hajime-no-ippo/"
SAVE_FOLDER = pathlib.Path("HNI")
DL_NEW_INDEX = True
SILENT_DOWNLOAD = True
DL_PAUSE = 10

# =============================================================================


def thread_checker(thread_list):
    for dl_thread in thread_list:
        dl_thread.join()
    print(f"Download group completed... Continuing after {DL_PAUSE} seconds")
    time.sleep(DL_PAUSE)


scrapper = link_scrapper.HNI_Link_Scrapper(
    home_url=HOME_URL,
    save_folder=SAVE_FOLDER,
)
links_list = scrapper.get_links(download_new=DL_NEW_INDEX)
dl_tool = link_downloader.HNI_Downloader(save_folder=SAVE_FOLDER)
dl_threads = []
is_downloaded = False


# Downloader
if links_list:
    for volume in links_list:
        print(f"Volume: {volume['volume']}")
        for chapter in volume["links"]:
            for key, value in chapter.items():
                # File check
                url_split = str(value).split("/")
                filename = pathlib.Path(
                    SAVE_FOLDER,
                    url_split[-3]
                    + CHAPTER_VOLUME_SEP
                    + url_split[-2]
                    + ".zip",
                )
                filepath = pathlib.Path(
                    SAVE_FOLDER,
                    url_split[-3],
                    url_split[-2],
                )
                if pathlib.Path.exists(filename):
                    if not SILENT_DOWNLOAD:
                        print(f"{filename} already downloaded.")
                    is_downloaded = True
                elif pathlib.Path.exists(filepath):
                    if not SILENT_DOWNLOAD:
                        print(f"{filepath} already exists.")
                    is_downloaded = True
                else:
                    is_downloaded = False

                if not is_downloaded:
                    # Enable Multithread downloader
                    args = []
                    args.append(value)
                    dl_thread = threading.Thread(
                        target=dl_tool.dl_chapter,
                        args=args,
                    )
                    dl_threads.append(dl_thread)
                    dl_thread.start()
                    if len(dl_threads) == MAX_THREADS:
                        thread_checker(dl_threads)
                        dl_threads = []

# Cleanup
if len(dl_threads) > 0:
    thread_checker(dl_threads)
    dl_threads = []

# Unzip
dl_tool.unzip_all()

print("Download completed.")
