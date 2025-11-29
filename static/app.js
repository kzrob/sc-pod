const table = document.getElementById("dataTable");
const rows = table.rows;
const checkboxes = document.querySelectorAll(".col-toggle");
let groupings = {};

// Replaces duplicate row entries in column i with rowspan
function mergeDuplicateCells(columnIndex, start, end) {
    if (rows[0].children[columnIndex].textContent == "quantity-purchased") {
        return;
    }
    const col = document.querySelectorAll(`.col-${columnIndex}`);
    let prevIndex = start;
    let count = 1;
    for (let i = prevIndex + 1; i < end; i++) {
        console.log(i)
        const cell = col[i];
        const prevCell = col[prevIndex];
        let check = false;
        let cellImages = cell.querySelectorAll("img");
        let prevCellImages = prevCell.querySelectorAll("img");
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
}

function addColumnToTable(tableId, headerText, cellContentCallback) {
    const table = document.getElementById(tableId);
    if (!table) {
        console.error(`Table with ID '${tableId}' not found.`);
        return;
    }

    const rows = table.rows;

    // Add header cell
    if (rows.length > 0) {
        const headerRow = rows[0]; // Assuming the first row is the header
        const th = document.createElement("th");
        th.textContent = headerText;
        headerRow.appendChild(th);
    }

    // Add data cells to subsequent rows
    for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        const td = document.createElement("td");
        // You can customize the content of the new cell based on the row or other logic
        td.textContent = cellContentCallback ? cellContentCallback(row, i) : "";
        row.appendChild(td);
    }
}


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
            if (cell.getAttribute("hidden") === "true") continue;
            cell.style.display = this.checked ? "" : "none";
        }
    });

    // Optionally, trigger change event on load to apply initial visibility based on checked state
    checkbox.dispatchEvent(new Event("change"));
};

// Toggle all columns button
document.getElementById("toggleAllBtn").addEventListener("click", function() {
    const allChecked = Array.from(checkboxes).every(checkbox => checkbox.checked);
    for (const checkbox of checkboxes) {
        checkbox.checked = !allChecked;
        checkbox.dispatchEvent(new Event("change"));
    };
});

// Create new column