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

/*
// Updates ID on change
function changeColName(select){    
    var hiddenVals = document.getElementsByName(select.name.replace('-select', '-hidden-vals'))[0];
    var overwrittenSelect = document.getElementById(select.value.replace(' ', '_').toLowerCase() + '-select');
    var overwrittenHiddenVals = document.getElementById(select.value.replace(' ', '_').toLowerCase() + '-hidden-vals');


    select.id = select.value.replace(' ', '_').toLowerCase() + '-select';
    hiddenVals.id = select.value.replace(' ', '_').toLowerCase() + '-hidden-vals';

    if(overwrittenSelect !== null){
        overwrittenSelect.value = 'Select...';
        overwrittenSelect.id = 'undefined-select';
        overwrittenHiddenVals.id = 'undefined-hidden-vals';
    }
}
*/

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

// Update value for flex from slider bar
// animation from 0?
