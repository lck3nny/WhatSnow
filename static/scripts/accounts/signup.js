function validateName(name, type=''){
    if(name.length <= 1){
        return [false, `You must enter a ${type} name`];
    }else if(!isNaN(name)){
        return [false, `You must enter a valid ${type} name`];
    }
    return[true, 'Valid ${type} name'];
}

function validateEmail(email){
    const validRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
    if(!email.match(validRegex)){
        return [false, 'Please enter a valid email address']
    }
    return [true, 'Email is valid']
}

function validatepassword(password, conf){
    if(password.length <= 7){
        return [false, 'Password must be 8 or more characters'];
    }else if(password != conf){
        return [false, 'Passwords do not match'];
    }
    return [true, 'Passwords are valid']
}

function validateSignup(fname, lname, email, password, conf){
    console.log('Validating fname');
    const isValidFName = validateName(fname, 'First');
    if(! isValidFName[0]){
        return isValidFName;
    }
    
    console.log('Validating lname');
    const isValidLName = validateName(lname, 'Last');
    if(! isValidLName[0]){
        return isValidLName;
    }

    console.log('Validating email');
    const isValidEmail = validateEmail(email);
    if(! isValidEmail[0]){
        return isValidEmail;
    }
    
    console.log('Validating passwords');
    const isValidpassword = validatepassword(password, conf);
    if(! isValidpassword[0]){
        return isValidpassword;
    }

    console.log('Validation Complete!');
    return [true, 'Successful Validation'];
}

const signupForm = document.querySelector('#signup-form');
signupForm.addEventListener('submit', (e)=>{

    const fname = signupForm['fname'].value;
    const lname = signupForm['lname'].value;
    const email = signupForm['email'].value;
    const password = signupForm['password'].value;
    const conf = signupForm['password2'].value;
    /*
    const ski = signupForm['ski'].value;
    const snowboard = signupForm['snowboard'].value;
    const goofyreg = signupForm['goofyreg'].value;
    */

    console.log('First Name: ' + fname);
    console.log('Last Name: ' + lname);
    console.log('Email: ' + email);
    console.log('Password: ' + password);
    console.log('Conf: ' + conf);

    const valid = validateSignup(fname, lname, email, password, conf);
    if(!valid[0]){
        e.preventDefault();
        console.log('Validation Error:\n' + valid[1]);
        const err = document.getElementById('error-msg');
        err.innerHTML = valid[1];
        err.classList.add('alert-danger');
        document.getElementById('err-break').removeAttribute('hidden');
    }
});

const sbrdCheck = document.querySelector('#snowboard-check');
sbrdCheck.addEventListener('click', (e)=>{
    const goofyreg = document.querySelector('#goofyreg');
    if(sbrdCheck.checked){
        goofyreg.hidden = false;
    }else{
        goofyreg.hidden = true;
    }
});