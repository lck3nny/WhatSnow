async function triggerSearch(event){
    if (event.keyCode == 13) {
        var query = document.getElementById("search_bar").value;
        console.log(query);

        let data = {
            "query": query
        }

        try {
            const response = await fetch("/search/", {
              method: "POST",
              headers: {"Content-Type": "application/json"},
              body: JSON.stringify(data)
            });
        
            const result = await response.json();
            console.log("Success:", result);

            let results = result.results;
            if (results.length > 0){
                showResults(result.results);
            }else{
                alert("No results returned from your search");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("There was an issue with your search query. Please try again.");
        }
    }
}

function showResults(results) {
    let divResults = document.getElementById('div-results');
    divResults.removeAttribute("hidden");
    divResults.scrollIntoView();
    
    let tblResults = document.getElementById('tbl-results');
    tblResults.removeChild(tblResults.getElementsByTagName("tbody")[0]);
    tbody = tblResults.createTBody();

    results.forEach( result => {
        let row = tbody.insertRow();
        row.setAttribute("onclick","followLink('/view/" + result.slug + "');");

        let year = row.insertCell(0);
        year.innerHTML = result.year;

        let model = row.insertCell(0);
        model.innerHTML = result.model;
        
        let brand = row.insertCell(0);
        brand.innerHTML = result.brand;
    })

}


function followLink(url){
    window.location.href = url;
}