
// T R I G G E R   S E A R C H                                      F U N C T I O N
// --------------------------------------------------------------------------------
// Retreive query from search bar and send to backend via Async request.
// --------------------------------------------------------------------------------
async function triggerSearch(event){
    console.log("Trigger REG Search");
    if (event.keyCode == 13) {
        // Fetch search query and store in variable
        var query = document.getElementById("search_bar").value;
        if ( query == " "){
            return false;
        }


        // console.log("Searching for: " + query);
        // Restructure variable as an object
        let data = {
            "query": query
        }

        try {
            // Send Async POST request to backend
            const response = await fetch("/search/", {
              method: "POST",
              headers: {"Content-Type": "application/json"},
              body: JSON.stringify(data)
            });
        
            // Fetch results from request
            const result = await response.json();
            // console.log("Results:", result);

            let results = result.results;
            if (results.length > 0){
                // Display results in hidden div
                showResults(result.results);
            }else{
                alert("No results returned from your search");
            }
        } catch (error) {
            // Display errors
            console.error("Error:", error);
            alert("There was an issue with your search query. Please try again.");
        }
    }
}

// S H O W   R E S U L T S                                          F U N C T I O N
// --------------------------------------------------------------------------------
// Display the results that have been retreived from the Search POST request.
// --------------------------------------------------------------------------------
function showResults(results) {
    // Display hidden results pannel 
    let divResults = document.getElementById('div-results');
    divResults.removeAttribute("hidden");
    divResults.scrollIntoView();
    
    // Create table body
    let tblResults = document.getElementById('tbl-results');
    tblResults.removeChild(tblResults.getElementsByTagName("tbody")[0]);
    tbody = tblResults.createTBody();

    // Display each results as a new list item
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

// F O L L O W   L I N K                                            F U N C T I O N
// --------------------------------------------------------------------------------
// Simply follow the link of the url held within the HTML element
// --------------------------------------------------------------------------------
function followLink(url){
    window.location.href = url;
}