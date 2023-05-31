import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import re

# Read marks from CSV file
markalar = pd.read_csv("keywords.csv", header=None)
markalar = markalar[0].tolist()

# Start WebDriver
driver = webdriver.Chrome()

# Create a DataFrame to store the results
email_df = pd.DataFrame(columns=["Marka", "Email", "Phone", "Website"])

# Regex edits for phone and website
phone_regex = re.compile(r'\+[\d\s\-\(\)]{7,}')
domain_regex = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')

try:
    # Google search for each keyword
    for marka in markalar:
        query = f"\"Email\" inurl:{marka}"
        driver.get(f"https://www.google.com/search?q={query}&gl=us&hl=en")

        email_set = set()
        phone_set = set()
        website_set = set()

        # Check if Google reCAPTCHA page appears and wait for user to complete it before proceeding.
        while "About this page" in driver.page_source:
            print("Google reCAPTCHA detected. Please complete it to proceed.")
            time.sleep(20)

        # Browse results pages
        while True:
            time.sleep(2)  # To wait for the page to load
            page_source = driver.page_source
            emails = re.findall(r'[\w.-]+@[\w.-]+\.\w+', page_source)
            phones = phone_regex.findall(page_source)
            websites = domain_regex.findall(page_source)

            for email in emails:
                email_set.add(email)
            for phone in phones:
                phone_set.add(phone)
            for website in websites:
                website_set.add(website)

            # Switch to the next page or stop the process
            try:
                next_button = driver.find_element_by_link_text("Next")
                next_button.click()
            except Exception as e:
                break

        # Add emails, phone numbers and websites to DataFrame
        for email in email_set:
            phone = next(iter(phone_set), None)
            website = next(iter(website_set), None)
            email_df = email_df.append({"Marka": marka, "Email": email, "Phone": phone, "Website": website}, ignore_index=True)
            if phone in phone_set:
                phone_set.remove(phone)
            if website in website_set:
                website_set.remove(website)

except Exception as e:
    print(f"Error: {e}")
finally:
    # Save emails, phone numbers and websites to output.csv
    email_df.to_csv("output.csv", index=False)

    # Close WebDriver
    driver.quit()