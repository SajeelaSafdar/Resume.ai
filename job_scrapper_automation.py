import schedule
import time
import pandas as pd
from datetime import datetime
import subprocess
import os
from pathlib import Path

class JobScraperScheduler:
    def __init__(self):
        self.scraper_scripts = [
            "scrapers/afiniti.py",
            "scrapers/devsinc.py", 
            "scrapers/i2c.py",
            "scrapers/netsol.py",
            "scrapers/techlogix.py",
            "scrapers/tkxel.py"
        ]
        
        # Single combined file for all jobs
        self.jobs_file = "jobs.csv"
        
        os.makedirs("csv", exist_ok=True)
        
    def run_scraper(self, script_name):
        """Run a single scraper script"""
        try:
            print(f"Running {script_name}...")
            
            result = subprocess.run(['python', script_name], 
                                  capture_output=True, text=True, timeout=600, 
                                  cwd=os.getcwd())
            
            if result.returncode == 0:
                print(f"{script_name} completed successfully")
                return True
            else:
                print(f"{script_name} failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"{script_name} timed out after 10 minutes")
            return False
        except Exception as e:
            print(f"Error running {script_name}: {e}")
            return False
    
    def weekly_scraping_job(self):
        """Main function that runs weekly"""
        print("\n" + "="*60)
        print(f"WEEKLY JOB SCRAPING STARTED")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        with open(self.jobs_file, 'w', encoding='utf-8') as f:
            f.write("Job Title,Job URL,Source\n")
        print(f"Initialized {self.jobs_file}")
        
        successful_scrapers = 0
        total_scrapers = len(self.scraper_scripts)
        
        # Run each scraper
        for script in self.scraper_scripts:
            if os.path.exists(script):
                if self.run_scraper(script):
                    successful_scrapers += 1
                time.sleep(30)  # Wait 30 seconds between scrapers to avoid being blocked
            else:
                print(f"Scraper not found: {script}")
        
        print(f"\nScraping Summary:")
        print(f"   Successful: {successful_scrapers}/{total_scrapers}")
        print(f"   Failed: {total_scrapers - successful_scrapers}/{total_scrapers}")
    
    def start_scheduler(self):
        """Start the weekly scheduler"""
        print("Setting up weekly job scraping schedule...")
        print(f"Project directory: {os.getcwd()}")
        print(f"Jobs will be saved to: {os.path.abspath(self.jobs_file)}")
        
        # Schedule weekly scraping (every Monday at 2 AM)
        schedule.every().monday.at("02:00").do(self.weekly_scraping_job)
        
        print("Scheduler started!")
        print("Jobs will be scraped every Monday at 2:00 AM")
        print("Running initial test scraping...")
        print("Press Ctrl+C to stop the scheduler")
        
        # Run once immediately
        self.weekly_scraping_job()
        
        # Keep the scheduler running
        while True:
            schedule.run_pending()
            time.sleep(60)  

if __name__ == "__main__":
    print("Job Scraper Automation System")
    print("=" * 50)
    
    scheduler = JobScraperScheduler()
    
    try:
        scheduler.start_scheduler()
    except KeyboardInterrupt:
        print("\nScheduler stopped by user")
        print("Goodbye!")