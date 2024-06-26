import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.get("https://www.linkedin.com/jobs/search?keywords=Engenheiro%20De%20Software&location=Portugal&geoId=&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0")
driver.maximize_window()

wait = WebDriverWait(driver, 10)

with open('./assets/jobs_data.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["job_title", "company_name", "location", "time_posted", "experience_level", "job_type"])

    collected_jobs = 0
    try:
        while collected_jobs < 1000:
            jobs = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.base-card.base-card--link.base-search-card.base-search-card--link.job-search-card')))
            for job in jobs[collected_jobs:]:
                driver.execute_script("arguments[0].scrollIntoView(true);", job)

                job_title = job.find_element(By.CSS_SELECTOR, 'h3.base-search-card__title').text.strip()
                company_name = job.find_element(By.CSS_SELECTOR, 'h4.base-search-card__subtitle').text.strip()
                location = job.find_element(By.CSS_SELECTOR, 'span.job-search-card__location').text.strip()
                time_posted_elements = job.find_elements(By.CSS_SELECTOR, 'time')
                time_posted = time_posted_elements[0].get_attribute('datetime') if time_posted_elements else "N/A"
                
                try:
                    anchor = job.find_element(By.CSS_SELECTOR, 'a.base-card__full-link')
                    driver.execute_script("arguments[0].click();", anchor)
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.description__job-criteria-list')))
                    time.sleep(2) # Wait 2 second
                except TimeoutException:
                    print("CRITERIA LIST NOT FOUND.")
                except Exception as e:
                    print("ANCHOR NOT CLICKABLE:", e)

                try:
                    criteria_list = driver.find_elements(By.CSS_SELECTOR, 'ul.description__job-criteria-list li')
                    experience_level = criteria_list[0].text.split('\n')[1] if len(criteria_list) > 0 else "N/A"
                    job_type = criteria_list[1].text.split('\n')[1] if len(criteria_list) > 1 else "N/A"
                except Exception as e:
                    print("ERROR EXTRACTING CRITERIA LIST DETAILS:", e)
                    experience_level = "N/A"
                    job_type = "N/A"

                writer.writerow([job_title, company_name, location, time_posted, experience_level, job_type])

                collected_jobs += 1
                if collected_jobs >= 1000:
                    break

            try:
                more_button = driver.find_element(By.CSS_SELECTOR, 'button.infinite-scroller__show-more-button')
                if more_button:
                    driver.execute_script("arguments[0].click();", more_button)
                    time.sleep(1)
            except Exception as e:
                print("Não foi possível encontrar o botão 'Ver mais vagas':", e)

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
    finally:
        driver.quit()
