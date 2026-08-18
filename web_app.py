"""
Book Buzz Web Application
Ranked Pairs (Tideman Condorcet) Ballot Analysis Tool
Run with: python web_app.py
Then open: http://localhost:5000
"""

import os
import io
import csv
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

from engine.ballot_parser import parse_ballot_dataset
from engine.ranked_pairs import solve_ranked_pairs


app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = Path(__file__).parent / 'uploads'
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)

# Store current analysis in memory
current_dataset = None
current_result = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    global current_dataset, current_result
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith(('.csv', '.zip')):
        return jsonify({'error': 'Only CSV and ZIP files are supported'}), 400
    
    try:
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = app.config['UPLOAD_FOLDER'] / filename
        file.save(filepath)
        
        # Parse dataset
        dataset = parse_ballot_dataset(str(filepath))
        current_dataset = dataset
        current_result = None
        
        return jsonify({
            'success': True,
            'source_name': dataset.source_name,
            'total_ballots': dataset.total_ballots,
            'num_candidates': len(dataset.candidates),
            'candidates': dataset.candidates,
            'compliant_count': dataset.compliant_ballots_count,
            'non_compliant_count': dataset.non_compliant_ballots_count,
            'included_count': len(dataset.included_ballots),
        })
    except Exception as e:
        return jsonify({'error': f'Failed to parse file: {str(e)}'}), 400
    finally:
        # Clean up uploaded file
        if filepath.exists():
            filepath.unlink()


@app.route('/api/ballots')
def get_ballots():
    global current_dataset
    
    if not current_dataset:
        return jsonify({'error': 'No dataset loaded'}), 400
    
    ballots_data = []
    for ballot in current_dataset.ballots:
        ballots_data.append({
            'voter_name': ballot.voter_name,
            'num_ranked': ballot.num_ranked,
            'total_candidates': len(ballot.all_candidates),
            'is_compliant': ballot.is_compliant,
            'issues': ballot.issues,
            'included': ballot.included,
            'timestamp': ballot.timestamp or '',
        })
    
    return jsonify({
        'ballots': ballots_data,
        'total': current_dataset.total_ballots,
        'compliant': current_dataset.compliant_ballots_count,
        'non_compliant': current_dataset.non_compliant_ballots_count,
    })


@app.route('/api/analyze', methods=['POST'])
def analyze():
    global current_dataset, current_result
    
    if not current_dataset:
        return jsonify({'error': 'No dataset loaded'}), 400
    
    try:
        # Get ballot inclusion state from request if provided
        data = request.get_json() or {}
        ballot_selections = data.get('ballot_selections', {})
        
        # Update ballot inclusion state
        for idx, ballot in enumerate(current_dataset.ballots):
            key = str(idx)
            if key in ballot_selections:
                ballot.included = ballot_selections[key]
        
        # Rebuild included_ballots list
        current_dataset.included_ballots = [b for b in current_dataset.ballots if b.included]
        
        # Run analysis
        result = solve_ranked_pairs(current_dataset.candidates, current_dataset.ballots)
        current_result = result
        
        # Format standings
        standings = []
        for standing in result.standings:
            standings.append({
                'rank': standing.rank,
                'candidates': standing.candidates,
                'is_tie': standing.is_tie,
                'score': standing.score,
                'defeat_notes': standing.defeat_notes,
            })
        
        # Format pairwise matrix (simplified)
        matrix_data = []
        for i, cand_a in enumerate(result.candidates):
            row = []
            for j, cand_b in enumerate(result.candidates):
                if i == j:
                    row.append(None)
                else:
                    v_for = result.pairwise_matrix[i, j]
                    v_against = result.pairwise_matrix[j, i]
                    margin = v_for - v_against
                    row.append({
                        'for': int(v_for),
                        'against': int(v_against),
                        'margin': int(margin),
                    })
            matrix_data.append(row)
        
        return jsonify({
            'success': True,
            'winner': result.winner_name,
            'standings': standings,
            'candidates': result.candidates,
            'pairwise_matrix': matrix_data,
            'included_ballots': len(current_dataset.included_ballots),
            'total_ballots': len(current_dataset.ballots),
        })
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 400


@app.route('/api/ballot/<int:ballot_idx>')
def get_ballot_detail(ballot_idx):
    global current_dataset
    
    if not current_dataset or ballot_idx >= len(current_dataset.ballots):
        return jsonify({'error': 'Ballot not found'}), 404
    
    ballot = current_dataset.ballots[ballot_idx]
    
    ranked_books = [{'rank': rank, 'title': title} for rank, title in ballot.sorted_ranks]
    unranked_books = ballot.unranked_books
    
    return jsonify({
        'voter_name': ballot.voter_name,
        'timestamp': ballot.timestamp or '',
        'is_compliant': ballot.is_compliant,
        'issues': ballot.issues,
        'num_ranked': ballot.num_ranked,
        'ranked_books': ranked_books,
        'unranked_books': unranked_books,
        'included': ballot.included,
    })


@app.route('/api/export/results', methods=['POST'])
def export_results():
    global current_result
    
    if not current_result:
        return jsonify({'error': 'No analysis results to export'}), 400
    
    try:
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write standings
        writer.writerow(['Rank', 'Book(s)', 'RP Score', 'Notes'])
        for standing in current_result.standings:
            candidates_str = ' (Tie) '.join(standing.candidates) if standing.is_tie else standing.candidates[0]
            notes = '; '.join(standing.defeat_notes) if standing.defeat_notes else 'N/A'
            writer.writerow([standing.rank, candidates_str, standing.score, notes])
        
        writer.writerow([])
        writer.writerow(['Winner:', current_result.winner_name])
        writer.writerow(['Total Ballots:', current_result.included_ballots_count])
        
        output.seek(0)
        
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name='book_buzz_results.csv'
        )
    except Exception as e:
        return jsonify({'error': f'Export failed: {str(e)}'}), 400


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🎓 Book Buzz Web App Starting...")
    print("=" * 60)
    print("📖 Open your browser to: http://localhost:5000")
    print("=" * 60 + "\n")
    app.run(debug=False, host='0.0.0.0', port=5000)
