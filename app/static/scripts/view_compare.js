async function addToCompare(skiboard){
    const selectedSizes = document.getElementById('selected-sizes');
    var selected = selectedSizes.innerHTML.replace('[', '').replace(']', '').trim().split(',');
    
    const comparisons = document.getElementById('compare-nav');
    var numCompasisons = comparisons.innerHTML.replace(/^\D+/g, '');

    var data = {
        'skiboard': skiboard,
        'sizes': selected
    }

    // missing data
    if ( selected == "" || skiboard == ""){
        alert("Please select a size of Ski or Snowboard to compare.");
        return false;
    }

    // max comparisons
    if ( numCompasisons >= 10 ){
        alert("You have reached the maximum of 10 comparisons.");
        return false;
    }



    console.log(data);
    try {
        const response = await fetch("/add-to-compare/", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify(data)
        });
    
        const result = await response.json();
        console.log("Success:", result);

        var compareNav = document.getElementById('compare-nav');
        compareNav.innerHTML = "Compare " + result.comparisons;
    } catch (error) {
        console.error("Error:", error);
        alert("There was an issue with your search query. Please try again.");
    }
}

async function removeComparison(skiboard, size){
    console.log("Removing skiboard from comparison");
    console.log(skiboard);
    console.log(size);

    var data = {
        'skiboard': skiboard,
        'size': size
    }
    console.log("Removing Skiboard ~" + skiboard + ": " + size)
    try {
        const response = await fetch("/remove-from-compare/", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify(data)
        });
    
        const result = await response.json();
        console.log("Success:", result);

        var compareNav = document.getElementById('compare-nav');
        compareNav.innerHTML = "Compare " + result.comparisons;

        window.location.href = '../';
    } catch (error) {
        console.error("Error:", error);
        alert("There was an issue with your search query. Please try again.");
    }
}

async function addToQuiver(skiboard){
    const selectedSizes = document.getElementById('selected-sizes');
    var selected = selectedSizes.innerHTML.replace('[', '').replace(']', '').trim().split(',');
    var data = {
        'skiboard': skiboard,
        'sizes': selected
    }

    console.log(data);
    try {
        const response = await fetch("/add-to-quiver/", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify(data)
        });
    
        const result = await response.json();
        console.log("Success:", result);
    } catch (error) {
        console.error("Error:", error);
        alert("There was an issue with your search query. Please try again.");
    }
}

async function clearComparisons(){
    var data = {
        'comparisons': "all",
    }

    console.log(data);
    try {
        const response = await fetch("/clear-comparisons/", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify(data)
        });
    
        const result = await response.json();
        console.log("Success:", result);
        var compareNav = document.getElementById('compare-nav');
        compareNav.innerHTML = "Compare [ 0 ]";

        window.location.href = '../';
    } catch (error) {
        console.error("Error:", error);
        alert("There was an issue with your search query. Please try again.");
    }
}

function toggleSize(id){
    colorToggleVals = ['white', 'blue'];
    //alert("Selected: " + id);
    var col = [].slice.call(document.getElementsByClassName(id));
    console.log(col)

    col.forEach(function(item){
        console.log(item);
        item.classList.toggle('selected');
        if (item.classList.contains('selected')){
            item.style.color = '#658eff';
            //item.style.color = '#FABF2A';
        }else{
            item.style.color = "white";
        }
        
    });

    const selectedCols = [].slice.call(document.getElementsByClassName('size selected'));
    var sizes = [];
    selectedCols.forEach(function(col){
        sizes.push(col.innerHTML);
    });

    var selectedSizes = document.getElementById('selected-sizes');
    console.log(selectedSizes.innerHTML);

    selectedSizes.innerHTML = `[ ${sizes.toString()} ]`;
}


