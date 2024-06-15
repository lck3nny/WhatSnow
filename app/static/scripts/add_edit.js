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
    stiffness = document.getElementById('stiffnessSlider').value;
    stiffnessLabel = document.getElementById('stiffnessLabel');
    stiffnessLabel.value = 'Stiffness: ' + stiffness;
}