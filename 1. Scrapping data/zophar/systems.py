from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import json
import time
import os

driver = None
path = os.path.dirname(__file__)

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

    systems = [
        "nintendo-nes-nsf",
        "nintendo-snes-spc",
        "gameboy-gbs",
        "gameboy-advance-gsf",
        "nintendo-ds-2sf",
        "nintendo-3ds-3sf",
        "nintendo-64-usf",
        "nintendo-gamecube-gcn",
        "nintendo-wii",
        "playstation-psf",
        "playstation2-psf2",
        "playstation3-psf3",
        "playstation-portable-psp",
        "sega-game-gear-sgc",
        "sega-master-system-vgm",
        "sega-mega-drive-genesis",
        "sega-saturn-ssf",
        "sega-dreamcast-dsf",
        "turbografx-16-hes",
        "xbox",
        "xbox-360",
    ]

    for system in systems:
        os.makedirs(f"{path}/systems/{system}", exist_ok=True)

        print(f"Coletando dados do console {system}")

        page = 1

        while page > 0:
            # Get the first page of the system
            driver.get(f"https://www.zophar.net/music/{system}?page={page}")

            time.sleep(5)
            wait = WebDriverWait(driver, 5)

            print(f"Página {page}")
            with open(f"{path}/systems/{system}/{page}.html", "w") as f:
                f.write(driver.page_source)

            try:
                pagination_next = driver.find_element(By.CLASS_NAME, "pagination-next")
                href_value = pagination_next.find_element(
                    By.TAG_NAME, "a"
                ).get_attribute("href")
                page_number = (
                    href_value.split("page=")[1] if "page=" in href_value else "#"
                )
                page = int(page_number) if page_number != "#" else 0
            except Exception as e:
                page = 0

        print("\n")

# except Exception as e:
# with open(f"{path}/error.log", "w") as f:
# f.write(str(e))

finally:
    # Feche o navegador
    if driver:
        driver.quit()
