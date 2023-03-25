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
