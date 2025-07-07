from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import time

def scrape_afiniti_jobs():
    # Set up Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Run in headless mode (uncomment to run in background)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Set up the driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Navigate to the URL
        print("Navigating to Afiniti careers page...")
        driver.get("https://afiniti.com/jobs/")
        
        # Wait for the page to load
        print("Waiting for page to load...")
        time.sleep(5)
        
        # Scroll down to ensure all content is loaded (in case of infinite scroll)
        print("Scrolling to load all content...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        
        while scroll_attempts < 5:  # Limit scroll attempts
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait to load page
            time.sleep(2)
            
            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempts += 1
            else:
                scroll_attempts = 0  # Reset if new content loaded
            last_height = new_height
        
        print("Finished scrolling. Now extracting job information...")
        
        # ROUND 1: Extract job titles
        print("ROUND 1: Extracting job titles...")
        
        job_titles = []
        
        # Based on the images, job titles appear to be in a table structure
        # Let's try multiple approaches to find them
        
        # Approach 1: Look for job titles in table rows or similar structures
        title_selectors = [
            "tr td:first-child",  # First column of table rows (most likely for job titles)
            ".job-title",         # Direct job title class
            "[class*='job-title']", # Class containing job-title
            "h3",                 # Job titles might be in h3 tags
            "h4",                 # Or h4 tags
            "h2",                 # Or h2 tags
            "[class*='position']", # Class containing position
            "[class*='role']",    # Class containing role
        ]
        
        for selector in title_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"Found {len(elements)} elements using selector: {selector}")
                for elem in elements:
                    try:
                        title = elem.text.strip()
                        if title and len(title) > 5:
                            # Filter out non-job titles
                            excluded_terms = ["select location", "all locations", "ireland", "pakistan", 
                                            "romania", "turkey", "open positions", "we're always looking",
                                            "location", "date", "apply", "careers", "contact us"]
                            
                            # Check if it's likely a job title
                            if not any(x in title.lower() for x in excluded_terms):
                                # Look for job-like keywords or patterns
                                job_keywords = ["manager", "engineer", "developer", "analyst", "specialist",
                                              "consultant", "director", "lead", "senior", "associate",
                                              "executive", "coordinator", "representative", "scientist",
                                              "researcher", "administrator", "president", "vice president"]
                                
                                # Also accept titles that are reasonably long and don't contain excluded terms
                                # Always add the title, even if it's a duplicate
                                job_titles.append(title)
                                print(f"  Found job title: {title}")
                    except Exception as e:
                        continue
                
                # If we found a good number of titles, we can break
                if len(job_titles) >= 5:
                    break
        
        # Approach 2: If not enough titles found, try looking for clickable job elements
        if len(job_titles) < 5:
            print("Not enough titles found. Trying to find clickable job elements...")
            
            # Look for clickable elements that might be job titles
            clickable_selectors = [
                "a[href*='job']",     # Links containing 'job'
                "a[href*='position']", # Links containing 'position'
                "a[href*='career']",   # Links containing 'career'
                "tr a",               # Links within table rows
                "td a",               # Links within table cells
            ]
            
            for selector in clickable_selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"Found {len(elements)} clickable elements using selector: {selector}")
                    for elem in elements:
                        try:
                            title = elem.text.strip()
                            if title and len(title) > 5:
                                excluded_terms = ["select location", "all locations", "ireland", "pakistan", 
                                                "romania", "turkey", "open positions", "apply", "view",
                                                "location", "date", "careers", "contact us"]
                                
                                if not any(x in title.lower() for x in excluded_terms):
                                    job_keywords = ["manager", "engineer", "developer", "analyst", "specialist",
                                                  "consultant", "director", "lead", "senior", "associate",
                                                  "executive", "coordinator", "representative", "scientist",
                                                  "researcher", "administrator", "president", "intelligence"]
                                    
                                    if any(keyword in title.lower() for keyword in job_keywords):
                                        if title not in job_titles:  # Avoid duplicates
                                            job_titles.append(title)
                                            print(f"  Found clickable job title: {title}")
                        except Exception as e:
                            continue
                    
                    if len(job_titles) >= 10:
                        break
        
        # Approach 3: If still not enough, try comprehensive text scanning
        if len(job_titles) < 5:
            print("Still not enough titles. Trying comprehensive text scanning...")
            
            # Get all text elements and look for job-like content
            text_elements = driver.find_elements(By.XPATH, "//*[string-length(normalize-space(text())) > 5]")
            
            for elem in text_elements:
                try:
                    text = elem.text.strip()
                    if text and 8 < len(text) < 100:  # Reasonable length for job titles
                        # Check if it looks like a job title
                        job_keywords = ["manager", "engineer", "developer", "analyst", "specialist",
                                      "consultant", "director", "lead", "senior", "associate",
                                      "executive", "coordinator", "representative", "scientist",
                                      "researcher", "administrator", "president", "intelligence",
                                      "business intelligence", "data scientist", "data engineer"]
                        
                        if any(keyword in text.lower() for keyword in job_keywords):
                            excluded_terms = ["select location", "all locations", "ireland", "pakistan", 
                                            "romania", "turkey", "open positions", "we're always looking",
                                            "location", "date", "apply", "careers", "contact us",
                                            "05/", "04/", "06/", "2025"]  # Exclude dates
                            
                            if not any(x in text.lower() for x in excluded_terms):
                                # Always add, even if duplicate
                                job_titles.append(text)
                                print(f"  Found potential job title: {text}")
                except:
                    continue
        
        # Don't remove duplicates - keep all jobs as found
        job_titles = job_titles  # Keep original list without deduplication
        print(f"ROUND 1 COMPLETE: Found {len(job_titles)} job titles")
        
        # ROUND 2: Extract job links
        print("ROUND 2: Extracting job links...")
        
        job_links = []
        
        # Try to find job links
        link_selectors = [
            "a[href*='job']",     # Links containing 'job'
            "a[href*='position']", # Links containing 'position'
            "a[href*='career']",   # Links containing 'career'
            "a[href*='apply']",    # Links containing 'apply'
            "tr a",               # Links within table rows
            "td a",               # Links within table cells
        ]
        
        for selector in link_selectors:
            link_elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if link_elements:
                print(f"Found {len(link_elements)} potential job links with selector: {selector}")
                
                for link_elem in link_elements:
                    try:
                        url = link_elem.get_attribute('href')
                        if url and url not in job_links:
                            # Filter out non-job URLs
                            excluded_url_parts = ["contact", "about", "products", "testimonials", 
                                                 "news", "industries", "#", "javascript:", "mailto:"]
                            if not any(part in url.lower() for part in excluded_url_parts):
                                job_links.append(url)
                                print(f"  Found job link: {url}")
                    except:
                        continue
                
                if job_links:
                    break
        
        # If no specific job links found, try to create application links based on job titles
        if not job_links and job_titles:
            print("No direct job links found. Attempting to construct application links...")
            
            # Look for any apply buttons or similar elements
            apply_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Apply') or contains(text(), 'apply')]")
            
            for elem in apply_elements:
                try:
                    # Check if it's a link
                    if elem.tag_name == 'a':
                        url = elem.get_attribute('href')
                        if url:
                            job_links.append(url)
                    else:
                        # Check if it's inside a link
                        parent_link = elem.find_element(By.XPATH, "./ancestor::a[@href]")
                        if parent_link:
                            url = parent_link.get_attribute('href')
                            if url and url not in job_links:
                                job_links.append(url)
                except:
                    continue
        
        print(f"ROUND 2 COMPLETE: Found {len(job_links)} job links")
        
        # Match job titles and links
        jobs_data = []
        
        # If we have both titles and links
        if job_titles and job_links:
            # Use the minimum of titles and links for perfect matching
            min_count = min(len(job_titles), len(job_links))
            
            # Create jobs with both title and link
            for i in range(min_count):
                jobs_data.append((job_titles[i], job_links[i]))
            
            # Add remaining titles with empty links
            for i in range(min_count, len(job_titles)):
                jobs_data.append((job_titles[i], ""))
                
        elif job_titles:
            # Only titles found, no links
            for title in job_titles:
                jobs_data.append((title, ""))
        
        print(f"Successfully extracted {len(jobs_data)} job listings")
        
        return jobs_data
    
    except Exception as e:
        print(f"Error during scraping: {e}")
        return []
    
    finally:
        # Always close the driver
        driver.quit()

def main():
    print("Scraping job titles and links from Afiniti using Selenium...")
    jobs_data = scrape_afiniti_jobs()
    
    if jobs_data:
        # Display all jobs found
        print(f"\nFound {len(jobs_data)} job listings at Afiniti:")
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
                f.write(f'"{escaped_title}","{url}","afiniti"\n')
        
        print(f"\nAll {len(jobs_data)} job listings appended to jobs.csv")
    else:
        print("\nNo job listings were found.")

if __name__ == "__main__":
    main()