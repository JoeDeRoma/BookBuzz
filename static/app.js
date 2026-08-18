// Book Buzz Web App - Frontend JavaScript

let allBallots = [];
let selectedBallots = new Set();

// File upload handling
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const browseBtn = document.getElementById('browse-btn');
const fileStatus = document.getElementById('file-status');

browseBtn.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        uploadFile(e.target.files[0]);
    }
});

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
        uploadFile(e.dataTransfer.files[0]);
    }
});

function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    fileStatus.className = 'status-message loading';
    fileStatus.textContent = 'Uploading and parsing file...';

    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            fileStatus.className = 'status-message error';
            fileStatus.textContent = `Error: ${data.error}`;
        } else {
            fileStatus.className = 'status-message success';
            fileStatus.textContent = `✓ Loaded: ${data.source_name} (${data.total_ballots} ballots, ${data.num_candidates} candidates)`;
            
            document.getElementById('dataset-section').style.display = 'block';
            document.getElementById('results-section').style.display = 'none';
            
            loadDatasetInfo(data);
        }
    })
    .catch(error => {
        fileStatus.className = 'status-message error';
        fileStatus.textContent = `Error: ${error.message}`;
    });
}

function loadDatasetInfo(data) {
    // Update stats
    document.getElementById('stat-total').textContent = data.total_ballots;
    document.getElementById('stat-compliant').textContent = data.compliant_count;
    document.getElementById('stat-non-compliant').textContent = data.non_compliant_count;
    document.getElementById('stat-included').textContent = data.included_count;

    // Update candidates
    const candidatesList = document.getElementById('candidates-list');
    candidatesList.innerHTML = data.candidates
        .map(c => `<span class="candidate-tag">${c}</span>`)
        .join('');

    // Load ballots
    loadBallots();
}

function loadBallots() {
    fetch('/api/ballots')
    .then(response => response.json())
    .then(data => {
        if (!data || !data.ballots) {
            console.log('No ballots loaded yet');
            return;
        }
        allBallots = data.ballots;
        selectedBallots.clear();
        
        // Pre-select included ballots
        allBallots.forEach((ballot, idx) => {
            if (ballot.included) {
                selectedBallots.add(idx);
            }
        });

        renderBallotTable();
        updateStats(data);
    })
    .catch(err => console.log('Loading ballots...', err));
}

function renderBallotTable() {
    const tbody = document.getElementById('ballots-tbody');
    tbody.innerHTML = allBallots.map((ballot, idx) => {
        const checked = selectedBallots.has(idx) ? 'checked' : '';
        const complianceClass = ballot.is_compliant ? 'compliant' : 'non-compliant';
        const complianceText = ballot.is_compliant ? '✓ Compliant' : '✗ Issues';
        
        return `
            <tr>
                <td>
                    <input type="checkbox" ${checked} onchange="toggleBallot(${idx})">
                </td>
                <td>${ballot.voter_name}</td>
                <td>${ballot.num_ranked} / ${ballot.total_candidates}</td>
                <td>
                    <span class="compliance-badge ${complianceClass}">
                        ${complianceText}
                    </span>
                </td>
            </tr>
        `;
    }).join('');
}

function toggleBallot(idx) {
    if (selectedBallots.has(idx)) {
        selectedBallots.delete(idx);
    } else {
        selectedBallots.add(idx);
    }
}

document.getElementById('btn-select-all').addEventListener('click', () => {
    allBallots.forEach((_, idx) => selectedBallots.add(idx));
    renderBallotTable();
});

document.getElementById('btn-deselect-all').addEventListener('click', () => {
    selectedBallots.clear();
    renderBallotTable();
});

document.getElementById('btn-exclude-invalid').addEventListener('click', () => {
    allBallots.forEach((ballot, idx) => {
        if (!ballot.is_compliant) {
            selectedBallots.delete(idx);
        }
    });
    renderBallotTable();
});

function updateStats(data) {
    document.getElementById('stat-included').textContent = selectedBallots.size;
}

// Analysis
document.getElementById('btn-analyze').addEventListener('click', () => {
    const ballotSelections = {};
    allBallots.forEach((_, idx) => {
        ballotSelections[idx] = selectedBallots.has(idx);
    });

    const analyzeBtn = document.getElementById('btn-analyze');
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = 'Running Analysis...';

    fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ballot_selections: ballotSelections })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(`Analysis Error: ${data.error}`);
        } else {
            displayResults(data);
            document.getElementById('results-section').style.display = 'block';
            document.getElementById('results-section').scrollIntoView({ behavior: 'smooth' });
        }
    })
    .catch(error => alert(`Error: ${error.message}`))
    .finally(() => {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = '3. Run Analysis';
    });
});

function displayResults(data) {
    // Winner
    document.getElementById('winner-name').textContent = data.winner;

    // Standings
    const standingsList = document.getElementById('standings-list');
    standingsList.innerHTML = data.standings.map(standing => {
        const candidatesStr = standing.is_tie ? 
            `(Tie) ${standing.candidates.join(', ')}` : 
            standing.candidates[0];
        const notesHtml = standing.defeat_notes.length > 0 ?
            `<div class="standing-notes">${standing.defeat_notes.map(n => 
                `<div class="standing-note">↳ ${n}</div>`
            ).join('')}</div>` : '';

        return `
            <div class="standing-card">
                <div>
                    <span class="standing-rank">#${standing.rank}</span>
                    <div class="standing-info">
                        <div class="standing-title">${candidatesStr}</div>
                        <div class="standing-score">RP Score: ${standing.score}</div>
                    </div>
                </div>
                ${notesHtml}
            </div>
        `;
    }).join('');

    // Pairwise Matrix
    renderMatrix(data.candidates, data.pairwise_matrix);
}

function renderMatrix(candidates, matrix) {
    const table = document.getElementById('matrix-table');
    const n = candidates.length;

    // Header row
    let html = '<thead><tr><th></th>';
    candidates.forEach((cand, i) => {
        const shortName = cand.length > 10 ? cand.substring(0, 10) + '..' : cand;
        html += `<th title="${cand}">#${i+1} ${shortName}</th>`;
    });
    html += '</tr></thead><tbody>';

    // Data rows
    for (let i = 0; i < n; i++) {
        const shortName = candidates[i].length > 10 ? candidates[i].substring(0, 10) + '..' : candidates[i];
        html += `<tr><th title="${candidates[i]}">#${i+1} ${shortName}</th>`;
        
        for (let j = 0; j < n; j++) {
            const cell = matrix[i][j];
            if (cell === null) {
                html += '<td class="matrix-cell neutral">—</td>';
            } else {
                let cellClass = 'neutral';
                if (cell.margin > 0) cellClass = 'win';
                else if (cell.margin < 0) cellClass = 'loss';

                html += `
                    <td class="matrix-cell ${cellClass}">
                        <div class="matrix-margin">${cell.margin > 0 ? '+' : ''}${cell.margin}</div>
                        <div class="matrix-details">(${cell.for} vs ${cell.against})</div>
                    </td>
                `;
            }
        }
        html += '</tr>';
    }
    html += '</tbody>';

    table.innerHTML = html;
}

// Export
document.getElementById('btn-export').addEventListener('click', () => {
    window.location.href = '/api/export/results';
});

// Initialize
loadBallots();
