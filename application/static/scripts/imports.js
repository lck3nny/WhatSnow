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
