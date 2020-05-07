import logging

from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from bs4 import BeautifulSoup

_LOGGER = logging.getLogger(__name__)


class Client:

    def __init__(self, selenium, host, username, password):
        """Initialize the class."""
        self._selenium = selenium
        self._host = host
        self._username = username
        self._password = password
        self._meter_number = None
        self._last_read = None

    async def async_get_daily_consumption(self, start_date=None, end_date=None):
        """Update"""
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('whitelisted-ips')
        chrome_options.add_argument('headless')
        chrome_options.add_argument('no-sandbox')

        with webdriver.Remote(command_executor=urljoin(self._selenium, 'wd/hub'),
                              desired_capabilities=DesiredCapabilities.CHROME,
                              options=chrome_options) as driver:
            # Login
            _LOGGER.debug('Login')
            driver.implicitly_wait(5)
            driver.get(self._host)
            driver.find_element_by_id('txtEmail').send_keys(self._username)
            driver.find_element_by_id('txtPassword').send_keys(self._password)
            driver.find_element_by_id('btnLogin').click()
            # Extract some general data
            try:
                element = driver.find_element_by_id('cphMain_lblMeterSN')
                self._meter_number = element.text
                _LOGGER.debug(f"{self._meter_number}")
            except NoSuchElementException:
                pass
            try:
                element = driver.find_element_by_id('spn_current_read')
                self._last_read = element.text
            except NoSuchElementException:
                pass
            # Navigate to my consumption age
            driver.get(urljoin(self._host, 'Consumption.aspx#0'))
            try:
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'Consumption')))
            except TimeoutException:
                _LOGGER.error('Loading of my consumption page took too much time')
                return []
            _LOGGER.debug(f"{driver.current_url}")
            # Switch to daily table view
            element = driver.find_element_by_id('btn_table')
            webdriver.ActionChains(driver).move_to_element(element).click(element).perform()            
            try:
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'AlertsTable')))
            except TimeoutException:
                _LOGGER.error('Loading of table took too much time')
                return []
            _LOGGER.debug(f"{driver.current_url}")
            html = driver.page_source
            driver.close()
            # Extract daily table
            daily_table = []
            if html:
                soup = BeautifulSoup(html, features="html.parser")
                table = soup.find('table', attrs={'class':'AlertsTable'})
                if table:
                  for row in table.find('tbody').find_all('tr'):
                      cols = row.find_all('td')
                      cols = [ele.text.strip() for ele in cols]
                      daily_table.append([ele for ele in cols if ele])
            return daily_table

    @property
    def meter_number(self):
        return self._meter_number

    @property
    def last_read(self):
        return self._last_read