$(document).ready(function() {

    // Load p5.js sketch
    loadScript(URL_FRONTEND + 'static/js/game_sketch.js', 'sketch');

    // Load p5.js libraries
    let p5Script = document.createElement('script');
    p5Script.src = 'https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.8.0/p5.js';
    p5Script.async = false;

    let p5SoundScript = document.createElement('script');
    p5SoundScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.8.0/addons/p5.sound.min.js';
    p5SoundScript.async = false;

    document.head.appendChild(p5Script);
    document.head.appendChild(p5SoundScript);

});
