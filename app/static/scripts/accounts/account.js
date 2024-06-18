// Basic Info


// Rider Info

var btnRiderInfoEdit = document.getElementById('btn-edit-rider-info');
var btnRiderInfoBack = document.getElementById('btn-rider-info-back');
var btnRiderInfoSave = document.getElementById('btn-rider-info-save');

btnRiderInfoEdit.addEventListener('click', triggerRiderInfoEdit);
btnRiderInfoBack.addEventListener('click', triggerRiderInfoBack);
btnRiderInfoSave.addEventListener('click', saveRiderInfo);

// Rider Info -> Edit
function triggerRiderInfoEdit(){
    console.log("Edit Rider Info");

    var hiddenButtons = document.getElementById('btns-submit-rider-info');
    var visabeButtons = document.getElementById('btn-edit-rider-info');
    hiddenButtons.hidden = false;
    visabeButtons.hidden = true;

    var inputs = document.getElementsByClassName('rider-info-param');
    for (var i = 0; i < inputs.length; i++){
        inputs[i].disabled = false;
    }
}

// Rider Info -> Back
function triggerRiderInfoBack(){

    var visableButtons = document.getElementById('btns-submit-rider-info');
    var hiddenButtons = document.getElementById('btn-edit-rider-info');
    visableButtons.hidden = true;
    hiddenButtons.hidden = false;

    var inputs = document.getElementsByClassName('rider-info-param');
    for (var i = 0; i < inputs.length; i++){
        inputs[i].disabled = true;
    }
}

// Rider Info -> Save
function saveRiderInfo(){
    console.log("Saving Rider info");
    // Make ASYNC request to save info
}

