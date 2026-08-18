import pandas as pd
import numpy as np
import sys
import os
import itertools
import math
from typing import Any


# UNRANKED value should be higher than any possible specific rank (usually 1-10)
UNRANKED = 999

def solve_voting(csv_file, df):
    """
    Solves for winners using multiple voting methods.
    """
    # --- 1. Column Identification ---
    # Find all columns that follow the pattern "Please rank ... [Book Name]"
    rank_cols = [col for col in df.columns if '[' in col and ']' in col and ("rank" in col.lower() or "preference" in col.lower())]

    if not rank_cols:
        print("Error: Could not find any columns match the ranking pattern.")
        return

    candidates = []
    for c in rank_cols:
        # Extract candidate name between brackets (handles smart quotes and other chars)
        candidates.append(c.split('[')[-1].split(']')[0].strip())
            
    num_candidates = len(candidates)
    num_voters = len(df)

    # --- 2. Data Parsing ---
    # Convert all ranking columns to numeric at once (handling NaNs and bad data)
    # Extract just the digits first to handle cases like "1 (Most Preferred)"
    for col in rank_cols:
        df[col] = df[col].astype(str).str.extract(r'(\d+)')[0]
        
    ranking_data: Any = df[rank_cols].apply(pd.to_numeric, errors='coerce')
    ranks_matrix = np.array(ranking_data.values, dtype=float)

    name_col = None
    for col in df.columns:
        if "discord tag" in col.lower() or "full name" in col.lower() or "name" in col.lower():
            name_col = col
            break

    invalid_voters = []

    # For each voter, unranked books should be tied for last place.
    # If a voter ranks N books, the remaining (num_candidates - N) books 
    # should all receive the rank (N + 1). (Not an arbitrary 999).
    for v in range(num_voters):
        voter_ranks = ranks_matrix[v]
        ranked_indices = ~np.isnan(voter_ranks)
        num_ranked = np.sum(ranked_indices)
        
        voter_name = str(df.iloc[v][name_col]) if name_col else f"Voter {v+1}"
        
        # Validation
        if num_ranked > 0:
            assigned_ranks = sorted(voter_ranks[ranked_indices])
            if assigned_ranks[0] != 1:
                invalid_voters.append(f"- {voter_name}: Rankings started at {int(assigned_ranks[0])} instead of 1.")
            else:
                for k in range(1, len(assigned_ranks)):
                    if assigned_ranks[k] > assigned_ranks[k-1] + 1 and assigned_ranks[k] != assigned_ranks[k-1]:
                        invalid_voters.append(f"- {voter_name}: Skipped ranking between {int(assigned_ranks[k-1])} and {int(assigned_ranks[k])}.")
                        break
        
        if num_ranked == 0:
            # If they ranked nothing, everyone ties for 1st
            ranks_matrix[v, :] = 1
        else:
            # The rank they get is exactly the next available rank integer
            # Example: Ranked 1, 2, 3. Next rank is 4.
            last_place_rank = num_ranked + 1
            ranks_matrix[v, ~ranked_indices] = last_place_rank
            
    if invalid_voters:
        print("\n" + "!"*40)
        print("INVALID BALLOTS DETECTED (Rules match: no skips, start at 1)")
        print("!"*40)
        for issue in invalid_voters:
            print(issue)
        print("!"*40 + "\n")
            
    # UNRANKED threshold is no longer 999 because unranked items are now just "last place" ranks.
    # Methods that need to distinguish explicitly explicitly unranked books can look for ties at the max rank,
    # but the math for most methods now naturally flows without "filtering out" UNRANKED.

    # --- 3. Pairwise Matrix Calculation ---
    pairwise = np.zeros((num_candidates, num_candidates), dtype=float)
    for v in range(num_voters):
        for i, j in itertools.permutations(range(num_candidates), 2):
            if ranks_matrix[v, i] < ranks_matrix[v, j]: # type: ignore
                pairwise[i, j] += 1.0
    print("\n" + "="*40)
    print("PAIRWISE HEAD-TO-HEAD MARGINS")
    print("="*40)
    for i in range(num_candidates):
        for j in range(i+1, num_candidates):
            print(f"{candidates[i]} vs {candidates[j]}: {pairwise[i, j]} to {pairwise[j, i]}")
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
        
    for margin, votes_for, w, l in list_p:
        if not path(l, w, lk): 
            lk[w, l] = True
            
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
        
    previous_rank_cands = []
    for rank, cands in ordered_candidates:
        if len(cands) == 1:
            cand = cands[0]
            print(f"{rank}. {candidates[cand]}")
            if previous_rank_cands:
                for prev_cand in previous_rank_cands:
                    votes_for = pairwise[cand, prev_cand]
                    votes_against = pairwise[prev_cand, cand]
                    diff = votes_against - votes_for
                    print(f"      -> Lost head-to-head to '{candidates[prev_cand]}' by {diff} votes ({votes_for} vs {votes_against})")
        else:
            names = [candidates[i] for i in cands]
            print(f"{rank}. Tie: {', '.join(names)}")
            if previous_rank_cands:
                for cand in cands:
                    for prev_cand in previous_rank_cands:
                        votes_for = pairwise[cand, prev_cand]
                        votes_against = pairwise[prev_cand, cand]
                        diff = votes_against - votes_for
                        print(f"      -> '{candidates[cand]}' lost head-to-head to '{candidates[prev_cand]}' by {diff} votes ({votes_for} vs {votes_against})")
        previous_rank_cands = cands




def main():
    fname = None
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    else:
        import glob
        files = glob.glob("Book Choice - *.csv")
        if files:
            files.sort(reverse=True) # Usually gets the latest month
            fname = files[0]
        else:
            fname = "Book Choice - Summer 2026.csv"
            
    if not os.path.exists(fname):
        print(f"File '{fname}' not found.")
        return
        
    for enc in ['utf-8-sig', 'cp1252', 'latin1']:
        try:
            df = pd.read_csv(fname, encoding=enc)
            solve_voting(fname, df)
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
