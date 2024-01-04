$(document).ready(function() {

    // Query backend for lobby data
    socket.emit('get_lobby_data');
    socket.on('lobby_data', function(data) {
        let sid = socket.id;
        // Display lobby code

        // Display players

        // Display kick player option for host

        // Display enable settings for host

        // Display start game button for host

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
