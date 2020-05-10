async function rate(rating, id, type){
    response = await fetch('/vote?id=' + id + '&type=' + type + '&val=' + rating, {method: 'POST'});
    if(response.ok){
        location.reload();
    }else{
        alert('Ошибка ' + response.status + '!');
    }
}