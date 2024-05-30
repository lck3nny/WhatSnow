
// T R I G G E R   S E A R C H                                      F U N C T I O N
// --------------------------------------------------------------------------------
// Retreive search parameters from Advanced Search form
// and send to backend via Async request.
// --------------------------------------------------------------------------------
async function triggerSearch(event){
    console.log("Advanced Search...")

    // Fetch search params and store in variables
    var year = document.getElementById("year").value;
    var category = document.getElementById("category").value;
    var stiffness = document.getElementById("stiffness").value;
    var shape = document.getElementById("shape").value;
    var camberProfile = document.getElementById("camber_profile").value;
    var length = document.getElementById("length").value;
    var noseWidth = document.getElementById("nose_width").value;
    var waistWidth = document.getElementById("waist_width").value;
    var tailWidth = document.getElementById("tail_width").value;
    var effectiveEdge = document.getElementById("effective_edge").value;

    // Restructure variables as an object
    let data = {
        "year": year,
        "category": category,
        "stiffness": stiffness,
        "shape": shape,
        "camber_profile": camberProfile,
        "length": length,
        "nose_width": noseWidth,
        "waist_width": waistWidth,
        "tail_width": tailWidth,
        "effective_edge": effectiveEdge
    };

    console.log("Search Criteria: \n");
    console.log(data);

    try {
        // Send Async POST request to backend
        const response = await fetch("/advanced-search/", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(data)
        });
    
        // Fetch results from request
        const result = await response.json();
        console.log("Results:", result);

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

// S H O W   R E S U L T S                                          F U N C T I O N
// --------------------------------------------------------------------------------
// Display the results that have been retreived from 
// the Advanced Search POST request.
// --------------------------------------------------------------------------------
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

        let size = row.insertCell(0);
        size.innerHTML = result.size;
        
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