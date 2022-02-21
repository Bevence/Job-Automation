from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import re
from pyvirtualdisplay import Display
from urllib3.exceptions import MaxRetryError, NewConnectionError, ConnectTimeoutError
from selenium.common.exceptions import ElementNotInteractableException

import logging

# Get an instance of a logger
logger = logging.getLogger("apps")


# Create your tests here.
class LinkedinAutomate:
    def __init__(self):
        # self.resume = resume
        self.display = Display(visible=0, size=(800, 600))
        self.display.start()
        # cap = DesiredCapabilities().FIREFOX
        # profile = webdriver.FirefoxProfile()
        # cap["marionette"] = False
        self.selenium = webdriver.Firefox() 
        # self.selenium = webdriver.Remote(
        #     command_executor='http://selenium_hub:4444/wd/hub',
        #     desired_capabilities=cap,
        #     browser_profile=profile
        # )
        self.selenium.maximize_window()
        # self.selenium = webdriver.Firefox(capabilities=cap, executable_path="/usr/local/bin/geckodriver") 

    # def setUp(self): 

    #     # cap = DesiredCapabilities().FIREFOX
    #     # cap["marionette"] = False

    #     # self.selenium = webdriver.Firefox()
    #     self.display = Display(visible=0, size=(1024, 768))
    #     self.display.start()
    #     self.selenium = webdriver.Remote(
    #         command_executor='http://selenium_hub:4444/wd/hub',
    #         desired_capabilities=DesiredCapabilities.FIREFOX
    #     )
    #     # self.selenium = webdriver.Firefox(capabilities=cap, executable_path="/usr/local/bin/geckodriver")
    #     super(LinkedinTestCase, self).setUp()

    def quit(self):
        self.selenium.quit()
        self.display.stop()

    def url_generator(self, job_title, city, state):
        base = "https://www.linkedin.com/jobs/search/?keywords="
        job_title = job_title.replace(" ","%20")+"&location="
        state = state.replace(" ","%20")

        if city:
            city = city.replace(" ","%20")+"%2C%20"
            url = base + job_title + city + state
        else:
            url = base + job_title + state 

        logger.info("Target url: %s", url)
        return url

    def login(self, email, password):
        try:
            logger.info("Logging to LinkedIn")
            self.selenium.get('https://www.linkedin.com/login')
            logger.info("NAVIGATING to logging page")
            email_field = self.selenium.find_element_by_id('username')
            password_field = self.selenium.find_element_by_id('password')
            email_field.send_keys(email)
            password_field.send_keys(password)
            logger.info("Pressing signing button")
            sign_in = self.selenium.find_element_by_class_name('btn__primary--large')
            sign_in.click()
            logger.info("Pressed signing button")
            time.sleep(3)
            logger.info("LOGGED IN")
            newURL = self.selenium.current_url
            if newURL != "https://www.linkedin.com/feed/":
                logger.info("Fail to login for user %s", email)
                self.quit()
                return False

        except TimeoutError as e:
            logger.error("Timout while logging in loggedin")
        except MaxRetryError as e:
            logger.exception(e)
        except NewConnectionError as e:
            logger.exception(e)
        except ConnectionRefusedError as e:
            logger.exception(e)
        else:
            return True
            
    def search_jobs(self, job_title, city, state):
        url = self.url_generator(job_title, city, state)
        self.selenium.get(url)

    def find_offers(self):
        """This function finds all the offers through all the pages result of the search and filter"""

        # find the total amount of results (if the results are above 24-more than one page-, we will scroll trhough all available pages)
        total_results = self.selenium.find_element_by_class_name("display-flex.t-12.t-black--light.t-normal")
        total_results_int = int(total_results.text.split(' ',1)[0].replace(",",""))
        print(total_results_int)

        time.sleep(2)
        # get results for the first page
        current_page = self.selenium.current_url
        results = self.selenium.find_elements_by_class_name("occludable-update.artdeco-list__item--offset-2.artdeco-list__item.p0.ember-view")

        # for each job add, submits application if no questions asked
        for result in results:
            self.submit_apply(result)

        # if there is more than one page, find the pages and apply to the results of each page
        if total_results_int > 24:
            time.sleep(2)

            # find the last page and construct url of each page based on the total amount of pages
            find_pages = self.selenium.find_elements_by_class_name("artdeco-pagination__pages.artdeco-pagination__pages--number")
            total_pages = find_pages[len(find_pages)-1].text
            total_pages_int = int(re.sub(r"[^\d.]", "", total_pages))
            get_last_page = self.selenium.find_element_by_xpath("//button[@aria-label='Page "+str(total_pages_int)+"']")
            get_last_page.send_keys(Keys.RETURN)
            time.sleep(2)
            last_page = self.selenium.current_url
            total_jobs = int(last_page.split('start=',1)[1])

            # go through all available pages and job offers and apply
            for page_number in range(25,total_jobs+25,25):
                self.selenium.get(current_page+'&start='+str(page_number))
                time.sleep(2)
                results_ext = self.selenium.find_elements_by_class_name("occludable-update.artdeco-list__item--offset-2.artdeco-list__item.p0.ember-view")
                for result_ext in results_ext:
                    self.submit_apply(result_ext)
        else:
            self.quit()
        return True
       
        
    def submit_apply(self,job_add):
        """This function submits the application for the job add found"""

        logger.info("You are applying to the position of %s", job_add.text)
        job_add.click()
        time.sleep(2)

        # click on the easy apply button, skip if already applied to the position
        try:
            in_apply = self.selenium.find_element_by_xpath("//button[@data-control-name='jobdetails_topcard_inapply']")
            in_apply.click()
        except NoSuchElementException:
            logger.info("You already have applied to the job:  %s", job_add.text)
        time.sleep(1)

        # try to submit if submit application is available...
        try:
            submit = self.selenium.find_element_by_xpath("//button[@data-control-name='submit_unify']")
            submit.send_keys(Keys.RETURN)
            time.sleep(1)
            discard = self.selenium.find_element_by_xpath("//button[@data-test-modal-close-btn]")
            discard.send_keys(Keys.RETURN)
            time.sleep(1)
            logger.info("Job applied:  [Job Title - [ %s ]", job_add.text)
        
        # ... if not available, discard application and go to next
        except NoSuchElementException:
            logger.info("Unable to apply for this job title:  %s", job_add.text)
            try:
                discard = self.selenium.find_element_by_xpath("//button[@data-test-modal-close-btn]")
                discard.send_keys(Keys.RETURN)
                time.sleep(1)
                discard_confirm = self.selenium.find_element_by_xpath("//button[@data-test-dialog-primary-btn]")
                discard_confirm.send_keys(Keys.RETURN)
                time.sleep(1)
            except NoSuchElementException:
                pass

        time.sleep(4)

        