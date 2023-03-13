function showResults() {
    let results = document.getElementById('search_results');
    results.removeAttribute("hidden");
    results.scrollIntoView();
}

function triggerSearch(event){
    if (event.keyCode == 13) {
        var query = document.getElementById("search_bar").value;
        console.log(query);
        showResults();
    }
}
