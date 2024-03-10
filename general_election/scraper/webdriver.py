import os
import bs4
import platform
from bs4 import BeautifulSoup
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service


class CustomWebDriver:
    def __init__(self, headless=True):
        self.headless = headless

        os_system = platform.system()
        driver_path = os.path.abspath(os.path.join(os.getcwd(), './general_election/scraper/driver'))
        driver_fn = 'msedgedriver.exe' if os_system == 'Windows' else 'msedgedriver'

        self.driver_location = os.path.abspath(os.path.join(driver_path, './' ,driver_fn))

        self.driver = self._load_driver()

    
    def _load_driver(self) -> webdriver.Edge:
        self._kill_driver()

        def _interceptor(request):
            REFERER = 'https://search.naver.com/'
            HEADERS = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'

            request.headers['Referer'] = REFERER
            request.headers['User-Agent'] = HEADERS

        edge_options = webdriver.EdgeOptions()
        edge_options.accept_insecure_certs = True

        if self.headless:
            edge_options.add_argument('--headless')

        edge_options.add_argument('--no-sandbox')
        edge_options.add_argument('--disable-gpu')
        edge_options.add_argument("--disable-crash-reporter")
        edge_options.add_argument("--disable-extensions")
        edge_options.add_argument('--allow-running-insecure-content')
        edge_options.add_argument('--ignore-certificate-errors')
        edge_options.add_argument("--disable-logging")

        seleniumwire_options = {
            'exclude_hosts': ['google-analytics.com'],
            'verify_ssl': False
        }
        
        driver = webdriver.Edge(
            service=Service(self.driver_location),
            options=edge_options,
            seleniumwire_options=seleniumwire_options
        )
        
        driver.request_interceptor = _interceptor
        driver.set_page_load_timeout(30)

        return driver
    

    def _check_driver(self) -> bool:
        try:
            self.driver.window_handles
            return True
        
        except Exception as e:
            return False
        
    
    def _kill_driver(self) -> None:
        try:
            self.driver.quit()
            self.driver = None

        except Exception as e:
            pass


    def _check_windows(self) -> int:
        all_windows = self.driver.window_handles
        return all_windows


    def switch_to_frame(self, frame: str) -> None:
        self.driver.switch_to.frame(frame)


    def get(self, url: str) -> bool:
        if not self._check_driver():
            self.driver = self._load_driver()

        try:
            self.driver.get(url)

        except Exception as e:
            self._kill_driver()
            return False

        windows = self._check_windows()
        if len(windows) > 1:
            for window in windows[:0:-1]:
                self.driver.switch_to.window(window)
                self.driver.close()

            return False
        
        return True


    def get_page_source(self, to_soup=True) -> str | bs4.element.Tag :
        try:
            if to_soup:
                return BeautifulSoup(self.driver.page_source, 'html.parser')
            
            return self.driver.page_source
        except:
            return ''


    def find_element(self,
        by: str = By.CLASS_NAME,
        value: str = 'u_cbox_btn_more'
    ):
        """
        Webdriver Click

        Parameters
        ----------
        by: str
            String or selenium.webdriver.common.by
        value: str
            css selector

        Returns
        -------
        selenium.webdriver.remote.webelement.WebElement
        """
        element = self.driver.find_element(by, value)

        return element
