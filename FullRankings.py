import pandas as pd
import numpy as np
import sys
import os
import itertools
from typing import Any

# UNRANKED value placeholder
UNRANKED = 999

def solve_full_rankings(csv_file, df):
    # --- 1. Column Identification ---
    rank_cols = [col for col in df.columns if '[' in col and ']' in col and ("rank" in col.lower() or "preference" in col.lower())]

    if not rank_cols:
        print("Error: Could not find any columns match the ranking pattern.")
        return

    candidates = []
    for c in rank_cols:
        candidates.append(c.split('[')[-1].split(']')[0].strip())
            
    num_candidates = len(candidates)
    num_voters = len(df)
    
    print(f"Candidates ({num_candidates}):")
    for i, c in enumerate(candidates):
        print(f"  {i + 1}: {c}")
    print(f"\nTotal Ballots: {num_voters}")

    # --- 2. Data Parsing ---
    ranking_data: Any = df[rank_cols].apply(pd.to_numeric, errors='coerce')
    ranks_matrix = np.array(ranking_data.values, dtype=float)

    # For each voter, unranked books should be tied for last place.
    # If a voter ranks N books, the remaining (num_candidates - N) books 
    # should all receive the rank (N + 1).
    for v in range(num_voters):
        voter_ranks = ranks_matrix[v]
        ranked_indices = ~np.isnan(voter_ranks)
        num_ranked = np.sum(ranked_indices)
        
        if num_ranked == 0:
            ranks_matrix[v, :] = 1
        else:
            last_place_rank = num_ranked + 1
            ranks_matrix[v, ~ranked_indices] = last_place_rank

    # --- 3. Pairwise Matrix Calculation ---
    pairwise = np.zeros((num_candidates, num_candidates), dtype=float)
    for v in range(num_voters):
        for i, j in itertools.permutations(range(num_candidates), 2):
            if ranks_matrix[v, i] < ranks_matrix[v, j]: # type: ignore
                pairwise[i, j] += 1.0

    print("\n" + "="*40)
    print("FULL RANKINGS")
    print("="*40)

    # ==========================
    # Ranked Pairs Full Ranking
    # ==========================
    # Ranked Pairs standard sorts primarily by margin of victory, then winning votes.
    list_p = sorted([(pairwise[i, j]-pairwise[j, i], pairwise[i, j], i, j) for i, j in itertools.permutations(range(num_candidates), 2) if pairwise[i, j] > pairwise[j, i]], reverse=True)
    lk = np.zeros((num_candidates, num_candidates), dtype=bool)
    
    def path(start, end, g):
        q, v = [start], {start}
        while q:
            c = q.pop()
            if c == end: return True
            for n in range(num_candidates):
                if g[c][n] and n not in v:
                    v.add(n)
                    q.append(n)
        return False
        
    print("\n--- Ranked Pairs Method ---")
    print("Selection Process (Locking pairs in order of margin):")
    for margin, votes_for, w, l in list_p:
        if not path(l, w, lk): 
            lk[w, l] = True
            print(f"  Locked: '{candidates[w]}' over '{candidates[l]}' (Margin: {margin})")
        else:
            print(f"  Skipped (Cycle): '{candidates[w]}' over '{candidates[l]}' (Margin: {margin})")
            
    rp_scores = {}
    for i in range(num_candidates):
        # Count how many nodes this candidate has a path to
        reachable = set()
        q = [i]
        while q:
            curr = q.pop()
            for n in range(num_candidates):
                if lk[curr, n] and n not in reachable:
                    reachable.add(n)
                    q.append(n)
        rp_scores[i] = len(reachable)
        
    sorted_unique_scores = sorted(list(set(rp_scores.values())), reverse=True)
    
    print("\nFinal Ranked Pairs Ranking:")
    ordered_candidates = []
    current_rank = 1
    for score in sorted_unique_scores:
        cands_with_score = [i for i, s in rp_scores.items() if np.isclose(s, score)]
        ordered_candidates.append((current_rank, cands_with_score))
        current_rank += len(cands_with_score)
        
    for rank, cands in ordered_candidates:
        if len(cands) == 1:
            print(f"{rank}. {candidates[cands[0]]}")
        else:
            names = [candidates[i] for i in cands]
            print(f"{rank}. Tie: {', '.join(names)}")




def main():
    fname = None
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    else:
        import glob
        files = glob.glob("Book Choice - *.csv")
        if files:
            files.sort(reverse=True)
            fname = files[0]
        else:
            fname = "Book Choice - March 2026.csv"
            
    if not os.path.exists(fname):
        print(f"File '{fname}' not found.")
        return
        
    for enc in ['utf-8-sig', 'cp1252', 'latin1']:
        try:
            df = pd.read_csv(fname, encoding=enc)
            solve_full_rankings(fname, df)
            return
        except ValueError:
            pass
        except Exception as e:
            import traceback
            traceback.print_exc()
            continue
    print(f"Error: Could not read file or calculate winners consistently. Make sure formatting is correct.")

if __name__ == "__main__":
    main()
