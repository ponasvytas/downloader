import asyncio
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from ffmpeg.asyncio import FFmpeg

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from ..config.rinks import RINK_NAMES
from ..models.settings import GameInfo

load_dotenv()


async def download_multiple_files(urls, filepaths):
    tasks = []
    for url, filepath in zip(urls, filepaths):
        tasks.append(download_file(url, filepath))
    await asyncio.gather(*tasks)


async def download_file(url, filepath: Path):
    filepath.parent.mkdir(exist_ok=True, parents=True)

    ffmpeg = (
        FFmpeg()
        .input(url)
        .output(filepath.as_posix(), None, **{"c": "copy", "bsf:a": "aac_adtstoasc"})
    )

    @ffmpeg.on("start")
    def start(command):
        print("Started command downloading")

    # @ffmpeg.on("progress")
    # def on_progress(progress):
    #     print(progress)

    @ffmpeg.on("completed")
    def completed(command):
        print("Finished!", command)

    @ffmpeg.on("terminated")
    def exited(return_code: int):
        print("Oh no!", return_code)

    await ffmpeg.execute()


def round_down_to_nearest_half_hour(dt: datetime) -> datetime:
    # Calculate the number of minutes to subtract to round down
    minutes_to_subtract = dt.minute % 30
    rounded_time = dt - timedelta(
        minutes=minutes_to_subtract, seconds=dt.second, microseconds=dt.microsecond
    )
    return rounded_time


def create_urls(rink: int, start_date: datetime, length: timedelta):
    lb_start_time = round_down_to_nearest_half_hour(start_date)
    end_time = start_date + length

    total_time = end_time - lb_start_time

    intervals = int(total_time / timedelta(hours=0.5)) + 1

    HOST_URL = os.getenv("HOST_URL")
    urls = []
    for i in range(intervals):
        vid_timestamp = lb_start_time + timedelta(hours=0.5) * i
        vid_date = vid_timestamp.strftime("%Y-%m-%d")
        vid_time = vid_timestamp.strftime("%H:%M")
        url = f"{HOST_URL}/{rink}/{vid_date}/{vid_time}/"

        urls.append(url)

    return urls


def download_link(url, filename):
    return f"ffmpeg -i {url} -c copy -bsf:a aac_adtstoasc {filename} && "


def extract_mp4_links(driver: webdriver.Chrome) -> List[str]:
    script = "return window.performance.getEntriesByType('resource');"
    pure_urls = []
    try:
        network_requests = driver.execute_script(script)
    except Exception as e:
        print(f"Error getting network requests: {e}")
        network_requests = []

    pure_urls = [n["name"] for n in network_requests if n["name"].endswith("=m3u8")]

    # for i, n in enumerate(network_requests):
    #     # if ("=m3u8" in n["name"]) or ("playlist.m3u8" in n["name"]):
    #     print(i, n["name"])
    #     if n["name"] not in pure_urls:
    #         print(i, n["name"])
    #         pure_urls.append(n["name"])
    return pure_urls


def find_playlist_links(urls: list[str], download_pano=False):
    TIMEOUT = 5  # in seconds
    DOWNLOADER_USERNAME = os.getenv("DOWNLOADER_USERNAME", "")
    DOWNLOADER_PASSWORD = os.getenv("DOWNLOADER_PASSWORD", "")

    CSS_SELECTOR = "css selector"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--mute-audio")

    pure_urls: List[str] = []
    for part_num, url in enumerate(urls):
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        driver.implicitly_wait(TIMEOUT)
        time.sleep(TIMEOUT)

        # login part
        username_field = driver.find_element(
            by=CSS_SELECTOR,
            value="#ts-body > section > div > form > div:nth-child(1) > div > input",
        )
        username_field.send_keys(DOWNLOADER_USERNAME)

        password_field = driver.find_element(
            by=CSS_SELECTOR,
            value="#ts-body > section > div > form > div:nth-child(2) > div > input",
        )
        password_field.send_keys(DOWNLOADER_PASSWORD)

        submit_button = driver.find_element(
            by=CSS_SELECTOR,
            value="#ts-body > section > div > form > div > button.MuiButton-root",
        )
        submit_button.click()

        # we are now logged in
        # if pano mode is requested, click the button

        if download_pano:
            driver.implicitly_wait(TIMEOUT * 4)
            time.sleep(TIMEOUT * 4)

            _ = driver.execute_script(
                """
                b = document.querySelector('button[aria-label="Panoramic"]'); 
                b.click();
                """
            )

        # Wait for the page to load and network requests to complete, sometimes the links to the m3u8 files take longer to appear
        driver.implicitly_wait(TIMEOUT * 10)
        time.sleep(TIMEOUT * 10)

        urls_for_part = extract_mp4_links(driver)
        print(f"Found {len(urls_for_part)} URLs for part {part_num}")

        pure_urls.extend(urls_for_part)

        driver.quit()

    return pure_urls


def download_game(
    rink: int,
    start_time: str,
    length: float,
    root_path: Path,
    game_name: str,
    download_pano=False,
):
    game_folder = root_path.joinpath(game_name)
    game_folder.mkdir(exist_ok=True, parents=True)

    start_date_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
    game_length = timedelta(hours=length)

    urls = create_urls(rink, start_date=start_date_time, length=game_length)

    print(urls)

    pure_urls = find_playlist_links(urls, download_pano=download_pano)

    # Ensure pure_urls is always a list
    if pure_urls is None:
        pure_urls = []

    vid_info = GameInfo(
        video_name=game_name,
        rink_code=rink,
        rink_name=RINK_NAMES[rink],
        video_start_date=start_date_time.date(),
        video_start_time=start_date_time.time(),
        video_length=length,
        download_urls=pure_urls,
        video_urls=urls,
    )

    with open(game_folder.joinpath("video_info.json"), "w") as f:
        f.write(vid_info.model_dump_json(by_alias=True, indent=2))

    filepaths = []
    for url_num, pure_url in enumerate(pure_urls):
        t = game_folder.joinpath(f"part{url_num}.mp4")
        filepaths.append(t)

    asyncio.run(download_multiple_files(pure_urls, filepaths))
