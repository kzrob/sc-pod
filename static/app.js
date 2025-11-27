const checkboxes = document.querySelectorAll('.col-toggle');
const col0 = document.querySelectorAll('.col-0');

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

// Rowspan for duplicate row entries in the first column
let currentIndex = 0;
let count = 1;
for (let i = 1; i < col0.length; i++) {
    cell = col0[i];
    if (cell.textContent === col0[currentIndex].textContent) {
        count++;
        cell.style.display = 'none';
        col0[currentIndex].setAttribute('rowspan', count);
    }
    else {
        currentIndex = i;
        count = 1;
    }
}