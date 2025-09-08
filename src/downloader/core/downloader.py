import asyncio
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv
from ffmpeg_asyncio import FFmpeg, Progress
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from ..models.settings import GameInfo
from ..config.rinks import RINK_NAMES

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

    @ffmpeg.on("progress")
    def on_progress(progress: Progress):
        print(progress)

    @ffmpeg.on("completed")
    def completed():
        print("Finished!")

    @ffmpeg.on("terminated")
    def exited(return_code: int):
        print("Oh no!")

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


def download_game(
    rink: int,
    start_time: str,
    length: float,
    root_path: Path,
    game_name: str,
    download_pano=False,
):
    TIMEOUT = 5  # in seconds
    DOWNLOADER_USERNAME = os.getenv("DOWNLOADER_USERNAME", "")
    DOWNLOADER_PASSWORD = os.getenv("DOWNLOADER_PASSWORD", "")

    game_folder = root_path.joinpath(game_name)
    game_folder.mkdir(exist_ok=True, parents=True)

    start_date_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
    game_length = timedelta(hours=length)

    urls = create_urls(rink, start_date=start_date_time, length=game_length)

    print(urls)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--mute-audio")

    CSS_SELECTOR = "css selector"

    links = []
    pure_urls = []
    file_parts = []
    for part_num, url in enumerate(urls):
        # create a session
        # go to the url
        # create script that will return network requests
        networkScript = """
        let performance = window.performance;
        let network = performance.getEntries();
        return network;
        """

        driver = webdriver.Chrome(options=chrome_options)

        driver.get(url)  # https://{domain_url}/153/2024-09-07/18:30/
        driver.implicitly_wait(TIMEOUT)
        time.sleep(TIMEOUT)

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

        if download_pano:
            driver.implicitly_wait(TIMEOUT * 4)
            time.sleep(TIMEOUT * 4)

            # # find pano button and click it
            # _ = driver.execute_script(
            #     """
            #     b = document.querySelector("#auto-pano-select > a[data-testid='pano-button'] > img");
            #     b.click();
            #     """
            # )
            _ = driver.execute_script(
                """
                b = document.querySelector('button[aria-label="Panoramic"]'); 
                b.click();
                """
            )

        driver.implicitly_wait(TIMEOUT * 4)
        time.sleep(TIMEOUT * 4)

        print("About to run the script...")
        network_requests = driver.execute_script(
            "return window.performance.getEntriesByType('resource');"
        )

        print(f"Part {part_num}")
        file_name = f"part{part_num}.mp4"
        for i, n in enumerate(network_requests):
            temp_links = []
            if ("=m3u8" in n["name"]) or ("playlist.m3u8" in n["name"]):
                if n["name"] not in pure_urls:
                    print(i, n["name"])
                    pure_urls.append(n["name"])
                    links.append(download_link(n["name"], file_name))

        # if download_pano:
        #     file_parts = file_parts[1::2]
        #     pure_urls = pure_urls[1::2]
        #     links = links[1::2]

        # file_parts.append(f"file '{file_name}'\n")

    # with open("file_parts.txt", "w") as f:
    #     f.writelines(file_parts)

    # with open("pure_urls.txt", "w") as f:
    #     f.writelines(("\n").join(pure_urls))

    # with open("auto_links.txt", "w") as f:
    #     f.writelines(links)
    #     f.write("ffmpeg -f concat -i file_parts.txt -c copy full_video.mp4")

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
