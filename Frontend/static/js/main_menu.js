$(document).ready(function() {

    function setupEventListeners() {

        function hasInvalidSelectorChars(name) {
            // Define a regular expression for invalid characters
            const invalidChars = /[!"#$%&'()*+,.\/:;<=>?@[\\\]^`{|}~\s]/;
            // Test the name against the regular expression
            return invalidChars.test(name);
        }    

        $('#btn_createLobby').click(function() {
        let username = $('#nickname').val().trim();
        if (username === '') {
            popup("Must enter a name!", 1000);
            return;
        } else if (username.length > 12) {
            popup("Name longer than 12 characters!", 1000);
            return;
        } else if (hasInvalidSelectorChars(username)) {
            popup("Name containing unrecognized special characters!", 2000);
            return
        }
        console.log('create_lobby');
        socket.emit('create_lobby', {'username': username});
    });
    
    $('#btn_joinLobby').click(function() {
        let lobby_code = $("#joinLobbyCode").val();
        let username = $('#nickname').val().trim();
        if (username === '') {
            popup("Must enter a name!", 1000);
            return;
        } else if (username.length > 12) {
            popup("Name longer than 12 characters!", 1000);
            return;
        } else if (hasInvalidSelectorChars(username)) {
            popup("Name containing unrecognized special characters!", 2000);
            return
        }
        if (lobby_code.trim() === ''){
            popup("Must enter a lobby ID!", 1000);
            return;
        }
        socket.emit('join_lobby', {'username': username, 'lobby_code': lobby_code});
    });
    }

    setupEventListeners();

    socket.on('lobby_created', function() {
        console.log('lobby_created');
        loadPage('lobby')
        .then(() => {
            return unloadScript('page_script');
        })
        .then(() => {
            return loadScript(URL_FRONTEND + 'static/js/lobby.js', 'page_script');
        })
        .then(() => {
            socket.off('lobby_created');
            console.log('lobby.js script loaded successfully');
        })
        .catch((error) => {
            console.error('Error loading page or script:', error);
        });
    });

    socket.on('lobby_joined', function() {
        console.log('lobby_joined');
        loadPage('lobby')
        .then(() => {
            return unloadScript('page_script');
        })
        .then(() => {
            return loadScript(URL_FRONTEND + 'static/js/lobby.js', 'page_script');
        })
        .then(() => {
            socket.off('lobby_joined');
            console.log('lobby.js script loaded successfully');
            // Additional logic after loading lobby.js if needed
        })
        .catch((error) => {
            console.error('Error loading page or script:', error);
        });
    });

});
