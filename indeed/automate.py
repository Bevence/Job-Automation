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
from selenium.common.exceptions import ElementNotInteractableException
import re
from pyvirtualdisplay import Display
from selenium.webdriver import ActionChains




# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger("apps")

# Create your tests here.
class IndeedAutomation:
    def __init__(self):
        self.display = Display(visible=0, size=(800, 600))
        self.display.start()
        self.selenium = webdriver.Firefox()
        self.selenium.maximize_window()
        # self.selenium = webdriver.Remote(
        #     command_executor='http://selenium_hub:4444/wd/hub',
        #     desired_capabilities=DesiredCapabilities.FIREFOX
        # )

    # def setUp(self):
    #     self.display = Display(visible=0, size=(1024, 768))
    #     self.display.start()
    #     self.selenium = webdriver.Remote(
    #         command_executor='http://selenium_hub:4444/wd/hub',
    #         desired_capabilities=DesiredCapabilities.FIREFOX
    #     )
    #     super(IndeedTestCase, self).setUp()
        

    def quit(self):
        self.selenium.quit()
        self.display.stop()

    def url_generator(self, job_title, city, state):
        base = "https://www.indeed.com/jobs?q="
        job_title = job_title.replace(" ","%20")+"&l="
        state = state.replace(" ","%20")

        city = city.replace(" ","%20")+"%2C%20" if city else None
        url = base + job_title + city + state if city else base + job_title + state 

        logger.info("Target url: %s", url)
        return url
        
    def login(self, email, password):
        try:
            logger.info("Redirected to login page... ")
            self.selenium.get('https://secure.indeed.com/account/login')
            email_field = WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.ID, 'login-email-input')))
            # email = selenium.find_element_by_id('login-email-input')
            password_field = WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.ID, 'login-password-input')))
            # password = selenium.find_element_by_id('login-password-input')
            email_field.send_keys(email)
            password_field.send_keys(password)
            sign_in = self.selenium.find_element_by_id('login-submit-button')
            logger.info("Trying to logged in... ")
            sign_in.click()
            logger.info("User get logged in... [Email: %s]", email)
            time.sleep(5)
            newURL = self.selenium.current_url
            print("old url = 'https://secure.indeed.com/account/login'")
            print("New URL = ", newURL)
            logger.info("Redirected to job page:  [ %s]", newURL)
            if newURL != "https://secure.indeed.com/account/view":
                try:
                    logger.info("Navigating to captcha iframe")
                    # find iframe
                    captcha_iframe = WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))

                    ActionChains(self.selenium).move_to_element(captcha_iframe).click().perform()

                    # click im not robot
                    captcha_box = WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, 'g-recaptcha-response')))
                    logger.info("Trying to click captcha iframe")
                    self.selenium.execute_script("arguments[0].click()", captcha_box)
                    logger.info("Clicked captcha iframe")
                    password_field = WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.ID, 'login-password-input')))
                    password_field.send_keys(password)
                    sign_in = self.selenium.find_element_by_id('login-submit-button')
                    sign_in.click()
                    time.sleep(5)
                    newURL = self.selenium.current_url
                    logger.info("New url: %s", newURL)
                    if newURL != "https://secure.indeed.com/account/view":
                        self.quit()
                        return 0 # for image captcha
                    logger.info("User get logged in... [Email: %s]", email)
                    time.sleep(5)
                except Exception as e:
                    logger.error("Logging error: ", e)
                    return False
            return True
                    
            
        except TimeoutError as e:
            logger.exception("Timeout while trying to login.")
            
    def search_jobs(self, job_title, city=None, state=None):
        url = self.url_generator(job_title, city, state)
        self.selenium.get(url)
        

    def find_offers(self):
        """This function finds all the offers through all the pages result of the search and filter"""

        # find the total amount of results (if the results are above 24-more than one page-, we will scroll trhough all available pages)
        # total_results = self.selenium.find_element_by_id("searchCountPages")
        # total_results_int = int(total_results.text.split(' ')[-2].replace(",",""))
        # print(total_results_int)
        
        while True:
            
            try:
                # activate = WebDriverWait(self.selenium, 2).until(EC.presence_of_element_located((By.ID, 'popover-form-container')))
                button = self.selenium.find_element_by_id('job-alert-popover-button')
                button.click()
                close = self.selenium.find_element_by_id('popover-x')
                close.click()
            
            except (NoSuchElementException, ElementNotInteractableException):
                pass
            # pane = self.selenium.find_element_by_id("resultsCol")
            results = self.selenium.find_elements_by_class_name('jobsearch-SerpJobCard.unifiedRow.row.result.clickcard')
            print("RESULTS: ", len(results))
            for result in results:
                self.submit_apply(result)
                # time.sleep(5)
                # selenium.switch_to.frame("vjs-container-iframe")
                # # iframe = self.selenium.find_elements_by_id('vjs-container-iframe')
                # # time.sleep(5)
                # # self.selenium.switch_to_frame(iframe[0])
                # time.sleep(5)
                # button = selenium.find_element_by_xpath("//a[@class='icl-Button.icl-Button--primary.icl-Button--lg.icl-Button--block']")
                # time.sleep(5)
                # button.click()
                # print("After iframe")
                # # self.selenium.switch_to_default_content()
                
            try:
                next_button = self.selenium.find_element_by_xpath("//li[a/@aria-label='Next']")
                logger.info("Moving to next page...")
                next_button.click()
                logger.info("Moved to next page...")
            except NoSuchElementException:
                logger.exception("Unable to move in next page.")
                break
            
            time.sleep(1)

    def submit_apply(self, job_add):
        """This function submits the application for the job add found"""

        # print('You are applying to the position of: ', job_add.text)
        print("JOB ADD : ", job_add)
        job_add.click()
        time.sleep(2)
        # print("After Iframe")
        try:
            # get_frame = self.selenium.find_element_by_id("vjs-container-iframe")
            get_frame = WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, 'vjs-container-iframe')))
            self.selenium.switch_to_frame(get_frame)
        except Exception as e:
            print("ERROR: ", e)
            self.selenium.switch_to_default_content()
        else:
            # click on the easy apply button, skip if already applied to the position
            try:
                in_apply = self.selenium.find_element_by_id('viewJobButtonLinkContainer')
            except NoSuchElementException:
                try:
                    print("CRURRENT URL: ", self.selenium.current_url)
                    in_apply = self.selenium.find_element_by_xpath("//button[@class='icl-Button.icl-Button--branded.icl-Button--block']")
                    in_apply.click()
                    continue1 = self.selenium.find_element_by_xpath("//button[@id='form-action-continue']")
                    continue1.send_keys(Keys.RETURN)
                    time.sleep(2)
                    submit = self.selenium.find_element_by_xpath("//button[@id='form-action-submit']")
                    submit.send_keys(Keys.RETURN)
                    time.sleep(2)
                    close = self.selenium.find_element_by_class_name('ia-ConfirmationScreen-closeLink')
                    close.send_keys(Keys.RETURN)
                    time.sleep(2)
                    
                    print('You already applied to this job, go to next...')
                    self.selenium.switch_to_default_content()
                except NoSuchElementException:
                    print("APPLY NOW ERROR")
                    self.selenium.switch_to_default_content()
                    # discard = self.selenium.find_element_by_xpath("//button[@data-test-modal-close-btn]")
                    # discard.send_keys(Keys.RETURN)
                    # time.sleep(1)
                    # discard_confirm = self.selenium.find_element_by_xpath("//button[@data-test-dialog-primary-btn]")
                    # discard_confirm.send_keys(Keys.RETURN)
                    # time.sleep(1)
                # try:
                #     discard = self.selenium.find_element_by_xpath("//button[@data-test-modal-close-btn]")
                #     discard.send_keys(Keys.RETURN)
                #     time.sleep(1)
                #     discard_confirm = self.selenium.find_element_by_xpath("//button[@data-test-dialog-primary-btn]")
                #     discard_confirm.send_keys(Keys.RETURN)
                #     time.sleep(1)
                # except NoSuchElementException:
                #     pass
            else:
                print("viewJobButtonLinkContainer")
                self.selenium.switch_to_default_content()
                
                


       

     
    def main(self):
        pass
        # self.setUp()
        # time.sleep(5)
        # self.login()
        # time.sleep(5)
        # self.search_jobs()
        # time.sleep(5)
        # self.find_offers()
        # time.sleep(5)
        # self.tearDown()




        

# witbikesh.bs@gmail.com
# b!keshs!t!khu77