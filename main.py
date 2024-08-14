from pathlib import Path
import requests
import threading
import multiprocessing
import time
import asyncio
import os
import argparse

def download_image(url, image_path):
    start_time = time.time()
    response = requests.get(url, stream=True)
    filename = os.path.basename(url)
    with open(os.path.join(str(image_path), filename), "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    end_time = time.time() - start_time
    print(f"Загрузка {filename} завершена за {end_time:.2f} секунд")

async def download_image_async(url, image_path):
    start_time = time.time()
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, lambda url: requests.get(url, stream=True), url)
    filename = os.path.basename(url)
    with open(os.path.join(str(image_path), filename), "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    end_time = time.time() - start_time
    print(f"Загрузка {filename} завершена за {end_time:.2f} секунд")

async def download_image_asyncio(urls, image_path, chunk_size=10):
    for i in range(0, len(urls), chunk_size):
        chunk_urls = urls[i:i + chunk_size]
        await download_images_async(chunk_urls, image_path)
    end_time = time.time()
    print(f"Загрузка завершена за {end_time:.2f} секунд")

async def download_images_async(urls, image_path):
    tasks = []
    for url in urls:
        task = asyncio.create_task(download_image_async(url, image_path))
        tasks.append(task)
    await asyncio.gather(*tasks)

def download_image_threading(urls, image_path):
    start_time = time.time()
    threads = []
    for url in urls:
        t = threading.Thread(target=download_image, args=(url, image_path))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    end_time = time.time() - start_time
    print(f"Загрузка завершена за {end_time:.2f} секунд")

def download_images_multiprocessing(urls, image_path):
    start_time = time.time()
    processes = []
    for url in urls:
        p = multiprocessing.Process(target=download_image, args=(url, image_path))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
    end_time = time.time() - start_time
    print(f"Загрузка завершена за {end_time:.2f} секунд")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Парсер изображений по URL-адресам")
    parser.add_argument("--urls", nargs="+", help="Список URL-адресов для загрузки изображений")
    args = parser.parse_args()

    urls = args.urls
    if not urls:
        with open('image.txt', 'r') as images:
            urls = [image.strip() for image in images.readlines()]

    image_path = Path(os.path.join(os.path.dirname(__file__), 'images'))
    if not image_path.exists():
        image_path.mkdir()

    print(f"Загрузка {len(urls)} изображений - ПОТОКИ")
    download_image_threading(urls, image_path)

    print(f"\nЗагрузка {len(urls)} изображений - МУЛЬТИПРОЦЕССОРЫ")
    download_images_multiprocessing(urls, image_path)

    print(f"\nЗагрузка {len(urls)} изображений - АСИНХРОННО")
    asyncio.run(download_image_asyncio(urls, image_path))