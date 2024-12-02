from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

import json
import time
import os
import re

path = os.path.dirname(__file__)

data_dir = os.path.join(f"{path}", "systems")

try:
    # Inicialize o serviço do ChromeDriver
    service = Service(ChromeDriverManager().install())
    service.start()

    # Configure o WebDriver
    options = webdriver.ChromeOptions()

    options.binary_location = "/usr/bin/google-chrome"
    options.add_argument("--headless")  # Para rodar em background
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=service, options=options)

    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                soup = BeautifulSoup(content, "lxml")

                divs = soup.find_all("div", class_="url")

                rows = soup.find_all("tr", class_=["regularrow", "regularrow_image"])

                # Extract the href from the <a> tag inside the <td> with class "name"
                for row in rows:
                    name_cell = row.find("td", class_="name")
                    if name_cell and name_cell.a:
                        href = name_cell.a["href"]
                        # Get only the desired part of the href
                        [_, music, system, game] = href.split("/")

                        os.makedirs(f"{path}/data/{system}", exist_ok=True)

                        # Get the game page
                        driver.get(f"https://www.zophar.net/music/{system}/{game}")

                        with open(f"{path}/data/{system}/{game}.html", "w") as f:
                            f.write(driver.page_source)


finally:
    # Feche o navegador
    if driver:
        driver.quit()
