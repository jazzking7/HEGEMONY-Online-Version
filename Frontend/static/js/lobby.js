$(document).ready(function() {

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

        // Host only options //
        // TODO Display kick player option

        // Display enable settings
        $("#alliance").prop("disabled", false);
        $("#turn_time").prop("disabled", false);

        // Display start game button
        $(".container").append('<div class="row"><button class="btn btn-primary" id="start_game" style="padding: 1rem 5rem;">Start Game</button></div>');

    });

    // Connect start_game button
    $('#start_game').click(function() {
        let data = {
            'allies_on': $('#alliance').val() == "true",
            'turn_time': $('#turn_time').val()
        };
        socket.emit('start_game', data);
    });

    socket.on('start_game', function(data) {

    });

});
