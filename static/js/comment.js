async function send_comment(id, type, val_id){
            message = document.getElementById(val_id).value;
            response = await fetch('/send_comment?id=' + id + '&type=' + type + '&message=' + message, {method: 'POST'});
            if(response.ok){
                location.reload();
            }else{
                alert('Ошибка ' + response.status + '!');
            }
        }

async function make_comment_field(id){
    container = document.getElementById('comment-' + id);
    var element = document.getElementById('comment-reply-' + id);
    element.parentNode.removeChild(element);
    node = document.createElement('div');
    node.className = "input-group mb-3";
    input = document.createElement('input');
    input.className = "form-control";
    input.id = "comment-input-" + id;
    node.appendChild(input);
    button = document.createElement('button');
    button.className = "btn btn-primary";
    button.onclick=function() {send_comment("" + id, "comment", "comment-input-" + id);};

    button.appendChild(document.createTextNode('Отправить'));
    node.appendChild(button);
    container.appendChild(node);
}