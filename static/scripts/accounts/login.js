function validateLogin(email, password){
    const validRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
    if(!email.match(validRegex) || email.length <= 4){
        return [false, 'Please enter a valid email address'];
    }else if(password.length == 0){
        return [false, 'Please enter a password to sign in.'];
    }
    return [true, 'Form is valid'];
}

const loginForm = document.querySelector('#login-form');
loginForm.addEventListener('submit', (e)=>{
    const email = document.querySelector('#email').value;
    const password = document.querySelector('#password').value;

    const valid = validateLogin(email, password);
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
