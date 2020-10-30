
import requests
import tarfile
import io
import os
import sys
import time
import datetime

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

# Linux
LINUX_WEBDRIVER = "https://github.com/mozilla/geckodriver/releases/download/v0.27.0/geckodriver-v0.27.0-linux64.tar.gz"

# Mac OSX 
OSX_WEBDRIVER = "https://github.com/mozilla/geckodriver/releases/download/v0.27.0/geckodriver-v0.27.0-macos.tar.gz"


def download_driver():
    
    if not os.path.exists('assets'):
        os.mkdir('assets')
    
    if not os.path.exists('assets/geckodriver'):

        if sys.platform == 'linux':
            url = LINUX_WEBDRIVER
        elif sys.platform == 'darwin':
            url = OSX_WEBDRIVER

        # NEED TO FIGURE OUT TARFILES
        zipped = io.BytesIO(requests.get(url).content)
        data = tarfile.open(fileobj=zipped, mode='r:gz')
        geckodriver = data.extractfile('geckodriver').read()
        
        fp = 'assets/geckodriver'
        with open(fp, 'wb') as fh:
            fh.write(geckodriver)

        os.chmod(fp, 0o700)

    path = os.environ["PATH"]
    path = path + ':%s/assets' % os.path.abspath(os.curdir)
    os.environ["PATH"] = path
    
    return


def create_profile():

    dl_dir = os.path.abspath('data/tmp')
    if not os.path.exists(dl_dir):
        os.makedirs(dl_dir, exist_ok=True)

    profile = FirefoxProfile()
    profile.set_preference(
        "browser.download.panel.shown", False
    )
    profile.set_preference(
        "browser.helperApps.neverAsk.openFile", 
        "text/csv,application/excel"
    )
    profile.set_preference(
        "browser.helperApps.neverAsk.saveToDisk", 
        "text/csv,application/excel"
    )
    profile.set_preference(
        "browser.download.folderList", 2
    )
    profile.set_preference(
        "browser.download.downloadDir", dl_dir
    )
    profile.set_preference(
        "browser.download.dir", dl_dir
    )

    return profile


def start_driver():

    profile = create_profile()
    try:
        driver = webdriver.Firefox(firefox_profile=profile)
    except WebDriverException:
        download_driver()
        driver = webdriver.Firefox(firefox_profile=profile)

    return driver


def create_zoom_url():
    '''
    creates zoom url to pull participants in all meetings 30 days before present day.
    '''
    today = datetime.date.today()
    minus30 = today - datetime.timedelta(days=30)

    end_date = today.strftime('%m/%d/%Y') # '10/30/2020'
    start_date = minus30.strftime('%m/%d/%Y')   # '09/30/2020'

    url = "https://ucsd.zoom.us/account/my/report?p=1&from={start}&to={end}".format(start=start_date, end=end_date)

    return url

# ---------------------------------------------------------------------
# Scraping Logic
# ---------------------------------------------------------------------


def main():
        
    zoom_url = create_zoom_url()
    driver = start_driver()
    print("Log in to Zoom in the new browser window. Do not touch browser after logging in.")
    driver.get(zoom_url)

    xpath = "//table/tbody/tr/td/a[@data-attendees='']"

    # loop until log-in
    elems, ctr = [], 0
    while not elems:

        elems = driver.find_elements_by_xpath(xpath)
        time.sleep(5)
        ctr += 1
        if ctr > 24:
            break

    # for each meeting, click participants button
    # download attendees, click close meeting
    for elem in elems:

        elem.click()
        time.sleep(1)
        driver.find_element_by_id('withMeetingHeader').click()
        driver.find_element_by_id('btnExportParticipants').click()
        btn = driver.find_element_by_xpath(
            "//div[@id='attendees_dialog']//button[@aria-label='close']"
        )
        btn.click()
        time.sleep(1)

    driver.close()

    return


if __name__ == '__main__':
    
    main()
