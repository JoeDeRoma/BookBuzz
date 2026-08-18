import pandas as pd
import numpy as np
import itertools

fname = "Book Choice - March 2026.csv"
df = pd.read_csv(fname)
rank_cols = [col for col in df.columns if '[' in col and ']' in col]
candidates = [c.split('[')[-1].split(']')[0].strip() for c in rank_cols]
num_candidates = len(candidates)
num_voters = len(df)

ranking_data = df[rank_cols].apply(pd.to_numeric, errors='coerce')
ranks_matrix = np.array(ranking_data.values, dtype=float)

for v in range(num_voters):
    voter_ranks = ranks_matrix[v]
    ranked_indices = ~np.isnan(voter_ranks)
    num_ranked = np.sum(ranked_indices)
    
    if num_ranked == 0:
        ranks_matrix[v, :] = 1
    else:
        last_place_rank = num_ranked + 1
        ranks_matrix[v, ~ranked_indices] = last_place_rank

# Copeland: Net pairwise wins
copeland = np.zeros(num_candidates)
pairwise = np.zeros((num_candidates, num_candidates))

for v in range(num_voters):
    for i, j in itertools.permutations(range(num_candidates), 2):
        if ranks_matrix[v, i] < ranks_matrix[v, j]:
            pairwise[i, j] += 1.0

for i in range(num_candidates):
    for j in range(num_candidates):
        if i != j:
            if pairwise[i, j] > pairwise[j, i]:
                copeland[i] += 1
            elif pairwise[i, j] < pairwise[j, i]:
                copeland[i] -= 1

# Borda: 
# Candidates get points based on rank. Rank 1 = num_candidates pts, Rank 2 = num_candidates - 1 pts, etc.
borda = np.zeros(num_candidates)
for v in range(num_voters):
    for c in range(num_candidates):
        rank = ranks_matrix[v, c]
        borda[c] += (num_candidates - rank + 1)

print("Borda Scores:")
borda_results = sorted([(borda[i], candidates[i]) for i in range(num_candidates)], reverse=True)
for score, name in borda_results:
    print(f"{score}: {name}")

print("\nCopeland Net Wins:")
copeland_results = sorted([(copeland[i], candidates[i]) for i in range(num_candidates)], reverse=True)
for score, name in copeland_results:
    print(f"{score}: {name}")

print("\nTotal 1st Place Votes:")
first_place = np.zeros(num_candidates)
for v in range(num_voters):
    best_rank = np.min(ranks_matrix[v])
    for c in range(num_candidates):
        if ranks_matrix[v, c] == best_rank:
            # handle ties for 1st
            first_place[c] += 1
first_results = sorted([(first_place[i], candidates[i]) for i in range(num_candidates)], reverse=True)
for score, name in first_results:
    print(f"{score}: {name}")
