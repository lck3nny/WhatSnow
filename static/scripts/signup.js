const snowboard_check = document.querySelector('#snowboard_check');

snowboard_check.addEventListener('click', (e)=>{
    const goofyreg = document.querySelector('#goofyreg');
    if(snowboard_check.checked){
        goofyreg.hidden = false;
    }else{
        goofyreg.hidden = true;
    }
});