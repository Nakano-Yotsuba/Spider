import os
import re
import json
import time
import requests
from concurrent.futures import ThreadPoolExecutor

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0.0.0 Safari/537.36"
}


def check_directory(directory) -> None:
    if not os.path.exists(directory):
        os.mkdir(directory)


def get_image_name(url: str) -> str:
    try:
        return url.split("_")[1]
    except IndexError:
        return re.findall(r"/([^/]+)$", url)[0]


class Spider:
    def __init__(self):
        self.url = "https://api-os-takumi-static.hoyoverse.com/content_v2_user/app/5fcd2aa439ca4aea/getContentList"
        self.params = {
            "iPageSize": "40",
            "iPage": "1",
            "sLangKey": "en-us",
            "iChanId": "497",
        }
        self.session = requests.Session()
        self.images_urls = []

    def get_images_urls(self) -> list:
        print("start getting urls...")
        start = time.time()
        for page in range(1, 12):
            self.params['iPage'] = str(page)
            response = self.session.get(url=self.url, headers=headers, params=self.params).json()
            data_list = response['data']['list']
            for data in data_list:
                data = json.loads(data['sExt'])
                images = data['497_0']
                for image in images:
                    self.images_urls.append(image['url'])
        end = time.time()
        print(f"urls got in {end - start} seconds, {len(self.images_urls)} items in total.")
        print("--------------------------------------------------------------------------------")
        return self.images_urls

    def single_download(self, url: str) -> None:
        file_name = get_image_name(url)
        content = self.session.get(url=url, headers=headers).content
        if os.path.isfile(f"./image/{file_name}"):
            print(f"image {file_name} already existed!!!")
            return
        with open(f"./images/{file_name}", "wb") as file:
            file.write(content)
        print(f"{file_name} done.")

    def multithreaded_download(self, url_list):
        start = time.time()
        check_directory("images")
        with ThreadPoolExecutor(max_workers=20) as pool:
            pool.map(self.single_download, url_list)
        end = time.time()
        print(f"Process finished in {end - start} seconds, {(end - start) / 60} minutes.")


if __name__ == '__main__':
    spider = Spider()
    urls = spider.get_images_urls()
    spider.multithreaded_download(urls)
    spider.session.close()
