$(document).ready(function() {

    $('#btn_createLobby').click(function() {
        let username = $('#nickname').val();
        if (username.trim() === '') {
            popup("Must enter a name!", 1000);
            return;
        }
        console.log('create_lobby');
        socket.emit('create_lobby', {'username': username});
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

    socket.on('lobby_created', function() {
        console.log('lobby_created');
        try {
            loadPage('lobby');
        } catch (error) {
            return;
        }
        unloadScript('page_script');
        loadScript(URL_FRONTEND + 'static/js/lobby.js', 'page_script');
        socket.off('createLobby');
    });

});
