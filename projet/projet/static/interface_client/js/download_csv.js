function downloadCSV() {
    var data = [];
    var rows = document.querySelectorAll("table tr");
    
    for (var i = 0; i < rows.length; i++) {
        var row = [], cols = rows[i].querySelectorAll("td, th");
        
        for (var j = 0; j < cols.length; j++) {
            row.push(cols[j].innerText);
        }
        
        data.push(row.join(","));        
    }

    var csvContent = "data:text/csv;charset=utf-8," 
        + data.join("\n");

    var encodedUri = encodeURI(csvContent);
    var link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "donnees.csv");
    document.body.appendChild(link); 
    
    link.click();
}
