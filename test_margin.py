import pandas as pd
import numpy as np
import itertools

df = pd.read_csv('Book Choice - March 2026.csv', encoding='utf-8-sig')
rank_cols = [c for c in df.columns if '[' in c and ']' in c]
candidates = [c.split('[')[-1].split(']')[0].strip() for c in rank_cols]
num_candidates = len(candidates)
num_voters = len(df)

ranking_data = df[rank_cols].apply(pd.to_numeric, errors='coerce')
ranks = np.array(ranking_data.values, dtype=float)

for v in range(num_voters):
    r = ranks[v]
    ranked = ~np.isnan(r)
    n = np.sum(ranked)
    if n == 0:
        ranks[v, :] = 1
    else:
        ranks[v, ~ranked] = n + 1

pairwise = np.zeros((num_candidates, num_candidates), dtype=float)
for v in range(num_voters):
    for i, j in itertools.permutations(range(num_candidates), 2):
        if ranks[v, i] < ranks[v, j]:
            pairwise[i, j] += 1

piranesi = candidates.index('Piranesi')
remains = candidates.index('The Remains of the Day')

print('--- Matchup Result ---')
print(f'The Remains of the Day: {pairwise[remains, piranesi]}')
print(f'Piranesi: {pairwise[piranesi, remains]}')
