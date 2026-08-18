import os
import zipfile
from engine.ballot_parser import parse_ballot_dataset
from engine.ranked_pairs import solve_ranked_pairs

def test_engine():
    csv_path = "Book Choice - September 2026.csv"
    ds = parse_ballot_dataset(csv_path)
    print(f"Loaded: {ds.source_name}")
    print(f"Candidates ({len(ds.candidates)}): {ds.candidates}")
    print(f"Total ballots: {ds.total_ballots}")
    print(f"Compliant ballots: {ds.compliant_ballots_count}")
    print(f"Non-compliant ballots: {ds.non_compliant_ballots_count}")
    
    print("\n--- Ballots & Issues ---")
    for b in ds.ballots:
        status = "VALID" if b.is_compliant else "INVALID"
        print(f"[{status}] {b.voter_name} (Ranked {b.num_ranked}): {b.issues}")

    # Solve with all included
    res_all = solve_ranked_pairs(ds.candidates, ds.ballots)
    print("\n--- Results (All Ballots Included) ---")
    print(f"Winner: {res_all.winner_name}")
    for s in res_all.standings:
        print(f"  Rank {s.rank}: {s.candidates} (Score: {s.score})")
        for note in s.defeat_notes:
            print(f"     -> {note}")

    # Solve with non-compliant excluded
    ds.exclude_non_compliant()
    res_compliant_only = solve_ranked_pairs(ds.candidates, ds.ballots)
    print("\n--- Results (Only Compliant Included) ---")
    print(f"Included: {res_compliant_only.included_ballots_count}, Excluded: {res_compliant_only.excluded_ballots_count}")
    print(f"Winner: {res_compliant_only.winner_name}")
    for s in res_compliant_only.standings:
        print(f"  Rank {s.rank}: {s.candidates} (Score: {s.score})")

    # Test ZIP loading
    zip_path = "test_ballots.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        z.write(csv_path, arcname="monthly_votes/Book Choice - September 2026.csv")
    
    ds_zip = parse_ballot_dataset(zip_path)
    print(f"\nZIP Test: Successfully parsed ZIP archive! Source: {ds_zip.source_name}, Voters: {len(ds_zip.ballots)}")
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
    print("\nAll engine tests passed successfully!")

if __name__ == "__main__":
    test_engine()
