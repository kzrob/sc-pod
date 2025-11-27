// lowkey this script was completely vibe coded but it works...lol

document.addEventListener('DOMContentLoaded', function () {
    const table = document.getElementById('dataTable');
    if (!table) return;

    const thead = table.querySelector('thead');
    const tbody = table.querySelector('tbody');
    if (!thead || !tbody) return;

    const headerCells = Array.from(thead.querySelectorAll('th'));
    const headerCount = headerCells.length;
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const rowCount = rows.length;

    // Build a static matrix of cell text values so DOM mutations don't affect comparisons
    const matrix = rows.map(r => Array.from(r.children).map(td => (td.textContent || '').trim()));

    // Try to find an order-id column to limit merges within the same order group
    let orderCol = -1;
    for (let h = 0; h < headerCount; h++) {
        const key = (headerCells[h].textContent || '').trim();
        if (/order[-_\s]?item[-_\s]?id/i.test(key) || /order[-_\s]?id/i.test(key)) {
            orderCol = h;
            break;
        }
    }

    // For each column compute consecutive groups and apply rowspan
    for (let col = 0; col < headerCount; col++) {
        let i = 0;
        while (i < rowCount) {
            const val = matrix[i][col];
            if (!val) { i++; continue; }
            let j = i + 1;
            // advance j while values match AND (no orderCol specified OR order-id stays the same)
            while (j < rowCount && matrix[j][col] === val && (orderCol === -1 || matrix[j][orderCol] === matrix[i][orderCol])) j++;
            const span = j - i;
            if (span > 1) {
                // set rowspan on the first cell and hide subsequent duplicate cells
                const firstCell = rows[i].children[col];
                if (firstCell) firstCell.rowSpan = span;
                for (let k = i + 1; k < j; k++) {
                    const dupCell = rows[k].children[col];
                    if (!dupCell) continue;
                    dupCell.style.display = 'none';
                    dupCell.dataset.duplicate = 'true';
                }
            }
            i = j;
        }
    }

    // Column visibility toggles
    const toggles = Array.from(document.querySelectorAll('.col-toggle'));

    function setColumnVisibility(index, visible) {
        const th = headerCells[index];
        if (th) th.style.display = visible ? '' : 'none';
        rows.forEach(tr => {
            const cell = tr.children[index];
            if (!cell) return;
            if (!visible) {
                cell.style.display = 'none';
            } else {
                // if the cell was a duplicate cell from merging, keep it hidden
                cell.style.display = (cell.dataset.duplicate === 'true') ? 'none' : '';
            }
        });
    }

    // Initialize toggles
    toggles.forEach(cb => {
        const idx = parseInt(cb.dataset.index, 10);
        setColumnVisibility(idx, cb.checked);
        cb.addEventListener('change', () => setColumnVisibility(idx, cb.checked));
    });

    // Master "Toggle All" button behavior
    const toggleAllBtn = document.getElementById('toggleAllBtn');
    function updateToggleAllText() {
        if (!toggleAllBtn) return;
        const anyUnchecked = toggles.some(cb => !cb.checked);
        toggleAllBtn.textContent = anyUnchecked ? 'Select All' : 'Deselect All';
    }
    if (toggleAllBtn) {
        updateToggleAllText();
        toggleAllBtn.addEventListener('click', () => {
            const anyUnchecked = toggles.some(cb => !cb.checked);
            toggles.forEach(cb => {
                cb.checked = anyUnchecked;
                const idx = parseInt(cb.dataset.index, 10);
                setColumnVisibility(idx, cb.checked);
            });
            updateToggleAllText();
        });
        toggles.forEach(cb => cb.addEventListener('change', updateToggleAllText));
    }
});

const info = id => document.getElementById(id);

async function fetchData() {
    const res = await fetch('/data');
    const d = await res.json();
    if (d.error) {
        info('info').textContent = d.error;
        return;
    }
    renderTable(d.columns, d.rows);
    info('info').textContent = `${d.rows.length} rows · ${d.columns.length} columns`;
}

function renderTable(columns, rows) {
    const thead = info('thead'); thead.innerHTML = '';
    const tbody = info('tbody'); tbody.innerHTML = '';

    // Header
    const htr = document.createElement('tr');
    columns.forEach(c => {
        const th = document.createElement('th'); th.textContent = c; htr.appendChild(th);
    });
    thead.appendChild(htr);

    // Rows
    rows.forEach(r => {
        const tr = document.createElement('tr');
        columns.forEach(c => {
            const td = document.createElement('td');
            const val = r[c];
            td.textContent = (val === null || val === undefined) ? '' : String(val);
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
}

document.addEventListener('DOMContentLoaded', fetchData);

// Upload form handling: POST the selected file to /upload and refresh on success
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('uploadForm');
    if (!form) return;
    const status = document.getElementById('uploadStatus');
    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        const fileInput = document.getElementById('uploadFile');
        if (!fileInput || !fileInput.files || !fileInput.files[0]) {
            if (status) status.textContent = 'No file selected';
            return;
        }
        const file = fileInput.files[0];
        if (status) status.textContent = 'Uploading...';
        const fd = new FormData();
        fd.append('file', file);
        const storeSelect = document.getElementById('storeSelect');
        if (storeSelect && storeSelect.value) fd.append('store', storeSelect.value);
        try {
            const res = await fetch('/upload', { method: 'POST', body: fd });
            const j = await res.json().catch(() => ({}));
            if (!res.ok) {
                if (status) status.textContent = 'Error: ' + (j.error || res.status);
                console.error('Upload error', j);
                return;
            }
            if (status) status.textContent = 'Processed — reloading...';
            setTimeout(() => location.reload(), 600);
        } catch (err) {
            if (status) status.textContent = 'Upload failed';
            console.error(err);
        }
    });
});
