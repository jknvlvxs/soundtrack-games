from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json
import time
import os

driver = None
path = os.path.dirname(__file__)


def getJsonFromFile(file_path):
    with open(f"{path}/{file_path}", "r") as file:
        return json.load(file)


try:
    # Inicialize o serviço do ChromeDriver
    service = Service(f"{path}/chromedriver")
    service.start()

    # Configure o WebDriver
    options = webdriver.ChromeOptions() 

    options.binary_location = '/usr/bin/google-chrome'
    options.add_argument('--headless')  # Para rodar em background
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(service=service, options=options)

    systems = getJsonFromFile("systems/systems.json")
    systems_names = getJsonFromFile("systems/names.json")

    systems_names_relation = dict(zip(systems, systems_names))

    extensions = getJsonFromFile("extensions/convert.ffmpeg.json")

    for system in systems_names_relation:
        # Create a directory for system in 'data/{system}'
        system_name = systems_names_relation[system].replace(' ', '_')
        system_code = system.lower()

        for extension in extensions:
            os.makedirs(f"{path}/data/{system_name}", exist_ok=True)
            print(f"Coletando dados do console {system_name} ({system_code}) com extensão {extension}")

            page = 1

            while page != "":
                # Get the first page of the system
                driver.get(f"https://vgm.hcs64.com?site={system_code}&page={page}&exts={extension}")

                # Wait for the page to load
                time.sleep(5)
                wait = WebDriverWait(driver, 5)

                # Busca o next page no <a> com class="page-next" e data-page=""
                next_page = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.page-next")))
                data_page = next_page.get_attribute("data-page")

                if data_page == page: break

                print(f"→ Página {page}")

                with open(f"{path}/data/{system_name}/{system_code}_{extension}_{page}.html", "w") as f:
                    f.write(driver.page_source)

                page = data_page

            print("\n")

except Exception as e:
    with open("{path}/error.log", "w") as f:
        f.write(str(e))

finally:
    # Feche o navegador
    if driver:
        driver.quit()
