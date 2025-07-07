from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import time

def scrape_devsinc_jobs():
    # Set up Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Set up the driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Navigate to the URL
        print("Navigating to Devsinc careers page...")
        driver.get("https://apply.workable.com/devsinc-17/")
        
        # Wait for the page to load
        print("Waiting for page to load...")
        time.sleep(5)
        
        # Click "Show more" button until all jobs are loaded
        print("Looking for 'Show more' button...")
        
        # Keep clicking "Show more" until it's no longer available
        show_more_exists = True
        while show_more_exists:
            try:
                # Try multiple selectors to find the "Show more" button
                show_more_button = None
                
                # Method 1: Look for button with "Show more" text
                buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Show more')]")
                if buttons and buttons[0].is_displayed():
                    show_more_button = buttons[0]
                
                # Method 2: Look for button with class containing "more"
                if not show_more_button:
                    buttons = driver.find_elements(By.CSS_SELECTOR, "button[class*='more']")
                    if buttons and buttons[0].is_displayed():
                        show_more_button = buttons[0]
                
                # Method 3: Look for any element with "Show more" text
                if not show_more_button:
                    elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Show more')]")
                    for elem in elements:
                        if elem.is_displayed() and elem.is_enabled():
                            show_more_button = elem
                            break
                
                # If button found, click it
                if show_more_button:
                    # Scroll to the button to make sure it's in view
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", show_more_button)
                    time.sleep(1)
                    
                    # Try to click the button
                    print("Clicking 'Show more' button...")
                    try:
                        # Try normal click first
                        show_more_button.click()
                    except ElementClickInterceptedException:
                        # If the click is intercepted, try JavaScript click
                        print("Normal click intercepted, trying JavaScript click...")
                        driver.execute_script("arguments[0].click();", show_more_button)
                    
                    # Wait for new content to load
                    print("Waiting for new content to load...")
                    time.sleep(3)
                else:
                    # No button found, we're done
                    print("No 'Show more' button found. All jobs loaded.")
                    show_more_exists = False
            except Exception as e:
                print(f"Error when interacting with 'Show more' button: {e}")
                show_more_exists = False
        
        # Wait a bit longer to ensure all content is loaded
        time.sleep(5)
        
        # ROUND 1: Extract job titles (keeping your original code intact)
        print("ROUND 1: Extracting job titles...")
        
        job_titles = []
        
        # Try different CSS selectors
        selectors = [
            "a[role='presentation'] div[data-ui='job-title']",  # Based on your screenshots
            "div.styles_jobTitle__f9b9p", 
            "a.styles_jobTitle__f9b9p",
            "div[class*='jobTitle']",
            "a[class*='jobTitle']",
            "h2.job-title", 
            "div.whr-title",
            "h2, h3"  # Very generic fallback
        ]
        
        # Try each selector and collect all job titles found
        for selector in selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"Found {len(elements)} elements using selector: {selector}")
                for elem in elements:
                    title = elem.text.strip()
                    if title and len(title) > 5:
                        # Filter out elements that aren't job titles and page titles
                        excluded_terms = ["posted", "on-site", "full time", "location", "department", 
                                         "job openings", "current openings"]
                        if not any(x in title.lower() for x in excluded_terms):
                            job_titles.append(title)
                
                # If we found job titles with this selector, we'll use it and stop trying others
                if job_titles:
                    break
        
        # If still no job titles found, try XPath approach as a last resort
        if not job_titles:
            print("Trying XPath approach for job titles...")
            
            # Look for elements that match patterns seen in the screenshots
            patterns = ["Engineer", "Consultant", "Executive", "Developer", "Manager"]
            for pattern in patterns:
                xpath = f"//*/text()[contains(., '{pattern}')]/parent::*"
                elements = driver.find_elements(By.XPATH, xpath)
                for elem in elements:
                    title = elem.text.strip()
                    if title and len(title) > 5:
                        # Filter out non-job titles and page titles
                        excluded_terms = ["posted", "on-site", "full time", "location", "department", 
                                         "job openings", "current openings"]
                        if not any(x in title.lower() for x in excluded_terms):
                            job_titles.append(title)
        
        print(f"ROUND 1 COMPLETE: Found {len(job_titles)} job titles")
        
        # ROUND 2: Extract job links
        print("ROUND 2: Extracting job links...")
        
        job_links = []
        
        # Try multiple approaches to extract links
        
        # Approach 1: Find all links that look like job links
        link_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/j/']")
        print(f"Found {len(link_elements)} potential job links")
        
        for link_elem in link_elements:
            url = link_elem.get_attribute('href')
            if url and '/j/' in url:
                job_links.append(url)
        
        # Approach 2: If not enough links found, try another method
        if len(job_links) < len(job_titles):
            print("Not enough links found. Trying alternative approach...")
            
            # Get all anchor tags
            all_links = driver.find_elements(By.TAG_NAME, 'a')
            
            for link in all_links:
                try:
                    url = link.get_attribute('href')
                    if url and '/j/' in url and url not in job_links:
                        job_links.append(url)
                except:
                    pass
        
        # Approach 3: Direct JavaScript to get all job links
        if len(job_links) < len(job_titles):
            print("Still not enough links. Using JavaScript approach...")
            
            js_links = driver.execute_script("""
                return Array.from(document.querySelectorAll('a[href*="/j/"]')).map(a => a.href);
            """)
            
            for url in js_links:
                if url not in job_links:
                    job_links.append(url)
        
        # Debugging: Print all links on the page if we still don't have enough
        if len(job_links) < len(job_titles):
            print("DEBUG: Printing all links on the page")
            all_links = driver.find_elements(By.TAG_NAME, 'a')
            for i, link in enumerate(all_links):
                try:
                    href = link.get_attribute('href') or ''
                    text = link.text.strip()
                    print(f"Link {i}: Text='{text}', href='{href}'")
                except:
                    print(f"Link {i}: [Error getting attributes]")
        
        print(f"ROUND 2 COMPLETE: Found {len(job_links)} job links")
        
        # Match job titles and links
        # If we have fewer links than titles, some jobs will have empty links
        jobs_data = []
        
        # Use the minimum of titles and links
        min_count = min(len(job_titles), len(job_links))
        
        # Create jobs with both title and link
        for i in range(min_count):
            jobs_data.append((job_titles[i], job_links[i]))
        
        # Add remaining titles with empty links
        for i in range(min_count, len(job_titles)):
            jobs_data.append((job_titles[i], ""))
        
        print(f"Successfully matched {min_count} jobs with links")
        return jobs_data
    
    except Exception as e:
        print(f"Error during scraping: {e}")
        return []
    
    finally:
        # Always close the driver
        driver.quit()

def main():
    print("Scraping job titles and links from Devsinc using Selenium...")
    jobs_data = scrape_devsinc_jobs()
    
    if jobs_data:
        # Display all jobs found
        print(f"\nFound {len(jobs_data)} job listings at Devsinc:")
        for i, (title, url) in enumerate(jobs_data, 1):
            print(f"{i}. {title}")
            if url:
                print(f"   Link: {url}")
            else:
                print("   Link: [No link found]")
        
        # Append to the main jobs.csv file
        import os
        file_exists = os.path.exists("jobs.csv")
        
        with open("jobs.csv", "a", encoding="utf-8") as f:
            # Write header only if file doesn't exist
            if not file_exists:
                f.write("Job Title,Job URL,Source\n")
            
            # Write job data
            for title, url in jobs_data:
                escaped_title = title.replace('"', '""')
                f.write(f'"{escaped_title}","{url}","devsinc"\n')
        
        print(f"\nAll {len(jobs_data)} job listings appended to jobs.csv")
    else:
        print("\nNo job listings were found.")

if __name__ == "__main__":
    main()