import os
import io
import zipfile
import re
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
import pandas as pd
import numpy as np


class Ballot:
    def __init__(
        self,
        index: int,
        voter_name: str,
        timestamp: Optional[str],
        ranks: Dict[str, Optional[int]],  # book_name -> rank (1-based integer or None)
        all_candidates: List[str],
        min_ranked_required: int = 5,
    ):
        self.index = index
        self.voter_name = voter_name
        self.timestamp = timestamp or ""
        self.ranks = ranks
        self.all_candidates = all_candidates
        self.min_ranked_required = min_ranked_required
        
        # Computed properties
        self.ranked_books = {k: v for k, v in ranks.items() if v is not None}
        self.unranked_books = [k for k in all_candidates if k not in self.ranked_books]
        self.sorted_ranks = sorted([(v, k) for k, v in self.ranked_books.items()])
        self.num_ranked = len(self.ranked_books)
        
        # Compliance validation
        self.issues: List[str] = []
        self._validate()
        self.is_compliant = len(self.issues) == 0
        self.included = True  # Checked by default

    def _validate(self):
        if self.num_ranked == 0:
            self.issues.append("No books were ranked.")
            return

        if self.num_ranked < self.min_ranked_required:
            self.issues.append(f"Ranked {self.num_ranked} books (minimum {self.min_ranked_required} required).")

        assigned_numbers = [r for r, _ in self.sorted_ranks]

        if assigned_numbers and assigned_numbers[0] != 1:
            self.issues.append(f"Rankings started at {assigned_numbers[0]} instead of 1.")

        # Check for skipped ranks
        for i in range(1, len(assigned_numbers)):
            prev, curr = assigned_numbers[i - 1], assigned_numbers[i]
            if curr > prev + 1 and curr != prev:
                self.issues.append(f"Skipped rank between {prev} and {curr}.")

        # Check for duplicates
        counts = Counter(assigned_numbers)
        duplicates = [r for r, count in counts.items() if count > 1]
        if duplicates:
            self.issues.append(f"Duplicate rank(s) assigned: {duplicates}.")


class BallotDataset:
    def __init__(
        self,
        source_name: str,
        candidates: List[str],
        ballots: List[Ballot],
        raw_df: pd.DataFrame,
    ):
        self.source_name = source_name
        self.candidates = candidates
        self.ballots = ballots
        self.raw_df = raw_df

    @property
    def total_ballots(self) -> int:
        return len(self.ballots)

    @property
    def compliant_ballots_count(self) -> int:
        return sum(1 for b in self.ballots if b.is_compliant)

    @property
    def non_compliant_ballots_count(self) -> int:
        return sum(1 for b in self.ballots if not b.is_compliant)

    @property
    def included_ballots(self) -> List[Ballot]:
        return [b for b in self.ballots if b.included]

    def set_all_included(self, included: bool):
        for b in self.ballots:
            b.included = included

    def exclude_non_compliant(self):
        for b in self.ballots:
            if not b.is_compliant:
                b.included = False
            else:
                b.included = True

    def reset_defaults(self):
        for b in self.ballots:
            b.included = True


def list_csvs_in_zip(zip_path_or_bytes) -> List[str]:
    """Returns a list of CSV filenames found inside a ZIP file."""
    with zipfile.ZipFile(zip_path_or_bytes, 'r') as z:
        return [f.filename for f in z.filelist if not f.is_dir() and f.filename.lower().endswith('.csv')]


