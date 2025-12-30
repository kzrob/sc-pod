const table = document.getElementById("dataTable");
const rows = table.rows;
const checkboxes = document.querySelectorAll(".col-toggle");
const toggleAllBtn = document.getElementById("toggleAllBtn")
const downloadBtn = document.getElementById("downloadCSV");
let groupings = {};

// Replaces duplicate row entries in column i with rowspan
const exceptions = ["quantity-purchased"];
function mergeDuplicateCells(columnIndex, start, end) {
    if (exceptions.includes(rows[0].children[columnIndex].textContent)) {return;}
    const columns = document.querySelectorAll(`.col-${columnIndex}`);
    let prevIndex = start; //previous cell index
    let count = 1; // number of duplicates
    for (let i = prevIndex + 1; i < end; i++) {
        const cell = columns[i];
        const prevCell = columns[prevIndex];
        let cellImages = cell.querySelectorAll("img");
        let prevCellImages = prevCell.querySelectorAll("img");
        let check = false;
        if (cellImages.length > 0 && prevCellImages.length > 0) {
            check = cell.children[0].src === prevCell.children[0].src;
        } else {
            check = cell.textContent === prevCell.textContent;
        }
        if (check) {
            count++;
            cell.style.display = "none";
            cell.setAttribute("hidden", "true");
            prevCell.setAttribute("rowspan", count);
        } else {
            if (columnIndex == 0) {
                groupings[prevIndex] = count;
            }
            prevIndex = i;
            count = 1;
        }
    }
    // Save the last group
    if (columnIndex == 0) {
        groupings[prevIndex] = count;
    }
}

function downloadTableAsCSV() {
    let csv = [];
    const rows = table.querySelectorAll('tr');

    for (const row of rows) {
        const cells = row.querySelectorAll('td, th');
        const rowData = [];
        for (const cell of cells) {
            if (cell.style.display === 'none') continue;
            rowData.push('"' + cell.innerText.replace(/"/g, '""') + '"');
        }
        csv.push(rowData.join(','));
    }

    const csvString = csv.join('\n');
    const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    link.href = URL.createObjectURL(blob);
    link.setAttribute('download', 'data.csv');
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}


downloadBtn.addEventListener('click', downloadTableAsCSV);

// Execute merging for all columns
mergeDuplicateCells(0, 1, rows.length);
for (let col = 1; col < checkboxes.length; col++) {
    for (var row in groupings) {
        var count = groupings[row];
        row = parseInt(row);
        count = parseInt(count);
        mergeDuplicateCells(col, row, row + count);
    }
}

// Individual column toggles
for (const checkbox of checkboxes) {
    checkbox.addEventListener("change", function() {
        const columnCells = document.querySelectorAll(`.${checkbox.id}`);
        for (const cell of columnCells) {
            if (!cell.hidden) {
                cell.style.display = this.checked ? "" : "none";
            }
        }
    });
    checkbox.dispatchEvent(new Event("change"));
};

// Toggle all columns button
toggleAllBtn.addEventListener("click", function() {
    const allChecked = Array.from(checkboxes).every(checkbox => checkbox.checked);
    for (const checkbox of checkboxes) {
        checkbox.checked = !allChecked;
        checkbox.dispatchEvent(new Event("change"));
    };
});