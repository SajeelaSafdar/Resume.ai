from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import time

def scrape_techlogix_jobs():
    # Set up Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Run in headless mode (uncomment to run in background)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Set up the driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Navigate to the URL
        print("Navigating to Techlogix careers page...")
        driver.get("https://techlogix.com/careers/lahore/")
        
        # Wait for the page to load
        print("Waiting for page to load...")
        time.sleep(5)
        
        print("Extracting job information...")
        
        # ROUND 1: Extract job titles
        print("ROUND 1: Extracting job titles...")
        
        job_titles = []
        
        # Try multiple approaches to find job titles
        
        # Approach 1: Look for clickable job title elements
        title_selectors = [
            "a[href*='job']",         # Links containing 'job'
            "a[href*='career']",      # Links containing 'career'
            "a[href*='position']",    # Links containing 'position'
            "h3 a",                   # H3 tags with links
            "h2 a",                   # H2 tags with links
            "h4 a",                   # H4 tags with links
        ]
        
        for selector in title_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"Found {len(elements)} elements using selector: {selector}")
                for elem in elements:
                    try:
                        title = elem.text.strip()
                        if title and len(title) > 2:
                            job_titles.append(title)
                            print(f"  Found job title: {title}")
                    except Exception as e:
                        continue
                
                if job_titles:
                    break
        
        # Approach 2: Look for job titles in heading tags
        if not job_titles:
            print("No titles found with links. Trying heading tags...")
            
            heading_selectors = ["h3", "h2", "h4", "h5"]
            
            for selector in heading_selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"Found {len(elements)} {selector} elements")
                    for elem in elements:
                        try:
                            title = elem.text.strip()
                            if title and len(title) > 2:
                                job_titles.append(title)
                                print(f"  Found job title in {selector}: {title}")
                        except Exception as e:
                            continue
                
                if job_titles:
                    break
        
        # Approach 3: Look for any clickable elements that might be jobs
        if not job_titles:
            print("No titles found in headings. Trying all clickable elements...")
            
            clickable_elements = driver.find_elements(By.CSS_SELECTOR, "a[href]")
            
            for elem in clickable_elements:
                try:
                    title = elem.text.strip()
                    if title and len(title) > 2:
                        job_titles.append(title)
                        print(f"  Found clickable title: {title}")
                except Exception as e:
                    continue
        
        print(f"ROUND 1 COMPLETE: Found {len(job_titles)} job titles")
        
        # Print all job titles for debugging
        for i, title in enumerate(job_titles, 1):
            print(f"  {i}. {title}")
        
        # ROUND 2: Extract job links
        print("ROUND 2: Extracting job links...")
        
        job_links = []
        
        # Try to find job links
        link_selectors = [
            "a[href*='job']",         # Links containing 'job'
            "a[href*='career']",      # Links containing 'career'
            "a[href*='position']",    # Links containing 'position'
            "a[href*='apply']",       # Links containing 'apply'
        ]
        
        for selector in link_selectors:
            link_elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if link_elements:
                print(f"Found {len(link_elements)} potential job links with selector: {selector}")
                
                for link_elem in link_elements:
                    try:
                        url = link_elem.get_attribute('href')
                        if url:
                            job_links.append(url)
                            print(f"  Found job link: {url}")
                    except:
                        continue
                
                if job_links:
                    break
        
        # If no specific job links found, try to find any links that might be related to jobs
        if not job_links:
            print("No specific job links found. Looking for any relevant links...")
            
            all_links = driver.find_elements(By.CSS_SELECTOR, "a[href]")
            
            for link in all_links:
                try:
                    url = link.get_attribute('href')
                    if url and url.startswith('http'):
                        job_links.append(url)
                        print(f"  Found link: {url}")
                except:
                    continue
        
        print(f"ROUND 2 COMPLETE: Found {len(job_links)} job links")
        
        # Print all job links for debugging
        for i, link in enumerate(job_links, 1):
            print(f"  {i}. {link}")
        
        # Match job titles and links
        jobs_data = []
        
        # Use the minimum of titles and links for perfect matching
        min_count = min(len(job_titles), len(job_links))
        
        # Create jobs with both title and link
        for i in range(min_count):
            jobs_data.append((job_titles[i], job_links[i]))
        
        # Add remaining titles with empty links
        for i in range(min_count, len(job_titles)):
            jobs_data.append((job_titles[i], ""))
        
        print(f"Successfully matched {min_count} jobs with links, {len(job_titles) - min_count} jobs without links")
        
        return jobs_data
    
    except Exception as e:
        print(f"Error during scraping: {e}")
        return []
    
    finally:
        # Always close the driver
        driver.quit()

def main():
    print("Scraping job titles and links from Techlogix using Selenium...")
    jobs_data = scrape_techlogix_jobs()
    
    if jobs_data:
        # Display all jobs found
        print(f"\nFound {len(jobs_data)} job listings at Techlogix:")
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
                f.write(f'"{escaped_title}","{url}","techlogix"\n')
        
        print(f"\nAll {len(jobs_data)} job listings appended to jobs.csv")
    else:
        print("\nNo job listings were found.")
if __name__ == "__main__":
    main()