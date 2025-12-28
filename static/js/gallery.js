// Wait for jsPDF to load from CDN
document.addEventListener('DOMContentLoaded', function() {
    const { jsPDF } = window.jspdf;

    document.getElementById("cmd").addEventListener("click", () => {
        const container = document.getElementById("container");
        
        html2canvas(container, { 
            scale: 2,
            useCORS: true
        }).then(canvas => {
            const imgData = canvas.toDataURL('image/png');
            
            const pdf = new jsPDF({ 
                format: "letter",
                orientation: "portrait",
                unit: "mm"
            });
            
            const pageWidth = pdf.internal.pageSize.getWidth();
            const pageHeight = pdf.internal.pageSize.getHeight();
            
            pdf.addImage(imgData, 'PNG', 0, 0, pageWidth, pageHeight);
            pdf.save('gallery.pdf');
        });
    });
});