def load_dataframe_from_source(file_path_or_bytes, filename_hint: str = "") -> Tuple[pd.DataFrame, str]:
    """
    Loads a pandas DataFrame from either a CSV file path, a ZIP file containing a CSV,
    or raw bytes. Returns (DataFrame, resolved_display_name).
    """
    is_zip = False
    if isinstance(file_path_or_bytes, (str, os.PathLike)):
        ext = os.path.splitext(str(file_path_or_bytes))[1].lower()
        if ext == '.zip':
            is_zip = True
        display_name = os.path.basename(str(file_path_or_bytes))
    else:
        display_name = filename_hint or "Uploaded Data"
        if display_name.lower().endswith('.zip'):
            is_zip = True

    if is_zip:
        with zipfile.ZipFile(file_path_or_bytes, 'r') as z:
            csv_files = [f.filename for f in z.filelist if not f.is_dir() and f.filename.lower().endswith('.csv')]
            if not csv_files:
                raise ValueError("No .csv files found inside the provided ZIP archive.")
            
            # Prefer 'Book Choice' or first CSV
            chosen_csv = csv_files[0]
            for candidate_csv in csv_files:
                if "book choice" in candidate_csv.lower():
                    chosen_csv = candidate_csv
                    break
            
            display_name = f"{display_name} -> {os.path.basename(chosen_csv)}"
            raw_bytes = z.read(chosen_csv)
            return read_csv_from_bytes(raw_bytes), display_name
    else:
        if isinstance(file_path_or_bytes, (str, os.PathLike)):
            for enc in ['utf-8-sig', 'utf-8', 'cp1252', 'latin1']:
                try:
                    df = pd.read_csv(file_path_or_bytes, encoding=enc)
                    return df, display_name
                except Exception:
                    continue
            raise ValueError(f"Could not read CSV file '{file_path_or_bytes}' with supported encodings.")
        else:
            return read_csv_from_bytes(file_path_or_bytes), display_name


def read_csv_from_bytes(raw_bytes: bytes) -> pd.DataFrame:
    for enc in ['utf-8-sig', 'utf-8', 'cp1252', 'latin1']:
        try:
            return pd.read_csv(io.BytesIO(raw_bytes), encoding=enc)
        except Exception:
            continue
    raise ValueError("Could not decode CSV data from bytes with supported encodings.")


def parse_ballot_dataset(
    file_source: Any,
    filename_hint: str = "",
    min_ranked_required: int = 5
) -> BallotDataset:
    """
    Parses a CSV or ZIP source into a BallotDataset with full validation.
    """
    df, source_name = load_dataframe_from_source(file_source, filename_hint)

    # 1. Identify Candidate ranking columns
    rank_cols = [
        col for col in df.columns 
        if '[' in col and ']' in col and ("rank" in col.lower() or "preference" in col.lower() or "choice" in col.lower() or "book" in col.lower())
    ]
    
    # Fallback: any column with bracketed text if none matched pattern
    if not rank_cols:
        rank_cols = [col for col in df.columns if '[' in col and ']' in col]

    if not rank_cols:
        raise ValueError("Could not find candidate ranking columns matching '[Book Name]' pattern in CSV.")

    candidates: List[str] = []
    for c in rank_cols:
        candidate_name = c.split('[')[-1].split(']')[0].strip()
        candidates.append(candidate_name)

    # 2. Identify Voter Name column
    name_col = None
    for col in df.columns:
        col_lower = col.lower()
        if "full name" in col_lower or "discord" in col_lower or "your name" in col_lower or "voter" in col_lower or "name" in col_lower:
            name_col = col
            break

    # 3. Identify Timestamp column
    timestamp_col = None
    for col in df.columns:
        col_lower = col.lower()
        if "timestamp" in col_lower or "date" in col_lower or "time" in col_lower:
            timestamp_col = col
            break

    # 4. Parse Ballots
    ballots: List[Ballot] = []
    for idx in range(len(df)):
        row = df.iloc[idx]
        voter_name = str(row[name_col]).strip() if name_col and pd.notna(row[name_col]) else f"Voter {idx + 1}"
        if not voter_name or voter_name.lower() == "nan":
            voter_name = f"Voter {idx + 1}"
            
        timestamp_val = str(row[timestamp_col]).strip() if timestamp_col and pd.notna(row[timestamp_col]) else ""

        ranks_dict: Dict[str, Optional[int]] = {}
        for col_name, candidate_name in zip(rank_cols, candidates):
            raw_val = row[col_name]
            rank_int: Optional[int] = None
            if pd.notna(raw_val):
                match = re.search(r'(\d+)', str(raw_val))
                if match:
                    rank_int = int(match.group(1))
            ranks_dict[candidate_name] = rank_int

        ballot = Ballot(
            index=idx,
            voter_name=voter_name,
            timestamp=timestamp_val,
            ranks=ranks_dict,
            all_candidates=candidates,
            min_ranked_required=min_ranked_required
        )
        ballots.append(ballot)

    return BallotDataset(
        source_name=source_name,
        candidates=candidates,
        ballots=ballots,
        raw_df=df
    )
