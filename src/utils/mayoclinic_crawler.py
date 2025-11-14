import requests
from bs4 import BeautifulSoup
import time
import urllib.parse

HEADERS = {
    'User-Agent': 'MedicalResearchBot/1.0 (research@example.com)'
}

def search_mayo_clinic(query):
    """Search Mayo Clinic and return the first disease page URL"""
    search_url = f"https://www.mayoclinic.org/search/search-results?q={urllib.parse.quote(query)}"
    
    try:
        response = requests.get(search_url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the first disease result
        result = soup.find('a', href=lambda href: href and '/diseases-conditions/' in href)
        if result:
            return "https://www.mayoclinic.org" + result['href'] if not result['href'].startswith('http') else result['href']
    except Exception as e:
        print(f"Mayo Clinic search error: {e}")
    return None

def scrape_page_content(url):
    """Scrape Mayo Clinic content under h2 headers containing specific medical keywords only."""
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        main_content = (
            soup.find('div', {'id': 'main-content'}) or
            soup.find('main') or
            soup.find('article') or
            soup.find('body')
        )
        if not main_content:
            raise Exception("Main content container not found.")

        unwanted_classes = [
            'myc-subscription-form', 'myc-subscription-step-wrapper', 
            'requestappt', 'newsletter', 'myc-subscription-form-ending',
            'contentbox', 'acces-list-container', 'social-share'
        ]
        
        for cls in unwanted_classes:
            for tag in main_content.find_all(attrs={'class': lambda x: x and cls in x}):
                tag.decompose()

        # Remove newsletter signup forms and ads
        for tag in main_content.find_all('div', id=lambda x: x and ('ad-' in x or 'newsletter' in x.lower())):
            tag.decompose()

        form_h2 = main_content.find('h2', id='formTitle')
        if form_h2:
            parent_block = form_h2.find_parent('div')
            if parent_block:
                parent_block.decompose()

        # MayoClinic main function: causes & treatments
        allowed_keywords = [
            "symptom", "symptoms",
            "cause", "causes",
            "treatment", "treatments",
            "complication", "complications"
        ]

        content_by_section = {}
        current_section = None
        current_content = []
        collecting = False

        # Find all h2 tags and their following content
        for element in main_content.find_all(['h2', 'h3', 'p', 'ul', 'ol'], recursive=True):
            if element.name == 'h2':
                # Save previous section if we were collecting
                if collecting and current_section and current_content:
                    content_by_section[current_section] = '\n'.join(current_content).strip()
                
                # Check if this h2 contains any keywords
                h2_text = element.get_text(strip=True).lower()
                
                # Exact keyword matching - header must contain the exact keyword
                keyword_found = False
                
                for keyword in allowed_keywords:
                    # Check if the keyword appears as a complete word/phrase
                    if keyword == h2_text or h2_text.startswith(keyword + " ") or h2_text.endswith(" " + keyword) or (" " + keyword + " ") in h2_text:
                        keyword_found = True
                        break
                
                if keyword_found:
                    collecting = True
                    current_section = element.get_text(strip=True)
                    current_content = []
                else:
                    collecting = False
                    current_section = None
                    current_content = []
            
            elif collecting and element.name in ['h3', 'p', 'ul', 'ol']:
                # Only collect content if we're in a relevant section
                text = element.get_text(strip=True)
                if text:  # Only add non-empty text
                    current_content.append(text)

        # Last section
        if collecting and current_section and current_content:
            content_by_section[current_section] = '\n'.join(current_content).strip()

        # Limit each section to 180 words
        for section_title, content in content_by_section.items():
            words = content.split()
            if len(words) > 180:
                truncated_content = ' '.join(words[:180]) + '...'
                content_by_section[section_title] = truncated_content

        return content_by_section

    except Exception as e:
        print(f"Scraping error for {url}: {e}")
        return None

def crawl_mayoclinic_entity(query):
    """Main function to get medical information for a query from Mayo Clinic"""
    print(f"\nSearching for: {query}")
    
    mayo_url = search_mayo_clinic(query)
    results = {}
    
    if mayo_url:
        print(f"Found Mayo Clinic page: {mayo_url}")
        content_dict = scrape_page_content(mayo_url)
        if content_dict:
            results = {'url': mayo_url}
            results.update(content_dict)
            
        else:
            print("No relevant content found")
        time.sleep(0.5)
    else:
        print("No Mayo Clinic page found for this query")
    
    return results
