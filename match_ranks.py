import csv
import re
import os

march_file = 'Book Choice - March 2026.csv'
rank_file = 'the_greatest_books_since_1976.csv'
output_file = 'March 2026 GreatestBooks Rankings.csv'

# Extract books
poll_books: list[str] = []
with open(march_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    headers = next(reader)
    for h in headers:
        m = re.search(r'\[(.*?)\]', h)
        if m:
            poll_books.append(m.group(1).strip())

# Load rankings
rankings = {}
with open(rank_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Save title lowercase for case-insensitive matching
        title = row['Title'].strip()
        rankings[title.lower()] = {
            'Title': title,
            'Global Rank': row['Global Rank'],
            'Position': row['Position']
        }

# Match and write output
with open(output_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Book', 'GreatestBooks Global Rank', 'Top 500 Position'])
    
    for b in poll_books:
        matched = False
        # Exact match
        if b.lower() in rankings:
            r = rankings[b.lower()]
            writer.writerow([b, r['Global Rank'], r['Position']])
            matched = True
        else:
            # Try finding a partial match just in case
            for r_title, r_data in rankings.items():
                if r_title == b.lower() or r_title.startswith(b.lower() + ":") or r_title.startswith(b.lower() + " "):
                   writer.writerow([b, r_data['Global Rank'], r_data['Position']])
                   matched = True
                   break
            
            if not matched:
                writer.writerow([b, 'Unranked', 'Unranked'])

print(f"Done! Extracted {len(poll_books)} books. Wrote to {output_file}")
