import itertools
from typing import List, Dict, Any, Tuple, Optional, Set
import numpy as np
from engine.ballot_parser import Ballot


class PairwiseMatchup:
    def __init__(self, cand_a: str, cand_b: str, votes_a: float, votes_b: float):
        self.cand_a = cand_a
        self.cand_b = cand_b
        self.votes_a = votes_a
        self.votes_b = votes_b
        self.margin_a = votes_a - votes_b
        self.winner = cand_a if votes_a > votes_b else (cand_b if votes_b > votes_a else "Tie")


class LockingStep:
    def __init__(
        self,
        winner: str,
        loser: str,
        margin: float,
        votes_for: float,
        votes_against: float,
        locked: bool,
        reason: str = ""
    ):
        self.winner = winner
        self.loser = loser
        self.margin = margin
        self.votes_for = votes_for
        self.votes_against = votes_against
        self.locked = locked
        self.reason = reason


class StandingItem:
    def __init__(
        self,
        rank: int,
        candidates: List[str],
        score: int,
        is_tie: bool,
        defeat_notes: List[str]
    ):
        self.rank = rank
        self.candidates = candidates
        self.score = score
        self.is_tie = is_tie
        self.defeat_notes = defeat_notes


class RankedPairsResult:
    def __init__(
        self,
        candidates: List[str],
        included_ballots_count: int,
        excluded_ballots_count: int,
        pairwise_matrix: np.ndarray,
        standings: List[StandingItem],
        locking_steps: List[LockingStep],
        winner_name: str,
    ):
        self.candidates = candidates
        self.num_candidates = len(candidates)
        self.included_ballots_count = included_ballots_count
        self.excluded_ballots_count = excluded_ballots_count
        self.pairwise_matrix = pairwise_matrix
        self.standings = standings
        self.locking_steps = locking_steps
        self.winner_name = winner_name

    def get_pairwise_matchup(self, cand_a: str, cand_b: str) -> Optional[PairwiseMatchup]:
        if cand_a not in self.candidates or cand_b not in self.candidates:
            return None
        i = self.candidates.index(cand_a)
        j = self.candidates.index(cand_b)
        return PairwiseMatchup(cand_a, cand_b, self.pairwise_matrix[i, j], self.pairwise_matrix[j, i])


