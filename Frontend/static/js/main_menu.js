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


        $('#btn_roll_simulator').click(function() {
            loadPage('roll_simulator')
            .then(() => {
                return unloadScript('page_script');
            })
            .then(() => {
                return loadScript(URL_FRONTEND + 'static/js/roll_simulator.js', 'page_script');
            })
            .then(() => {
                console.log('Entered Roll Simulator');
            })
            .catch((error) => {
                console.error('Error loading page or script:', error);
            });
        });

        $('#btn_game_rules').click(function() {
            loadPage('game_rules')
            .then(() => {
                return unloadScript('page_script');
            })
            .then(() => {
                return loadScript(URL_FRONTEND + 'static/js/rules_ui.js', 'page_script');
            })
            .then(() => {
                console.log('Entered Game Rules');
            })
            .catch((error) => {
                console.error('Error loading page or script:', error);
            });
        });

        $('#btn_tutorials').click(function() {
            loadPage('tutorials')
            .then(() => {
                return unloadScript('page_script');
            })
            .then(() => {
                return loadScript(URL_FRONTEND + 'static/js/tutorials.js', 'page_script');
            })
            .then(() => {
                console.log('Entered Game Tutorials');
            })
            .catch((error) => {
                console.error('Error loading page or script:', error);
            });
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

    socket.on('join_lobby_game', function() {
        console.log('joined game by replacing disconnected player');
        loadPage('game')
        .then(() => {
            return unloadScript('page_script');
        })
        .then(() => {
            return loadScript(URL_FRONTEND + 'static/js/game.js', 'page_script');
        })
        .then(() => {
            socket.off('lobby_joined');
            console.log('game.js script loaded successfully');
            // Additional logic after loading lobby.js if needed
        })
        .catch((error) => {
            console.error('Error loading page or script:', error);
        });
    });

});
