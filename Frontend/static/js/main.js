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

function special_popup(msg, duration, text_color, background_color) {
    if (popup_timeout) clearTimeout(popup_timeout);
    let popup = document.getElementById("special_alert");
    popup.innerHTML = msg;
    popup.style.display = 'flex';
    popup.style.color = text_color;  
    popup.style.backgroundColor = background_color; 
    
    popup_timeout = setTimeout(() => {
        popup.innerHTML = '';
        popup.style.display = 'none';
    }, duration);
}

// Load page
// const URL_FRONTEND = 'http://127.0.0.1:8080/';
const URL_FRONTEND = 'http://35.183.100.227:8080/';
var main;

// function loadPage(page_route) {
//     $.ajax({
//         url: URL_FRONTEND + page_route,
//         type: 'GET',
//         success: function(response) {
//             main.innerHTML = response;
//         },
//         error: function(error) {
//             throw error;
//         }
//     });
// }

// function loadScript(script_src, id=null, async=false) {
//     let script = document.createElement('script');
//     script.src = script_src;
//     if (id) script.id = id;
//     script.async = async;
//     document.head.appendChild(script);
// }

// function unloadScript(script_id) {
//     let script = document.getElementById(script_id);
//     if (script) script.remove();
// }

function loadPage(page_route) {
    return new Promise((resolve, reject) => {
        // cache-busting -> use unique time stamp to force new request
        const url = `${URL_FRONTEND + page_route}?_=${new Date().getTime()}`;
        $.ajax({
            url: url,
            type: 'GET',
            success: function(response) {
                main.innerHTML = response;
                resolve();
            },
            error: function(error) {
                reject(error);
            }
        });
    });
}

function loadScript(script_src, id = null, async = false) {
    return new Promise((resolve, reject) => {
        let script = document.createElement('script');
        // cache-busting -> use unique time stamp to force new request
        script.src = `${script_src}?_=${new Date().getTime()}`;
        if (id) script.id = id;
        script.async = async;
        script.onload = () => resolve();
        script.onerror = () => reject(new Error(`Script load error for ${script_src}`));
        document.head.appendChild(script);
    });
}

function unloadScript(script_id) {
    return new Promise((resolve, reject) => {
        let script = document.getElementById(script_id);
        if (script) {
            script.remove();
            resolve();
        } else {
            reject(new Error(`Script with id ${script_id} not found`));
        }
    });
}

// Initiate socket connection
// const URL_BACKEND = 'http://127.0.0.1:8081';
const URL_BACKEND = 'http://35.183.100.227:8081/';
var socket = io.connect(URL_BACKEND);

// Main logic
$(document).ready(function() {

    main = document.getElementById('main');

    // // main_menu page
    // loadPage('main_menu');
    // loadScript(URL_FRONTEND + 'static/js/main_menu.js', 'page_script');

    // Load main_menu page and script
    loadPage('main_menu').then(() => {
            console.log('Main menu page loaded successfully');
            return loadScript(URL_FRONTEND + 'static/js/main_menu.js', 'page_script');
        })
    .then(() => {
        console.log('Both page and script are fully loaded');
        // Proceed with further logic here
    })
    .catch((error) => {
        console.error('Error loading page or script:', error);
    });

    // Error handling
    const ERROR_POPUP_DURATION = 1000;
    socket.on('error', function(data) {
        popup(data.msg, (data.duration ? data.duration : ERROR_POPUP_DURATION));
    });
    
});
