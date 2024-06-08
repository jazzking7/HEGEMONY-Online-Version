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
// const URL_FRONTEND = 'http://127.0.0.1:8080/';
const URL_FRONTEND = 'https://plankton-app-5cjv2.ondigitalocean.app/';
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

function loadScript(script_src, id=null, async=false, fun) {
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
// const URL_BACKEND = 'http://127.0.0.1:8081';
const URL_BACKEND = 'https://stingray-app-cr93a.ondigitalocean.app/'
var socket = io.connect(URL_BACKEND);

// Main logic
$(document).ready(function() {

    main = document.getElementById('main');

    // main_menu page
    loadPage('main_menu');
    loadScript(URL_FRONTEND + 'static/js/main_menu.js', 'page_script');

    // Error handling
    const ERROR_POPUP_DURATION = 1000;
    socket.on('error', function(data) {
        popup(data.msg, (data.duration ? data.duration : ERROR_POPUP_DURATION));
    });
    
});
