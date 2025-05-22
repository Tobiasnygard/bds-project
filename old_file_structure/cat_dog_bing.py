import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 검색 키워드
keywords = ["dog", "cat"]

# 저장 폴더 및 해상도 설정
save_dir = "./images"
os.makedirs(save_dir, exist_ok=True)

resize_width = 320
resize_height = 240
max_images = 20

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

def search_bing_images(query):
    print(f"[INFO] '{query}' 이미지 검색 시작...")

    # Bing 이미지 검색 URL
    url = f"https://www.bing.com/images/search?q={query}&form=HDRSC2&first=1&tsc=ImageHoverTitle"
    response = requests.get(url, headers=headers, verify=False)

    soup = BeautifulSoup(response.text, "html.parser")
    image_elements = soup.find_all("a", class_="iusc")

    image_urls = []
    for element in image_elements:
        try:
            m = eval(element.get("m"))
            image_url = m["murl"]
            image_urls.append(image_url)
            if len(image_urls) >= max_images:
                break
        except:
            continue

    return image_urls

def download_and_resize_images(query, urls):
    for idx, url in enumerate(urls):
        try:
            # 이미지 요청
            res = requests.get(url, timeout=5, verify=False)

            # ✅ 응답이 이미지인지 확인 (html/text인 경우 방지)
            if "image" not in res.headers.get("Content-Type", ""):
                print(f"[SKIP] 이미지가 아닙니다: {url}")
                continue

            # 이미지 처리 및 저장
            img_data = res.content
            image = Image.open(BytesIO(img_data)).convert("RGB")
            image = image.resize((resize_width, resize_height))
            filename = f"{query}_{idx+1}.jpg"
            filepath = os.path.join(save_dir, filename)
            image.save(filepath, format="JPEG")
            print(f"[OK] 저장됨: {filepath}")

        except Exception as e:
            print(f"[SKIP] 저장 실패 ({url}): {e}")


for kw in keywords:
    links = search_bing_images(kw)
    download_and_resize_images(kw, links)
