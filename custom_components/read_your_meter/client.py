"""Meter client"""

import logging
import time
import requests

from datetime import datetime
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

from bs4 import BeautifulSoup

from .utils import truncate

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
        self._forecast = None
        self._low_consumption = None
        self._house_hold_avg = None
        self._messages_count = None
        self._daily_table = []
        self._monthly_table = []

    def update_data(self, start_date=None, end_date=None):
        """Update consumption data"""
        daily_table = []
        monthly_table = []

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('whitelisted-ips')
        chrome_options.add_argument('headless')
        chrome_options.add_argument('no-sandbox')

        try:
            # Check selenuim connection
            r = requests.get(urljoin(self._selenium, 'wd/hub/status'))
            r.raise_for_status()

            with webdriver.Remote(command_executor=urljoin(self._selenium, 'wd/hub'),
                                desired_capabilities=DesiredCapabilities.CHROME,
                                options=chrome_options) as driver:
                # Login
                # _LOGGER.debug('Login')
                driver.implicitly_wait(5)
                driver.get(self._host)
                driver.find_element_by_id('txtEmail').send_keys(self._username)
                driver.find_element_by_id('txtPassword').send_keys(self._password)
                driver.find_element_by_id('btnLogin').click()
                # Extract some general data
                try:
                    element = driver.find_element_by_id('cphMain_lblMeterSN')
                    self._meter_number = element.text
                except NoSuchElementException:
                    pass
                try:
                    element = driver.find_element_by_id('spn_current_read')
                    self._last_read = element.text
                except NoSuchElementException:
                    pass
                try:
                    element = driver.find_element_by_id('spn_forecast')
                    self._forecast = element.text
                except NoSuchElementException:
                    pass
                try:
                    element = driver.find_element_by_id('spn_low_consumption')
                    self._low_consumption = element.text
                except NoSuchElementException:
                    pass
                try:
                    element = driver.find_element_by_id('spn_house_hold_avg')
                    self._house_hold_avg = element.text
                except NoSuchElementException:
                    pass
                try:
                    element = driver.find_element_by_id('cphMain_spn_messages_count')
                    self._messages_count = element.text
                except NoSuchElementException:
                    pass
                # Navigate to my consumption age
                driver.get(urljoin(self._host, 'Consumption.aspx#0'))
                try:
                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'Consumption')))
                except TimeoutException:
                    _LOGGER.error('Loading of my consumption page took too much time')
                    driver.close()
                    return False
                # _LOGGER.debug(f"{driver.current_url}")
                # Switch to daily table view
                element = driver.find_element_by_id('btn_table')
                webdriver.ActionChains(driver).move_to_element(element).click(element).perform()
                try:
                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'AlertsTable')))
                except TimeoutException:
                    _LOGGER.error('Loading of table took too much time')
                    driver.close()
                    return False
                # _LOGGER.debug(f"{driver.current_url}")
                html = driver.page_source
                # Extract daily table
                if html:
                    soup = BeautifulSoup(html, features="html.parser")
                    table = soup.find('table', attrs={'class':'AlertsTable'})
                    if table:
                        for row in table.find('tbody').find_all('tr'):
                            cols = row.find_all('td')
                            cols = [ele.text.strip() for ele in cols]
                            if len(cols):
                                daily_table.append([ele for ele in cols if ele])
                        # Remove table summary
                        if len(daily_table):
                            daily_table.pop()
                # Switch to monthly
                element = driver.find_element_by_id('btn_period_type_0')
                webdriver.ActionChains(driver).move_to_element(element).click(element).perform()
                time.sleep(1)
                # _LOGGER.debug(f"{driver.current_url}")
                html = driver.page_source
                # Extract daily table
                if html:
                    soup = BeautifulSoup(html, features="html.parser")
                    table = soup.find('table', attrs={'class':'AlertsTable'})
                    if table:
                        for row in table.find('tbody').find_all('tr'):
                            cols = row.find_all('td')
                            cols = [ele.text.strip() for ele in cols]
                            if len(cols):
                                monthly_table.append([ele for ele in cols if ele])
                        # Remove table summary
                        if len(monthly_table):
                            monthly_table.pop()
                # Update new values
                self._daily_table = daily_table
                self._monthly_table = monthly_table
                driver.close()
        except WebDriverException:
             _LOGGER.error('Webdriver error')
        except requests.exceptions.HTTPError as errh:
            _LOGGER.error('Sellenuim http error: %s', errh)
        except requests.exceptions.ConnectionError as errc:
            _LOGGER.error('Sellenuim error connecting: %s', errc)
        except requests.exceptions.Timeout as errt:
            _LOGGER.error("Sellenuim timeout error: %s", errt)
        except requests.exceptions.RequestException as err:
            _LOGGER.error("OOps: error: %s", err)

        return True

    def consumption(self, period, index=0):
        """Return consumption"""
        try:
            table = self._monthly_table if period == 'monthly' else self._daily_table
            return float(table[-1 - index][1])
        except IndexError:
           return None

    def state(self, period, index=0):
        """Return consumption state"""
        try:
            table = self._monthly_table if period == 'monthly' else self._daily_table
            return table[-1 - index][4]
        except IndexError:
           return None

    def date(self, period, index=0):
        """Return consumption date"""
        try:
            table = self._monthly_table if period == 'monthly' else self._daily_table
            return table[-1 - index][0]
        except IndexError:
           return None

    def statistics(self, period):
        """Return consumption statistics"""
        table = self._monthly_table if period == 'monthly' else self._daily_table
        values = [float(row[1]) for row in table[:-1]]
        if len(values):
            return {
                'avg': truncate(sum(values) / len(values), 2),
                'min': min(values),
                'max': max(values)
            }
        else:
            _LOGGER.debug(f"Failed to calculate {period} statistics")
            return {}

    @property
    def meter_number(self):
        return self._meter_number

    @property
    def last_read(self):
        return self._last_read

    @property
    def forecast(self):
        return self._forecast

    @property
    def low_consumption(self):
        return self._low_consumption

    @property
    def house_hold_avg(self):
        return self._house_hold_avg

    @property
    def messages_count(self):
        message_count = 0
        if self._messages_count:
            message_count = [int(s) for s in self._messages_count.split() if s.isdigit()][0]
        return message_count