from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import time

def scrape_tkxel_jobs():
    # Set up Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Run in headless mode (uncomment to run in background)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Set up the driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Navigate to the URL
        print("Navigating to Tkxel careers page...")
        driver.get("https://jobs.tkxel.com/jobs/Careers")
        
        # Wait for the page to load
        print("Waiting for page to load...")
        time.sleep(5)
        
        # First, let's scroll down to load all content
        print("Scrolling to load all content...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait to load page
            time.sleep(2)
            
            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        print("Finished scrolling. Looking for 'MORE' buttons (like '3 MORE', '5 MORE', etc.)...")
        
        # Look for "n MORE" buttons pattern
        more_button_exists = True
        click_count = 0
        
        while more_button_exists and click_count < 15:
            try:
                more_button = None
                
                # Method 1: Look for buttons/elements with "MORE" text (case insensitive)
                more_elements = driver.find_elements(By.XPATH, "//*[contains(translate(text(), 'MORE', 'more'), 'more')]")
                
                for elem in more_elements:
                    try:
                        text = elem.text.strip()
                        # Check if it matches pattern like "3 MORE", "5 MORE", etc.
                        if 'more' in text.lower() and any(char.isdigit() for char in text):
                            if elem.is_displayed() and elem.is_enabled():
                                more_button = elem
                                print(f"Found MORE button with text: '{text}'")
                                break
                    except:
                        continue
                
                # Method 2: Look specifically for clickable elements with number + MORE pattern
                if not more_button:
                    patterns = [f"{i} MORE" for i in range(1, 21)]  # Check for 1 MORE to 20 MORE
                    patterns.extend([f"{i} more" for i in range(1, 21)])  # lowercase version
                    
                    for pattern in patterns:
                        elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{pattern}')]")
                        for elem in elements:
                            if elem.is_displayed() and elem.is_enabled():
                                more_button = elem
                                print(f"Found MORE button with pattern: '{pattern}'")
                                break
                        if more_button:
                            break
                
                # Method 3: Look for buttons with specific classes that might contain MORE
                if not more_button:
                    button_elements = driver.find_elements(By.TAG_NAME, "button")
                    for btn in button_elements:
                        try:
                            text = btn.text.strip()
                            if text and 'more' in text.lower() and any(char.isdigit() for char in text):
                                if btn.is_displayed() and btn.is_enabled():
                                    more_button = btn
                                    print(f"Found MORE button element: '{text}'")
                                    break
                        except:
                            continue
                
                # Method 4: Look for clickable divs, spans, or other elements with MORE text
                if not more_button:
                    clickable_tags = ["div", "span", "a", "p"]
                    for tag in clickable_tags:
                        elements = driver.find_elements(By.TAG_NAME, tag)
                        for elem in elements:
                            try:
                                text = elem.text.strip()
                                if text and 'more' in text.lower() and any(char.isdigit() for char in text):
                                    # Check if element is clickable (has onclick, role=button, or is inside a clickable parent)
                                    if (elem.get_attribute('onclick') or 
                                        elem.get_attribute('role') == 'button' or
                                        elem.find_element(By.XPATH, "./ancestor::*[@onclick or @role='button']")):
                                        if elem.is_displayed():
                                            more_button = elem
                                            print(f"Found clickable MORE element: '{text}'")
                                            break
                            except:
                                continue
                        if more_button:
                            break
                
                if more_button:
                    click_count += 1
                    button_text = more_button.text.strip()
                    print(f"Clicking MORE button '{button_text}' (attempt {click_count})...")
                    
                    # Scroll to button to ensure it's visible
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", more_button)
                    time.sleep(1)
                    
                    try:
                        # Try normal click first
                        more_button.click()
                        print(f"Successfully clicked '{button_text}' button")
                    except ElementClickInterceptedException:
                        print("Normal click intercepted, trying JavaScript click...")
                        driver.execute_script("arguments[0].click();", more_button)
                        print(f"Successfully JavaScript clicked '{button_text}' button")
                    except Exception as click_error:
                        print(f"Both click methods failed: {click_error}")
                        more_button_exists = False
                        continue
                    
                    # Wait for new content to load
                    print("Waiting for new content to load...")
                    time.sleep(4)
                    
                    # Scroll down a bit to see if new content appeared
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    
                else:
                    print("No MORE button found. All jobs should be loaded.")
                    more_button_exists = False
                    
            except Exception as e:
                print(f"Error when interacting with MORE button: {e}")
                more_button_exists = False
        
        # Final scroll to make sure all content is visible
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        # ROUND 1: Extract job titles
        print("ROUND 1: Extracting job titles...")
        
        job_titles = []
        
        # Since we found 35 job links, let's extract titles from each link element directly
        print("Extracting job titles from the job link elements...")
        
        job_link_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='job']")
        print(f"Found {len(job_link_elements)} job link elements")
        
        for i, link_elem in enumerate(job_link_elements):
            try:
                # Method 1: Try to get the title from the link's text content
                title = link_elem.text.strip()
                
                # Method 2: If no text in link, look for title in nearby elements
                if not title or len(title) < 3:
                    # Look for title in parent or sibling elements
                    parent = link_elem.find_element(By.XPATH, "./..")
                    title = parent.text.strip()
                
                # Method 3: Look for specific child elements that contain the title
                if not title or len(title) < 3:
                    child_selectors = ["h3", "h4", "span", "div", ".title", "[class*='title']"]
                    for selector in child_selectors:
                        try:
                            child_elements = link_elem.find_elements(By.CSS_SELECTOR, selector)
                            for child in child_elements:
                                child_text = child.text.strip()
                                if child_text and len(child_text) > 3:
                                    title = child_text
                                    break
                            if title and len(title) > 3:
                                break
                        except:
                            continue
                
                # Method 4: Try to extract from the URL itself as last resort
                if not title or len(title) < 3:
                    url = link_elem.get_attribute('href')
                    if url:
                        # Extract job title from URL (e.g., "Senior-Software-Engineer")
                        url_parts = url.split('/')
                        for part in url_parts:
                            if '-' in part and '?' not in part and len(part) > 10:
                                # Convert URL format to readable title
                                potential_title = part.replace('-', ' ').replace('_', ' ')
                                if any(keyword in potential_title.lower() for keyword in 
                                      ["engineer", "manager", "developer", "analyst", "specialist",
                                       "consultant", "director", "lead", "senior", "associate",
                                       "executive", "coordinator", "representative", "intern"]):
                                    title = potential_title
                                    break
                
                # Clean and validate the title
                if title and len(title) > 3:
                    # Remove unwanted text
                    excluded_terms = ["lahore, pakistan", "remote job", "full time", "temporary",
                                    "bahawalpur", "filter by", "all", "view openings", "current openings"]
                    
                    # Clean the title
                    lines = title.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and len(line) > 3:
                            if not any(term in line.lower() for term in excluded_terms):
                                # Check if this looks like a job title
                                job_keywords = ["engineer", "manager", "developer", "analyst", "specialist",
                                              "consultant", "director", "lead", "senior", "associate",
                                              "executive", "coordinator", "representative", "intern",
                                              "designer", "architect", "administrator", "accountant",
                                              "writer", "support", "sales", "seo", "sqa", "python",
                                              "javascript", "blazor", "maui", "azure", "data"]
                                
                                if any(keyword in line.lower() for keyword in job_keywords):
                                    job_titles.append(line)
                                    print(f"  Found job title {i+1}: {line}")
                                    break
                    
            except Exception as e:
                print(f"  Error extracting title from link {i+1}: {e}")
                continue
        
        # If we still don't have enough titles, try the original h3 approach as backup
        if len(job_titles) < len(job_link_elements) * 0.5:  # If we have less than 50% of expected titles
            print("Not enough titles found from links. Trying backup h3 approach...")
            
            h3_elements = driver.find_elements(By.CSS_SELECTOR, "h3")
            for elem in h3_elements:
                try:
                    title = elem.text.strip()
                    if title and len(title) > 5:
                        # Filter out non-job titles
                        excluded_terms = ["filter by", "all", "remote jobs", "full time", "temporary",
                                        "accounting", "engineering", "it services", "current openings",
                                        "join us", "lahore, pakistan", "bahawalpur", "looking to apply"]
                        
                        if not any(x in title.lower() for x in excluded_terms):
                            job_keywords = ["engineer", "manager", "developer", "analyst", "specialist",
                                          "consultant", "director", "lead", "senior", "associate",
                                          "executive", "coordinator", "representative", "intern",
                                          "designer", "architect", "administrator", "accountant",
                                          "writer", "support", "sales", "seo", "sqa"]
                            
                            if any(keyword in title.lower() for keyword in job_keywords):
                                if title not in job_titles:  # Avoid duplicates
                                    job_titles.append(title)
                                    print(f"  Found backup job title: {title}")
                except Exception as e:
                    continue
        
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
                            excluded_url_parts = ["filter", "search", "home", "about", "contact"]
                            if not any(part in url.lower() for part in excluded_url_parts):
                                job_links.append(url)
                                print(f"  Found job link: {url}")
                    except:
                        continue
                
                if job_links:
                    break
        
        # If no specific job links found, try to find any clickable job elements
        if not job_links:
            print("No specific job links found. Looking for clickable job elements...")
            
            # Look for clickable elements that contain job titles
            for title in job_titles:
                try:
                    # Find elements containing this job title that are clickable
                    clickable_elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{title}')]/ancestor-or-self::a[@href]")
                    
                    for elem in clickable_elements:
                        url = elem.get_attribute('href')
                        if url and url not in job_links:
                            job_links.append(url)
                            print(f"  Found clickable link for '{title}': {url}")
                            break
                except:
                    continue
        
        print(f"ROUND 2 COMPLETE: Found {len(job_links)} job links")
        
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
    print("Scraping job titles and links from Tkxel using Selenium...")
    jobs_data = scrape_tkxel_jobs()
    
    if jobs_data:
        # Display all jobs found
        print(f"\nFound {len(jobs_data)} job listings at Tkxel:")
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
                f.write(f'"{escaped_title}","{url}","tkxel"\n')
        
        print(f"\nAll {len(jobs_data)} job listings appended to jobs.csv")
    else:
        print("\nNo job listings were found.")

if __name__ == "__main__":
    main()