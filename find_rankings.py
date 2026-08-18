import urllib.request
import urllib.parse
import re
import csv
import time
import html

input_csv = 'March 2026 GreatestBooks Rankings.csv'

books_to_check = []
with open(input_csv, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    headers = next(reader)
    for row in reader:
        if row[1] == 'Unranked':
            books_to_check.append(row[0])

print(f"Checking {len(books_to_check)} unranked books...")

for book in books_to_check:
    print(f"\nSearching for: {book}")
    query = urllib.parse.quote_plus(book)
    search_url = f"https://thegreatestbooks.org/search?SearchableText={query}"
    
    try:
        req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            html_content = response.read().decode('utf-8')
            
            # Simple regex to find results. The results usually have a link to the item.
            # E.g. <h4><a href="/items/1234">Book Title</a></h4>
            results = re.findall(r'<h4[^>]*>\s*<a href="(/items/\d+)">([^<]+)</a>', html_content, re.IGNORECASE)
            
            if results:
                print(f"Found search results for {book}:")
                for i, (link, title) in enumerate(results):
                    if i >= 3: break
                    print(f"  - {html.unescape(title)} (URL: {link})")
                    
                    # Fetch item page
                    item_url = f"https://thegreatestbooks.org{link}"
                    item_req = urllib.request.Request(item_url, headers={'User-Agent': 'Mozilla/5.0'})
                    try:
                        with urllib.request.urlopen(item_req) as item_resp:
                            item_html = item_resp.read().decode('utf-8')
                            
                            # looking for rank info in the item page. 
                            # Usually there's something like "Global Rank: 400" or similar
                            # Let's extract anything that looks like a rank or score
                            # Or we specifically care about "The Greatest Books Since 1976" rank
                            list_matches = re.findall(r'<a href="(/lists/[^"]+)">([^<]+)</a>[^<]*<span[^>]*>(\d+)</span>', item_html)
                            for l_url, l_name, l_rank in list_matches:
                                print(f"    * List: {html.unescape(l_name)} -> Rank: {l_rank}")
                                
                    except Exception as e:
                        print(f"    Error fetching item page: {e}")
            else:
                print(f"No results found for {book}.")
                
    except Exception as e:
        print(f"Error fetching search results: {e}")
        
    time.sleep(1)
