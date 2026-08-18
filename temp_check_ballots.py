import pandas as pd
import numpy as np
from collections import Counter
df = pd.read_csv("Book Choice - March 2026.csv")
rank_cols = [col for col in df.columns if '[' in col and ']' in col]
name_col = None
for col in df.columns:
    if "discord tag" in col.lower() or "full name" in col.lower() or "name" in col.lower():
        name_col = col
        break

for i in range(len(df)):
    row = df.iloc[i]
    name = row[name_col] if name_col else f"Voter {i}"
    ranks = pd.to_numeric(row[rank_cols], errors='coerce').dropna().values
    print(f"Voter: {name}")
    print(f"  Ranks given: {sorted(ranks)}")
    issues = []
    if len(ranks) < 5:
        issues.append(f"Ranked {len(ranks)} books")
    if len(ranks) > 0 and min(ranks) != 1:
        issues.append(f"Starts at {min(ranks)}")
    if len(ranks) > 0:
        sorted_ranks = sorted(ranks)
        for j in range(1, len(sorted_ranks)):
            if sorted_ranks[j] > sorted_ranks[j-1] + 1 and sorted_ranks[j] != sorted_ranks[j-1]:
                issues.append(f"Skipped {sorted_ranks[j-1]}->{sorted_ranks[j]}")
        counts = Counter(sorted_ranks)
        dupes = [k for k,v in counts.items() if v > 1]
        if dupes:
            issues.append(f"Duplicate ranks {dupes}")
        if max(ranks) > len(rank_cols):
             issues.append(f"Ranked {max(ranks)} > {len(rank_cols)} candidates")
    if not issues:
        issues.append("None")
    print(f"  Issues: {', '.join(issues)}")
