function validateName(name, type=""){
    if(name.length <= 1){
        return [false, `You must enter a ${type} name`];
    }else if(!isNaN(name)){
        return [false, `You must enter a valid ${type} name`];
    }
    return[true, 'Valid ${type} name'];
}

function validateEmail(email){
    var validRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
    if(!email.match(validRegex)){
        return [false, "Please enter a valid email address"]
    }
    return true
}

function validatePwd(pwd, conf){
    if(pwd.length <= 7){
        return [false, "Password must be 8 or more characters"];
    }else if(pwd != conf){
        return [false, "Passwords do not match"];
    }
    return [true, "Passwords are valid"]
}

function validateSignup(fname, lname, email, pwd, conf){
    const v_fname = validateName(fname, "First");
    if(! v_fname[0]){
        return v_fname;
    }
    
    const v_lname = validateName(lname, "Last");
    if(! v_lname[0]){
        return v_lname;
    }

    const v_email = validateEmail(email);
    if(! v_email[0]){
        return v_email;
    }
    
    const v_pwd = validatePwd(pwd, conf);
    if(! v_pwd[0]){
        return v_pwd;
    }

    return [true, 'Successful Validation'];
}

const signupForm = document.querySelector('#signup_form');
signupForm.addEventListener('submit', (e)=>{

    const fname = signupForm['fname'].value;
    const lname = signupForm['lname'].value;
    const email = signupForm['email'].value;
    const pwd = signupForm['password'].value;
    const conf = signupForm['password2'].value;
    /*
    const ski = signupForm['ski'].value;
    const snowboard = signupForm['snowboard'].value;
    const goofyreg = signupForm['goofyreg'].value;
    */

    // valid[true, 'successful validation']
    // valid[false, 'Please enter a value for XXX']
    const valid = validateSignup(fname, lname, email, pwd, conf);
    if(!valid[0]){
        e.preventDefault();
        console.log("Validation Error");
        const err = document.getElementById("error_msg");
        err.innerHTML = valid[1];
        err.classList.add('alert-danger');
        document.getElementById("err_break").removeAttribute("hidden");
    }
});