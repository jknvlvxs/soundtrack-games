from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

driver = None

try:
    # Inicialize o serviço do ChromeDriver
    service = Service('./chromedriver')
    service.start()

    # Configure o WebDriver
    options = webdriver.ChromeOptions() 

    options.binary_location = '/usr/bin/google-chrome'
    options.add_argument('--headless')  # Para rodar em background
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(service=service, options=options)

    # systems = ['pc', 'hoot', '2sf', 'switch', 'psf2', 'psp', 'nsf', 'spc', 'gbs', 'psf', 'vita', 'mobile', '3sf', 'gsf', 'x360', 'kss', 'smd', 'psf3', 'cdi', 'hes', 'wii', 'ssf', 'dsf', 'wiiu', 'xbox', 'gcn', 'psf4', 's98', 'usf', 'fmtowns', 'wsr', '3do', 'ncd', 'psf5']
    # systems_names = ['PC', 'Hoot', 'DS', 'Switch', 'PS2', 'PSP', 'NES', 'SNES', 'GB', 'PS1', 'Vita', 'Mobile', '3DS', 'GBA', 'Xbox 360', 'Master System', 'Mega Drive', 'PS3', 'Other systems', 'PC Engine', 'Wii', 'Saturn', 'Dreamcast', 'Wii U', 'Xbox', 'GameCube', 'PS4', 'Japanese PC', 'N64', 'FM Towns', 'WonderSwan', '3DO', 'Neo Geo CD', 'PS5']

    systems = ['usf', 'fmtowns', 'wsr', '3do', 'ncd', 'psf5']
    systems_names = ['N64', 'FM Towns', 'WonderSwan', '3DO', 'Neo Geo CD', 'PS5']


    systems_names_relation = dict(zip(systems, systems_names))

    for system in systems_names_relation:
        # Create a directory for system in 'data/{system}'
        system_name = systems_names_relation[system].replace(' ', '_')
        system_code = system.lower()

        os.makedirs(f'data/{system_name}', exist_ok=True)
        print(f'Coletando dados do console {system_name} ({system_code})')

        page = 1

        while(page != ''):
            # Get the first page of the system
            driver.get(f'https://vgm.hcs64.com?site={system_code}&page={page}') 

            # Wait for the page to load
            time.sleep(5)
            wait = WebDriverWait(driver, 10)

            # Busca o next page no <a> com class="page-next" e data-page=""
            next_page = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.page-next')))
            data_page = next_page.get_attribute('data-page')

            if(data_page == page): break;

            print(f'→ Página {page}')

            with open(f'data/{system_name}/{system_code}_page_{page}.html', 'w') as f:
                f.write(driver.page_source)
            
            page = data_page

        print('\n')

except Exception as e:
    with open('error.log', 'w') as f:
        f.write(str(e))

finally:
    # Feche o navegador
    if driver:
        driver.quit()
