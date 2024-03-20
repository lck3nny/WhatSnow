function validateReset(email){
    const validRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
    if(!email.match(validRegex) || email.length <= 4){
        return [false, 'Please enter a valid email address'];
    }
    return [true, 'Form is valid'];
}

const restetForm = document.querySelector('#reset-form');
restetForm.addEventListener('submit', (e)=>{
    const email = document.querySelector('#email').value;

    const valid = validateReset(email);
    if(!valid[0]){
        e.preventDefault();
        console.log('Validation Error');
        const err = document.getElementById('error-msg');
        err.innerHTML = valid[1];
        err.classList.add('alert-danger');
        document.getElementById('err-break').removeAttribute('hidden');
        document.getElementById('err-msg').removeAttribute('hidden');
    }
});