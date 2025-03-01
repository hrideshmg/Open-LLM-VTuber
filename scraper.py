import requests
from bs4 import BeautifulSoup
import json
import time

def scrape_olabs():
    base_url = "https://www.olabs.edu.in/"
    
    # Get the main page
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all subject divs with class "subj"
    subject_divs = soup.find_all('div', class_='subj')
    
    results = {}
    
    # Loop through each subject
    for subject_div in subject_divs[:3]:  # Only first 3 subjects (Physics, Chemistry, Biology)
        subject_link = subject_div.find('a')
        if subject_link:
            subject_name = subject_link.text.strip()
            subject_url = base_url + subject_link['href'] if not subject_link['href'].startswith('http') else subject_link['href']
            
            print(f"Scraping {subject_name} from {subject_url}")
            
            # Get the subject page
            subject_response = requests.get(subject_url)
            subject_soup = BeautifulSoup(subject_response.text, 'html.parser')
            
            # Find all experiment divs
            experiment_divs = subject_soup.find_all('div', class_='col-xs-12 col-sm-6 col-md-3 exptPadng')
            
            experiments = []
            
            # Loop through each experiment
            for experiment_div in experiment_divs:
                experiment_link = experiment_div.find('a')
                p_tag= experiment_div.find('p')
                if experiment_link and p_tag:
                    experiment_name = p_tag.text.strip()
                    experiment_url = base_url + experiment_link['href'] if not experiment_link['href'].startswith('http') else experiment_link['href']
                    
                    experiments.append({
                        "name": experiment_name,
                        "link": experiment_url
                    })
            
            results[subject_name] = experiments
            
            # Add a small delay to be respectful to the server
            time.sleep(1)
    
    # Save results to JSON file
    with open('olabs_experiments.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    
    print(f"Scraping complete. Data saved to olabs_experiments.json")
    return results

if __name__ == "__main__":
    scrape_olabs()
