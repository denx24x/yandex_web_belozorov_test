async function onMessage(obj){
    for(var i in obj['change']){
        var item = obj['change'][i];
        if(item['self'] != null){
            UserData.update_self(item['self'])
        }
        if(item['online'] != null){
            UserData.update_online(item['online']);
        }
        if(item['best_users'] != null ){
            UserData.update_best(item['best_users']);
        }
        if(item['message_receive'] != null ){
            UserData.update_messages(item['message_receive']);
        }
    }
}

async function onError(error){
    console.log(error);
}

function longpoll(url) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
    if (this.readyState != 4) return;
        if (this.status == 200) {
            onMessage(JSON.parse(this.responseText));
        } else {
            onError(this);
        }
        longpoll(url);
    }
    xhr.open("POST", url, true);
    xhr.send(JSON.stringify(UserData.get_data()));
}

longpoll('/poll')
