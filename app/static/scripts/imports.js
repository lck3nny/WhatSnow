// Display import category for user
function startImport(type) {
    if(type == "board"){
        let p1 = document.getElementById('board_import_1');
        p1.removeAttribute("hidden");
        p1.scrollIntoView();

        let p2 = document.getElementById('ski_import_1');
        p2.hidden = true;
    }else{
        let p1 = document.getElementById('ski_import_1');
        p1.removeAttribute("hidden");
        p1.scrollIntoView();

        let p2 = document.getElementById('board_import_1');
        p2.hidden = true;
    }
}

// Updates Name on change
function changeColName(select){    
    var hiddenVals = document.getElementById(select.id.replace('-select', '-hidden-vals'));
    var overwrittenSelect = document.getElementsByName(select.value.replace(' ', '_').toLowerCase() + '-select')[0];
    var overwrittenHiddenVals = document.getElementsByName(select.value.replace(' ', '_').toLowerCase() + '-hidden-vals')[0];


    select.name = select.value.replace(' ', '_').toLowerCase() + '-select';
    hiddenVals.name = select.value.replace(' ', '_').toLowerCase() + '-hidden-vals';

    if(overwrittenSelect !== undefined){
        overwrittenSelect.value = 'Select...';
        overwrittenSelect.name = 'undefined-select';
        overwrittenHiddenVals.name = 'undefined-hidden-vals';
    }
}

// Validate form for new imports
function validateNewImport(form_name){
    const b = document.forms[form_name]['brand'].value;
    const m = document.forms[form_name]['model'].value;
    const y = document.forms[form_name]['year'].value;

    if((b == null || b == "") || (m == null || m == "") || (y == null || y == "")){
        alert("Please complete all fields before moving forward");
        return false;
    }
    return true;
}

// Validate form for import details
function validateImportDetails(){
    const profile = document.forms['import-details-form']['profile'].value;
    const flex = document.forms['import-details-form']['flex'].value;
    const data = document.forms['import-details-form']['data-table'].value;

    if(data == null || data == ""){
        alert("Please enter some data for size specifications.");
        return false;
    }

    if(flex == 0 || flex == "0"){
        alert("Please enter a flex value from 1 to 10.");
        return false;
    }

    if(profile == "Profile..."){
        alert("Please select a profle for your ski or board.");
        return false;
    }

    return true;
}

// Validate form for import confirmation
function validateImportConf(){
    const profile = document.forms['import-conf-form']['profile'].value;
    const flex = document.forms['import-conf-form']['flex'].value;

    if(flex == 0 || flex == "0"){
        alert("Please enter a flex value from 1 to 10.");
        return false;
    }

    if(profile == "Select..."){
        alert("Please select a profle for your ski or board.");
        return false;
    }
    return true;
}
