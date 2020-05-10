async function login(){
    email = document.getElementById("InputEmail").value;
    password = document.getElementById("InputPassword").value;
    remember = document.getElementById("Remember").value;
    response = await fetch('/login?email=' + email + '&password=' + password + '&remember=' + remember, {method: 'POST'});
    if(response.ok){
        data = await response.json()
        if(data['success'] == 'failed'){
            document.getElementById("LoginAnswer").innerHTML = data['answer'];
        }else if(data['success'] == 'OK'){
            location.reload(true);
        }
    }else{
        alert('Ошибка ' + response.status + '!');
    }
}

async function reset_password(){
    email = document.getElementById("ResetPasswordModalEmail").value;
    response = await fetch('/send_confirmation?type=password_reset&email=' + email, {method: 'POST'});
    if(response.ok){
        data = await response.json();
        if(data['success'] == 'OK'){
            $('#ResetPasswordModal').modal('hide');
            alert(data['answer']);
        }else{
            document.getElementById("ResetPasswordModalMessage").innerHTML = data['answer'];
        }
    }else{
        alert('Ошибка ' + response.status + '!');
    }
}

async function resend_verification(){
    email = document.getElementById("VerificationModalEmail").value;
    response = await fetch('/send_confirmation?type=verification&email=' + email, {method: 'POST'});
    if(response.ok){
        data = await response.json();
        if(data['success'] == 'OK'){
            $('#VerificationModal').modal('hide');
            alert(data['answer']);
        }else{
            document.getElementById("VerificationModalMessage").innerHTML = data['answer'];
        }
    }else{
        alert('Ошибка ' + response.status + '!');
    }
}