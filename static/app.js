const checkboxes = document.querySelectorAll('.col-toggle');
const col0 = document.querySelectorAll('.col-0');

// Rowspan for duplicate row entries in the first column
let currentIndex = 0;
let count = 1;
for (let i = 1; i < col0.length; i++) {
    const cell = col0[i];
    const prevCell = col0[currentIndex];
    const row = col0[i].parentElement;
    if (cell.textContent === prevCell.textContent) {
        count++;
        row.deleteCell(0);
        prevCell.setAttribute('rowspan', count);
        console.log(count)
    }
    else {
        currentIndex = i;
        count = 1;
    }
}

// Individual column toggles
checkboxes.forEach(checkbox => {
    checkbox.addEventListener('change', function() {
        const columnCells = document.querySelectorAll(`.${checkbox.id}`);
        columnCells.forEach(cell => {
            cell.style.display = this.checked ? '' : 'none';
        });
    });

    // Optionally, trigger change event on load to apply initial visibility based on checked state
    checkbox.dispatchEvent(new Event('change'));
});

// Toggle all columns button
document.getElementById('toggleAllBtn').addEventListener('click', function() {
    const allChecked = Array.from(checkboxes).every(checkbox => checkbox.checked);
    checkboxes.forEach(checkbox => {
        checkbox.checked = !allChecked;
        checkbox.dispatchEvent(new Event('change'));
    });
});
