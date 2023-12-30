import pretty_errors
import os
import sys

from robocorp import browser
from robocorp.tasks import task

from RPA.Excel.Files import Files as Excel
from RPA.HTTP import HTTP
from RPA.HTTP import FileSystem
from RPA.Tables import Tables

pretty_errors.activate()
challenge_url = 'https://developer.automationanywhere.com/challenges/automationanywherelabs-customeronboarding.html'
file_url = 'https://aai-devportal-media.s3.us-west-2.amazonaws.com/challenges/customer-onboarding-challenge.csv'
excel = Excel()
request = HTTP()
file = FileSystem()
table = Tables()


class Customer_Onboard_Process:
    def __init__(self):
        pass

    @task
    def configure_browser(self):
        """Solve the RPA challenge"""
        browser.configure(
            browser_engine="chromium",
            screenshot="only-on-failure",
            headless=False)
        return None

    @task
    def open_page(self):
        """Open the challenge page"""
        page = browser.goto(challenge_url)
        page.wait_for_load_state(state='domcontentloaded')
        page.wait_for_selector(selector="//h2[contains(text(),'Customer Onboarding')]")
        return None

    @task
    def download_csv_file(self):
        """Download the input csv file"""
        request.download(file_url)
        return None

    @task
    def file_exists(self):
        """check if file downloaded or not"""
        exists = file.find_files("**/*challenge.csv")
        return exists

    @task
    def fill_form(self, file_data):
        """Read the data from the dataset"""
        if file_data:
            current_path = os.getcwd() + "\\"
            file_name = 'customer-onboarding-challenge.csv'
            full_path = current_path + file_name
            dataset = table.read_table_from_csv(header=True, path=full_path)
            for row in dataset:
                Customer_Onboard_Process.add_data(self, row)
            return None

    @task
    def add_data(self, row):
        """Insert the data in webpage"""
        page = browser.page()
        page.fill(selector="//input[contains(@id,'customerName')]", value=row['Company Name'])
        page.fill(selector="//input[contains(@id,'customerID')]", value=row['Customer ID'])
        page.fill(selector="//input[contains(@id,'primaryContact')]", value=row['Primary Contact'])
        page.fill(selector="//input[contains(@id,'street')]", value=row['Street Address'])
        page.fill(selector="//input[contains(@id,'city')]", value=row['City'])
        page.select_option(selector=f"//select[contains(@id,'state')]", value=row['State'])
        page.fill(selector="//input[contains(@id,'zip')]", value=row['Zip'])
        page.fill(selector="//input[contains(@id,'email')]", value=row['Email Address'])
        if row['Offers Discounts'] == 'YES':
            page.click(selector="//input[contains(@id,'activeDiscountYes')]")
        else:
            page.click(selector="//input[contains(@id,'activeDiscountNo')]")
        if row['Non-Disclosure On File'] == 'YES':
            page.click(selector="//input[contains(@id,'NDA')]")
        page.click("button:text('Register')")
        return None

    @task
    def take_screenshot(self):
        """Take the screenshot"""
        page = browser.page()
        page.wait_for_selector(selector="//div[@id='myModal']")
        page.screenshot(path='result.png')
        page.close()
        return None


if __name__ == '__main__':
    try:
        main = Customer_Onboard_Process()
        main.configure_browser()
        main.open_page()
        main.download_csv_file()
        is_file = main.file_exists()
        main.fill_form(is_file)
        main.take_screenshot()
        sys.exit()
    except Exception as e:
        print(e)
        sys.exit()
