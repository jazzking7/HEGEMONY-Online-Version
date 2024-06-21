$(document).ready(function() {

    // Display host only options
    function displayHostOptions() {
        // TODO Display kick player option

        // Display enable settings
        $("#alliance").prop("disabled", false);
        $("#turn_time").prop("disabled", false);

        // Display start game button
        $(".container").append('<div class="row"><button class="btn btn-primary" id="start_game" style="padding: 1rem 5rem; margin-bottom: 20px;">START GAME</button></div>');

        // Connect start_game button
        $('#start_game').click(function() {
            console.log('start_game');
            let data = {
                'alliance': $('#alliance').val() == "true",
                'turn_time': $('#turn_time').val()
            };
            socket.emit('start_game', data);
        });
    }

    // Query backend for lobby data
    socket.emit('get_lobby_data');
    socket.on('lobby_data', function(data) {
        let sid = socket.id;

        // Display lobby code
        $("#lobby_code").html(data.lobby_id);

        // Display players
        let players = data.players;
        let player_list = $("#player_list");
        for (let i = 0; i < players.length; i++) {
            let player = players[i];
            let player_html = '<li class="list-group-item">' + player + '</li>';
            player_list.append(player_html);
        }

        // Thats it for non-host players
        if (sid != data.host) return;

        // Host only options
        displayHostOptions();
    });

    // Get lobby updates
    socket.on('update_lobby', function(data) {
        switch (data.event) {
            case 'join':
                // Add player to player list
                let player_html = '<li class="list-group-item">' + data.target + '</li>';
                $("#player_list").append(player_html);
                break;
            case 'disconnect':
                // Remove player from player list
                let player = data.target;
                $("#player_list li").each(function() {
                    if ($(this).html() == player) {
                        $(this).remove();
                    }
                });
                break;
            case 'change_host':
                // Check if this client is the new host
                if (socket.id == data.target) {
                    // Display host only options
                    displayHostOptions();
                }
                break;
        }
    });

    // start game
    socket.on('game_started', function() {
        console.log('game_started');
        
        loadPage('game')
            .then(() => {
                return unloadScript('page_script');
            })
            .then(() => {
                return loadScript(URL_FRONTEND + 'static/js/game.js', 'page_script');
            })
            .then(() => {
                socket.off('lobby_data');
                socket.off('update_lobby');
                socket.off('game_started');
                console.log('game.js script loaded successfully');
                // Additional logic after loading game.js if needed
            })
            .catch((error) => {
                console.error('Error loading page or script:', error);
            });
    });

});
