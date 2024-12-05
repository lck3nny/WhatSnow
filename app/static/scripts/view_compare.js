function compareCheck(direction, size){
    var numComparisons = document.getElementById('num-comparisons').innerHTML.match(/\d+/)[0];

    if((direction == 'up' && Number(numComparisons) > 8) || (direction == 'down' && numComparisons > 0)){
        return 'reset'
    }else if(String(direction) == 'up' && (Number(numComparisons) + Number(size)) > 8 ){
        return 'stop'
    }else if(String(direction) == 'down' && Number(numComparisons) == 0){
        return 'stop'
    }else{
        return 'success'
    }
}

async function addToCompare(skiboard){

    console.log('adding new sizes to comparisons...');

    const selectedSizes = document.getElementById('selected-sizes');
    var selected = selectedSizes.innerHTML.replace('[', '').replace(']', '').trim().split(',');
    if(selected[0] == ''){
        selected = [];
    }
    var data = {
        'skiboard': skiboard,
        'sizes': selected
    }

    console.log(selected);
    console.log('Number of additions: ' + String(selected.length));
    if (selected.length < 1){
        alert('Please select a size to compare.');
        return
    }
    const checkMsg = compareCheck('up', selected.length);
    console.log('Check Message:');
    console.log(checkMsg);
    if (checkMsg == 'stop'){
        alert('You can add a maximum of 8 comparisons');
        return
    }else if(checkMsg == 'reset'){
        clearComparisons();
        return
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

   // clearComparisons();
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
    emptySelection();
}


function emptySelection(){
    var col = [].slice.call(document.getElementsByClassName('col-item'));
    console.log(col)

    col.forEach(function(item){
        console.log(item);
        item.classList.remove('selected');
        item.style.color = '#white';
    });
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