def solve_ranked_pairs(
    candidates: List[str],
    ballots: List[Ballot]
) -> RankedPairsResult:
    """
    Executes Ranked Pairs (Tideman method) Condorcet ranking on the provided ballots.
    Only ballots with ballot.included == True are counted.
    """
    included_ballots = [b for b in ballots if b.included]
    num_voters = len(included_ballots)
    num_candidates = len(candidates)

    if num_candidates == 0:
        raise ValueError("No candidates found.")

    if num_voters == 0:
        # Fallback if no ballots included
        standings = [
            StandingItem(rank=i+1, candidates=[cand], score=0, is_tie=False, defeat_notes=[])
            for i, cand in enumerate(candidates)
        ]
        return RankedPairsResult(
            candidates=candidates,
            included_ballots_count=0,
            excluded_ballots_count=len(ballots),
            pairwise_matrix=np.zeros((num_candidates, num_candidates)),
            standings=standings,
            locking_steps=[],
            winner_name=candidates[0] if candidates else "None"
        )

    # 1. Build rank matrix (voters x candidates)
    ranks_matrix = np.zeros((num_voters, num_candidates), dtype=float)

    for v_idx, ballot in enumerate(included_ballots):
        num_ranked = len(ballot.ranked_books)
        if num_ranked == 0:
            # Everyone ties for 1st
            ranks_matrix[v_idx, :] = 1.0
        else:
            last_place_rank = float(num_ranked + 1)
            for c_idx, candidate in enumerate(candidates):
                rank_val = ballot.ranks.get(candidate)
                if rank_val is not None:
                    ranks_matrix[v_idx, c_idx] = float(rank_val)
                else:
                    ranks_matrix[v_idx, c_idx] = last_place_rank

    # 2. Pairwise Matrix Calculation
    pairwise = np.zeros((num_candidates, num_candidates), dtype=float)
    for v in range(num_voters):
        for i, j in itertools.permutations(range(num_candidates), 2):
            if ranks_matrix[v, i] < ranks_matrix[v, j]:
                pairwise[i, j] += 1.0

    # 3. Sort Pairs by Margin, then Winning Votes
    list_p = sorted(
        [
            (pairwise[i, j] - pairwise[j, i], pairwise[i, j], i, j)
            for i, j in itertools.permutations(range(num_candidates), 2)
            if pairwise[i, j] > pairwise[j, i]
        ],
        reverse=True
    )

    # 4. Locking Graph and Cycle Detection
    lk = np.zeros((num_candidates, num_candidates), dtype=bool)

    def has_path(start: int, end: int, g: np.ndarray) -> bool:
        queue = [start]
        visited = {start}
        while queue:
            curr = queue.pop()
            if curr == end:
                return True
            for n in range(num_candidates):
                if g[curr, n] and n not in visited:
                    visited.add(n)
                    queue.append(n)
        return False

    locking_steps: List[LockingStep] = []
    for margin, votes_for, w, l in list_p:
        winner_name = candidates[w]
        loser_name = candidates[l]
        votes_against = pairwise[l, w]
        if not has_path(l, w, lk):
            lk[w, l] = True
            locking_steps.append(
                LockingStep(
                    winner=winner_name,
                    loser=loser_name,
                    margin=margin,
                    votes_for=votes_for,
                    votes_against=votes_against,
                    locked=True,
                    reason=f"Locked: '{winner_name}' over '{loser_name}' (+{margin} margin)"
                )
            )
        else:
            locking_steps.append(
                LockingStep(
                    winner=winner_name,
                    loser=loser_name,
                    margin=margin,
                    votes_for=votes_for,
                    votes_against=votes_against,
                    locked=False,
                    reason=f"Skipped (Cycle): '{winner_name}' over '{loser_name}' (+{margin} margin)"
                )
            )

    # 5. Compute RP Reachability Scores
    rp_scores: Dict[int, int] = {}
    for i in range(num_candidates):
        reachable: Set[int] = set()
        queue = [i]
        while queue:
            curr = queue.pop()
            for n in range(num_candidates):
                if lk[curr, n] and n not in reachable:
                    reachable.add(n)
                    queue.append(n)
        rp_scores[i] = len(reachable)

    sorted_unique_scores = sorted(list(set(rp_scores.values())), reverse=True)

    # Group into standings
    ordered_groups: List[Tuple[int, List[int], int]] = []
    current_rank = 1
    for score in sorted_unique_scores:
        cands_with_score = [i for i, s in rp_scores.items() if s == score]
        ordered_groups.append((current_rank, cands_with_score, score))
        current_rank += len(cands_with_score)

    standings: List[StandingItem] = []
    prev_group_cands: List[int] = []

    for rank, cands_indices, score in ordered_groups:
        is_tie = len(cands_indices) > 1
        cand_names = [candidates[i] for i in cands_indices]
        defeat_notes: List[str] = []

        if prev_group_cands:
            for cand_idx in cands_indices:
                for prev_cand_idx in prev_group_cands:
                    v_for = pairwise[cand_idx, prev_cand_idx]
                    v_against = pairwise[prev_cand_idx, cand_idx]
                    diff = v_against - v_for
                    cand_n = candidates[cand_idx]
                    prev_n = candidates[prev_cand_idx]
                    if diff > 0:
                        defeat_notes.append(
                            f"Lost head-to-head to '{prev_n}' by {diff:g} votes ({v_for:g} vs {v_against:g})"
                        )
                    elif diff == 0:
                        defeat_notes.append(
                            f"Tied head-to-head with '{prev_n}' ({v_for:g} vs {v_against:g})"
                        )
                    else:
                        defeat_notes.append(
                            f"Beat '{prev_n}' head-to-head by {-diff:g} votes ({v_for:g} vs {v_against:g})"
                        )

        standings.append(
            StandingItem(
                rank=rank,
                candidates=cand_names,
                score=score,
                is_tie=is_tie,
                defeat_notes=defeat_notes
            )
        )
        prev_group_cands = cands_indices

    winner_name = standings[0].candidates[0] if standings and standings[0].candidates else "None"
    if standings and standings[0].is_tie:
        winner_name = f"Tie: {', '.join(standings[0].candidates)}"

    return RankedPairsResult(
        candidates=candidates,
        included_ballots_count=num_voters,
        excluded_ballots_count=len(ballots) - num_voters,
        pairwise_matrix=pairwise,
        standings=standings,
        locking_steps=locking_steps,
        winner_name=winner_name
    )
