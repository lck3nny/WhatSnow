// Validate form for new imports
function validateNewEdit(form_name){
    const b = document.forms[form_name]['brand'].value;
    const m = document.forms[form_name]['model'].value;
    const y = document.forms[form_name]['year'].value;

    if((b == null || b == "") || (m == null || m == "") || (y == null || y == "")){
        alert("Please complete all fields before moving forward");
        return false;
    }
    return true;
}

// Update the listed value of stiffness in label when slider is moved
function updateStiffness(){
    var stiffness = document.getElementById('stiffnessSlider').value;
    var stiffnessLabel = document.getElementById('stiffnessLabel');
    stiffnessLabel.innerHTML = 'Stiffness: ' + stiffness;
    console.log("Stiffness: " + stiffness);
}

// Update hidden form values from data table 
function updateHiddenVals(v){
    var paramName = v.split("/")[0];
    var itteration = v.split("/")[1];
    var newValue = document.getElementById(paramName + "_" + itteration).innerHTML;
    var hiddenElement = document.getElementById(paramName + "_hidden_" + itteration);
    hiddenElement.setAttribute('value', newValue);
}