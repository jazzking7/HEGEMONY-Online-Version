$(document).ready(function() {

    $('#btn_createLobby').click(function() {
        let username = $('#nickname').val();
        if (username.trim() === '') {
            popup("Must enter a name!", 1000);
            return;
        }
        socket.emit('createLobby', {'username': username});
    });
    
    $('#btn_joinLobby').click(function() {
        let lobby_code = $("#joinLobbyCode").val();
        let username = $('#nickname').val();
        if (username.trim() === '') {
            popup("Must enter a name!", 1000);
            return;
        }
        if (lobby_code.trim() === ''){
            popup("Must enter a lobby ID!", 1000);
            return;
        }
        socket.emit('joinLobby', {'username': username, 'lobby_code': lobby_code});
    });

});
