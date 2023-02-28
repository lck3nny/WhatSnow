const snowboard_check = document.querySelector('#sbrd_check');
const goofyreg = document.querySelector('#goofyreg');

snowboard_check.addEventListener('click', (e)=>{
    goofyreg.removeAttribute('hidden');
});