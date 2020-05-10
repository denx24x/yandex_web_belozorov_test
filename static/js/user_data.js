class UserData{
    static update_self(user){
        this.data['self'] = user;
    }
    static update_online(users){
        this.data['online'] = users;
        var table = document.getElementById("OnlineTableContent");
        document.getElementById("OnlineCount").innerHTML = this.data['online'].length;
        table.innerHTML = '';
        for (var i = 0; i < Math.min(10, this.data['online'].length); i++) {
            var item = this.data['online'][i];
            var node = document.createElement("p");
            var node2 = document.createElement("a")
            node.setAttribute("align", "center");
            node2.appendChild(document.createTextNode(item));
            node2.href = '/profile/' + item;
            node.appendChild(node2);
            table.appendChild(node);
        }
    }
    static update_best(users){
        this.data['best_users'] = users;
        var table = document.getElementById("BestTableContent");
        table.innerHTML = '';
        for (var i = 0; i < this.data['best_users'].length; i++) {
            var item = this.data['best_users'][i];
            var node = document.createElement("div");
            node.setAttribute("align", "center");
            var node2 = document.createElement("a");
            node2.appendChild(document.createTextNode(item[0]));
            node2.href = '/profile/' + item[0];
            node.appendChild(node2);
            var node2 = document.createElement("a");
            node2.appendChild(document.createTextNode(': ' + item[1]));
            node.appendChild(node2);
            table.appendChild(node);
        }
    }
    static update_messages(message){
        try{
            var table = document.getElementById("messagesContainer");
            var node = document.createElement("div");
            if(message['sender'] == this.data['self']){
                node.setAttribute("align", "right");
            }else{
                node.setAttribute("align", "left");
            }
            node.className = 'col-md6 border rounded';
            var msg = document.createElement("p");
            var time = document.createElement("p");
            time.appendChild(document.createTextNode(message['created_date'].split('.').slice(0, -1).join('.')));
            node.appendChild(document.createTextNode(message['message']));
            node.appendChild(msg);
            node.appendChild(time);
            table.appendChild(node);
            var element = document.getElementById("MessagesWrapper");
            element.scrollTop = element.scrollHeight;
        }finally{}
    }

    static update_new_messages(){

    }
    static get_data(){
        return this.data;
    }
    static init(){
        this.data = {'online': [], 'best_users': [], 'self': ''};
    }
}
UserData.init();
