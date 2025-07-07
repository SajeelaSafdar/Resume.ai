from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import time

def scrape_i2c_jobs():
    # Set up Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Run in headless mode (uncomment to run in background)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Set up the driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Navigate to the URL
        print("Navigating to i2c Inc careers page...")
        driver.get("https://careers.i2cinc.com/en/sites/i2csitelhr/jobs")
        
        # Wait for the page to load
        print("Waiting for page to load...")
        time.sleep(5)
        
        # Click "Show More Results" button until all jobs are loaded
        print("Looking for 'Show More Results' button...")
        
        # Keep clicking "Show More Results" until it's no longer available
        show_more_exists = True
        click_count = 0
        
        while show_more_exists:
            try:
                # Try multiple selectors to find the "Show More Results" button
                show_more_button = None
                
                # Method 1: Look for button with "Show More Results" text
                buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Show More Results')]")
                if buttons and buttons[0].is_displayed():
                    show_more_button = buttons[0]
                
                # Method 2: Look for button with "Show more results" text (case variation)
                if not show_more_button:
                    buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Show more results')]")
                    if buttons and buttons[0].is_displayed():
                        show_more_button = buttons[0]
                
                # Method 3: Look for any clickable element with "Show More Results" text
                if not show_more_button:
                    elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Show More Results') or contains(text(), 'Show more results')]")
                    for elem in elements:
                        if elem.is_displayed() and elem.is_enabled():
                            show_more_button = elem
                            break
                
                # Method 4: Look for button with class containing "more" or "load" or "show"
                if not show_more_button:
                    buttons = driver.find_elements(By.CSS_SELECTOR, "button[class*='more'], button[class*='load'], button[class*='show']")
                    for btn in buttons:
                        if btn.is_displayed() and btn.is_enabled() and ('more' in btn.text.lower() or 'show' in btn.text.lower()):
                            show_more_button = btn
                            break
                
                # If button found, click it
                if show_more_button:
                    click_count += 1
                    print(f"Clicking 'Show More Results' button (attempt {click_count})...")
                    
                    # Scroll to the button to make sure it's in view
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", show_more_button)
                    time.sleep(1)
                    
                    # Try to click the button
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
                    
                    # Safety check to prevent infinite loops
                    if click_count > 20:
                        print("Maximum click attempts reached. Stopping.")
                        show_more_exists = False
                else:
                    # No button found, we're done
                    print("No 'Show More Results' button found. All jobs loaded.")
                    show_more_exists = False
                    
            except Exception as e:
                print(f"Error when interacting with 'Show More Results' button: {e}")
                show_more_exists = False
        
        # Wait a bit longer to ensure all content is loaded
        time.sleep(5)
        
        # ROUND 1: Extract job titles (keeping your original code intact)
        print("ROUND 1: Extracting job titles...")
        
        job_titles = []
        
        # Since we know there are 50 job links, let's try to extract titles from those links
        print("First, trying to extract titles from the job link elements themselves...")
        job_link_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/job/']")
        
        if job_link_elements:
            print(f"Found {len(job_link_elements)} job link elements, trying to extract titles from them...")
            for i, elem in enumerate(job_link_elements):
                try:
                    # Try getting text directly from the link
                    title = elem.text.strip()
                    if title and len(title) >= 3:
                        excluded_terms = ["apply now", "organizations", "posting dates", "locations", 
                                        "posted", "on-site", "full time", "show more", "search", "filter"]
                        if not any(x in title.lower() for x in excluded_terms):
                            job_titles.append(title)
                            print(f"  Found title from link {i+1}: {title}")
                except Exception as e:
                    continue
        
        # If that didn't work, try looking for titles in child elements of job links
        if len(job_titles) < 10:  # If we didn't find many titles
            print("Trying to find titles in child elements of job links...")
            for i, elem in enumerate(job_link_elements):
                try:
                    # Look for titles in various child elements
                    child_selectors = ["h2", "h3", "h4", "span", "div", ".title", "[class*='title']", "[class*='job']"]
                    for selector in child_selectors:
                        children = elem.find_elements(By.CSS_SELECTOR, selector)
                        for child in children:
                            title = child.text.strip()
                            if title and len(title) >= 3:
                                excluded_terms = ["apply now", "organizations", "posting dates", "locations", 
                                                "posted", "on-site", "full time", "show more", "search", "filter"]
                                if not any(x in title.lower() for x in excluded_terms):
                                    job_titles.append(title)
                                    print(f"  Found title from child {selector} in link {i+1}: {title}")
                                    break
                        if title and len(title) >= 3:  # Break if we found a title
                            break
                except Exception as e:
                    continue
        
        # If still not enough, try different approaches
        if len(job_titles) < 10:
            print("Trying different CSS selectors for job titles...")
            
            # Try different CSS selectors to find job titles
            selectors = [
                "div[class*='job'] h2",    # H2 inside job containers
                "div[class*='job'] h3",    # H3 inside job containers  
                "div[class*='position'] h2", # H2 inside position containers
                "div[class*='position'] h3", # H3 inside position containers
                ".job-title",              # Direct job title class
                "[data-testid*='job-title']", # Test ID based
                "h2[class*='title']",      # H2 with title class
                "h3[class*='title']",      # H3 with title class
                "[class*='title'][class*='job']", # Elements with both title and job classes
                ".position-title",         # Position title class
                "[aria-label*='job']",     # Elements with job in aria-label
                "[title*='job']",          # Elements with job in title attribute
            ]
            
            # Try each selector and collect all job titles found
            for selector in selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"Found {len(elements)} elements using selector: {selector}")
                    for elem in elements:
                        try:
                            title = elem.text.strip()
                            if title and len(title) >= 3:
                                # Filter out elements that aren't job titles
                                excluded_terms = ["apply now", "organizations", "posting dates", "locations",
                                                "posted", "on-site", "full time", "location", 
                                                "department", "job openings", "current openings", "show more", 
                                                "search", "filter", "sort", "home", "about", "contact", 
                                                "privacy", "benefits", "life at", "login", "follow us"]
                                if not any(x in title.lower() for x in excluded_terms):
                                    job_titles.append(title)
                                    print(f"  Found title: {title}")
                        except Exception as e:
                            continue
                    
                    # If we found job titles with this selector, break
                    if len(job_titles) >= 10:
                        break
        
        # If still no job titles found, try XPath approach as a last resort
        if len(job_titles) < 10:
            print("Trying XPath approach for job titles...")
            
            # Look for elements that match job patterns
            job_patterns = ["Engineer", "Manager", "Developer", "Analyst", "Coordinator", 
                           "Specialist", "Consultant", "Director", "Lead", "Senior", 
                           "Associate", "Executive", "Representative", "Marketing", "Sales"]
            
            for pattern in job_patterns:
                xpath = f"//*/text()[contains(., '{pattern}')]/parent::*"
                elements = driver.find_elements(By.XPATH, xpath)
                for elem in elements:
                    try:
                        title = elem.text.strip()
                        if title and len(title) >= 3:
                            # Filter out non-job titles
                            excluded_terms = ["apply now", "organizations", "posting dates", "locations",
                                            "posted", "on-site", "full time", "location", 
                                            "department", "job openings", "current openings", "show more", 
                                            "search", "filter", "sort", "home", "about", "contact"]
                            if not any(x in title.lower() for x in excluded_terms):
                                job_titles.append(title)
                                print(f"  Found title with pattern {pattern}: {title}")
                    except:
                        continue
        
        # Last resort: try to get all visible text that looks like job titles
        if len(job_titles) < 10:
            print("Last resort: scanning all visible text for job titles...")
            
            # Get all elements with text
            text_elements = driver.find_elements(By.XPATH, "//*[string-length(normalize-space(text())) > 5]")
            
            for elem in text_elements:
                try:
                    text = elem.text.strip()
                    if text and len(text) >= 3 and len(text) < 100:  # Reasonable length for job titles
                        # Check if it looks like a job title
                        job_keywords = ["engineer", "manager", "developer", "analyst", "coordinator", 
                                      "specialist", "consultant", "director", "lead", "senior", 
                                      "associate", "executive", "representative", "marketing", "sales",
                                      "content", "product", "customer", "service", "software"]
                        
                        if any(keyword in text.lower() for keyword in job_keywords):
                            # Always add, even if duplicate
                            excluded_terms = ["apply now", "organizations", "posting dates", "locations",
                                            "posted", "on-site", "full time", "location", 
                                            "department", "job openings", "current openings", "show more", 
                                            "search", "filter", "sort", "home", "about", "contact", 
                                            "privacy", "benefits", "life at", "login", "follow us"]
                            if not any(x in text.lower() for x in excluded_terms):
                                job_titles.append(text)
                                print(f"  Found potential title from text scan: {text}")
                except:
                    continue
        
        # Don't remove duplicates - keep all job titles as found
        print(f"ROUND 1 COMPLETE: Found {len(job_titles)} job titles")
        
        # Print job titles for debugging
        for i, title in enumerate(job_titles, 1):
            print(f"  {i}. {title}")
        
        # ROUND 2: Extract job links
        print("ROUND 2: Extracting job links...")
        
        job_links = []
        
        # Try multiple approaches to extract links
        
        # Approach 1: Find all links that look like job links
        link_selectors = [
            "a[href*='/job/']",     # Links containing /job/
            "a[href*='/position/']", # Links containing /position/
            "a[href*='/career/']",   # Links containing /career/
            "a[href*='/apply/']",    # Links containing /apply/
        ]
        
        for selector in link_selectors:
            link_elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if link_elements:
                print(f"Found {len(link_elements)} potential job links with selector: {selector}")
                
                for link_elem in link_elements:
                    try:
                        url = link_elem.get_attribute('href')
                        if url and url not in job_links:
                            job_links.append(url)
                    except:
                        continue
                
                if job_links:
                    break
        
        # Approach 2: If not enough links found, try another method
        if len(job_links) < len(job_titles):
            print("Not enough links found. Trying alternative approach...")
            
            # Get all anchor tags and filter
            all_links = driver.find_elements(By.TAG_NAME, 'a')
            
            for link in all_links:
                try:
                    url = link.get_attribute('href')
                    if url:
                        # Check if URL looks like a job link
                        job_url_patterns = ['/job/', '/position/', '/career/', '/apply/']
                        if any(pattern in url for pattern in job_url_patterns):
                            # Always add, even if duplicate
                            job_links.append(url)
                except:
                    pass
        
        # Approach 3: Direct JavaScript to get all job links
        if len(job_links) < len(job_titles):
            print("Still not enough links. Using JavaScript approach...")
            
            try:
                js_links = driver.execute_script("""
                    var links = [];
                    var anchors = document.querySelectorAll('a[href]');
                    for (var i = 0; i < anchors.length; i++) {
                        var href = anchors[i].href;
                        if (href.includes('/job/') || href.includes('/position/') || 
                            href.includes('/career/') || href.includes('/apply/')) {
                            links.push(href);
                        }
                    }
                    return links;
                """)
                
                for url in js_links:
                    # Always add, even if duplicate
                    job_links.append(url)
            except Exception as e:
                print(f"JavaScript approach failed: {e}")
        
        print(f"ROUND 2 COMPLETE: Found {len(job_links)} job links")
        
        # Print job links for debugging
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
    print("Scraping job titles and links from i2c Inc using Selenium...")
    jobs_data = scrape_i2c_jobs()
    
    if jobs_data:
        # Display all jobs found
        print(f"\nFound {len(jobs_data)} job listings at i2c Inc:")
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
                f.write(f'"{escaped_title}","{url}","i2c"\n')
        
        print(f"\nAll {len(jobs_data)} job listings appended to jobs.csv")
    else:
        print("\nNo job listings were found.")

if __name__ == "__main__":
    main()