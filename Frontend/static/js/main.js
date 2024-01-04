// Popup
var popup_timeout = null;

function popup(msg, duration) {
    if (popup_timeout) clearTimeout(popup_timeout);
    let popup = document.getElementById("alert");
    popup.innerHTML = msg;
    popup.style.display = 'flex';
    popup_timeout = setTimeout(() => {
        popup.innerHTML = '';
        popup.style.display = 'none';
    }, duration);
}

// Load page
const URL_FRONTEND = 'http://127.0.0.1:8080/';
var main;

function loadPage(page_route) {
    $.ajax({
        url: URL_FRONTEND + page_route,
        type: 'GET',
        success: function(response) {
            main.innerHTML = response;
        },
        error: function(error) {
            throw error;
        }
    });
}

function loadScript(script_src, id=null, async=false) {
    let script = document.createElement('script');
    script.src = script_src;
    if (id) script.id = id;
    script.async = async;
    document.head.appendChild(script);
}

function unloadScript(script_id) {
    let script = document.getElementById(script_id);
    if (script) script.remove();
}

// Initiate socket connection
const URL_BACKEND = 'http://127.0.0.1:8081';
var socket = io.connect(URL_BACKEND);

// Main logic
$(document).ready(function() {

    main = document.getElementById('main');

    // main_menu page
    loadPage('main_menu');
    loadScript(URL_FRONTEND + 'static/js/main_menu.js', 'page_script');
    
    socket.on('connect', function() {
        console.log('connected');
    });

    socket.on('errorPopup', function(data){
        popup(data.msg, 1000);
    });

    // GameLobby Page
    socket.on('gameLobby', function(data) {
        console.log("Inside lobby");
        $.ajax({
            url: 'http://127.0.0.1:8080/gameLobby',
            type: 'GET',
            success: function(response) {
                $('#main').html(response);
                $('#lobby_code').append('<h4></h4>');
                $('#lobby_code h4').text("Lobby Code: " + data.lobby_code);
                $('#maxPlayers').append('<h4></h4>');
                $('#maxPlayers h4').text("Maximum number of players: " + data.maxPlayers);
                $('#allianceOn').append('<h4></h4>');
                let onOff = data.allianceOn ? "On" : "Off"
                $('#allianceOn h4').text("Alliance Mode: " + onOff);
                let plist = "";
                for (let player of data.players) {
                    plist += '<h4>' + player + '</h4>';
                }
                $('#playerList').append(plist);
                if (data.isHost){
                    // Setting panels for host
                    $.ajax({
                        url: 'http://127.0.0.1:8080/changeSettings',
                        type: 'GET',
                        success: function(response) {
                            $('#lobbySettings').html(response);
                            $('#changeSettings').click(function(){
                                let numPlayers = $('#numPlayers').val();
                                let allianceMode = $('input[name="allianceMode"]:checked').val();
                                socket.emit('changeSettings', {
                                'numPlayers': numPlayers,
                                'allianceMode': allianceMode,
                                'lobby': data.lobby_code
                                });
                            });
                        },
                        error: function(error) {
                            console.log(error);
                        }
                    });
                    // Start game button for host
                    $.ajax({
                        url: 'http://127.0.0.1:8080/startGameBtn',
                        type: 'GET',
                        success: function(response) {
                            $('#START_GAME').html(response);
                            $('#START_GAME_BTN').click(function(){
                                socket.emit('START_GAME', {'lobby': data.lobby_code})
                            });
                        },
                        error: function(error) {
                            console.log(error);
                        }
                    });
                }
            },
            error: function(error) {
                console.log(error);
            }
        });
    });

    // signal to update lobby info
    socket.on('updateLobbyInfo', function(data){
        socket.emit('updateLobbyInfo', data)
    });


    // Game View
    socket.on('gameView', function(data){
        console.log("IN GAME")
        $.ajax({
            url: 'http://127.0.0.1:8080/gameMap',
            type: 'GET',
            success: function(response) {
                // Populate main
                $('#main').html(response);

                // Load p5 sketch
                let p5Sketch = document.createElement('script');
                p5Sketch.src = "/static/js/gameWindow.js";
                p5Sketch.async = false;
                document.head.appendChild(p5Sketch);

                // Load p5.js
                let p5Script = document.createElement('script');
                p5Script.src = 'https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.8.0/p5.js';
                p5Script.async = false;

                let p5SoundScript = document.createElement('script');
                p5SoundScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.8.0/addons/p5.sound.min.js';
                p5SoundScript.async = false;

                document.head.appendChild(p5Script);
                document.head.appendChild(p5SoundScript);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });

});
