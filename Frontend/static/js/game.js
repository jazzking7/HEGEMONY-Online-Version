$(document).ready(async function() {

    // Load in gameStyle.css
    var newLink = document.createElement('link');
    newLink.rel = 'stylesheet';
    newLink.href = URL_FRONTEND +"/static/css/gameStyle.css"; 
    var head = document.head || document.getElementsByTagName('head')[0];
    var initialLink = document.getElementById('initial_styling');
    head.replaceChild(newLink, initialLink);

    // Remove alert
    document.getElementById('alert').parentNode.removeChild(document.getElementById('alert'))

    // Get game settings
    game_settings = await get_game_settings();

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

    // Show continent border toggle
    $('#btn_show_cont').click(function() {
      showContBorders = !showContBorders;
      document.getElementById('btn_show_cont').textContent = showContBorders ? 'On' : "Off"
    });

});

let game_settings;

async function get_game_settings() {
    try {
      const gameSettings = await new Promise((resolve) => {
        // Emit the 'get_game_settings' event to request game settings
        socket.emit('get_game_settings');
        // Listen for the 'game_settings' event
        socket.once('game_settings', (settings) => {
          // Resolve the Promise with the received game settings
          resolve(settings);
        });
      });
      return gameSettings;
    } catch (error) {
      console.error('Error fetching game settings:', error);
    }
  }

// Receive Mission + Display info on Mission Tracker
socket.on('get_mission', function(data) {
    document.getElementById('announcement').innerHTML = `<h1>` + data.msg + `</h1>`
    socket.off('get_mission');
});

// Start Color Choosing
socket.on('choose_color', function(data){
    document.getElementById('announcement').innerHTML = `<h2>` + data.msg + `</h2>`;
    document.getElementById('middle_display').style.display = 'flex';
    let colorBoard = document.getElementById('middle_content');
    let disabled = false;
    colorBoard.innerHTML = ''
    for (let option of data.options){
      let btn_c = document.createElement("button");
      btn_c.className = 'btn';
      btn_c.style.width = '2vw';
      btn_c.style.height = '2vw';
      btn_c.style.backgroundColor = option;
      btn_c.style.border = 'none';
      btn_c.style.margin = '1px';
      btn_c.onclick = function(){
        if (!disabled){
          disabled = true;
          btn_c.style.border = '2px solid';
          btn_c.style.borderColor = 'red';
          document.getElementById('control_panel').style.display = 'flex';
          document.getElementById('control_confirm').onclick = function(){
            document.getElementById('control_panel').style.display = 'none';
            socket.emit('send_color_choice', {'choice': rgbToHex(btn_c.style.backgroundColor)})
          }
          document.getElementById('control_cancel').onclick = function(){
            document.getElementById('control_panel').style.display = 'none';
            disabled = false;
            btn_c.style.border = "none";
          }
        }
      };
      colorBoard.appendChild(btn_c);
    }
});
// Update color options
socket.on('color_picked', function(data) {
  let colorBoard = document.getElementById('middle_content');
  let buttons = colorBoard.getElementsByTagName('button');
  let targetButton = null;
  let targetColor = hexToRgb(data.option)
  for (let btn of buttons) {
    if (btn.style.backgroundColor === targetColor) {
      targetButton = btn;
      break; 
    }
  }
  if (targetButton) {
    targetButton.remove();
  } else {
    console.log("Button with color", targetColor, "not found.");
  }
});
function rgbToHex(rgb) {
  // Extract RGB values from the computed color style
  var rgbValues = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);

  // Convert the RGB values to hex
  var hexColor = "#" + 
      ("0" + parseInt(rgbValues[1], 10).toString(16)).slice(-2) +
      ("0" + parseInt(rgbValues[2], 10).toString(16)).slice(-2) +
      ("0" + parseInt(rgbValues[3], 10).toString(16)).slice(-2);
  return hexColor.toUpperCase();
}
function hexToRgb(hex) {
  // Remove the hash (#) if it exists
  hex = hex.replace(/^#/, '');
  // Parse the hex value into separate RGB components
  var bigint = parseInt(hex, 16);
  var r = (bigint >> 16) & 255;
  var g = (bigint >> 8) & 255;
  var b = bigint & 255;
  // Return the RGB values in the format "rgb(x, x, x)"
  return "rgb(" + r + ", " + g + ", " + b + ")";
}

// announcements
socket.on('set_up_announcement', function(data){
  document.getElementById('announcement').innerHTML = `<h2>` + data.msg + `</h2>`;
});

socket.on('choose_territorial_distribution', function(data){
  document.getElementById('middle_display').style.display = 'flex';
  let dist_choices = document.getElementById('middle_content');
  dist_choices.innerHTML = ``;
  let disabled = false;
  for (let trty_dist in data.options){
    let btn_dist = document.createElement("button");
      btn_dist.className = 'btn';
      btn_dist.style.width = '2vw';
      btn_dist.style.height = '2vw';
      btn_dist.style.backgroundColor = trty_dist;
      btn_dist.style.border = 'none';
      btn_dist.style.margin = '1px';
      btn_dist.onclick = function(){
        if (!disabled){
          disabled = true;
          btn_dist.style.border = '2px solid';
          btn_dist.style.borderColor = 'red';
          document.getElementById('control_panel').style.display = 'flex';
          document.getElementById('control_confirm').onclick = function(){
            document.getElementById('control_panel').style.display = 'none';
            socket.emit('send_dist_choice', {'choice': rgbToHex(btn_dist.style.backgroundColor)})
            document.getElementById('middle_display').style.display = 'none';
          }
          document.getElementById('control_cancel').onclick = function(){
            document.getElementById('control_panel').style.display = 'none';
            disabled = false;
            btn_dist.style.border = "none";
          }
        }
      };
      dist_choices.appendChild(btn_dist);
  }
});

// Clear current selection window
socket.on('clear_view', function(){
  socket.off('color_picked');
  socket.off('choose_color');
  document.getElementById('control_panel').style.display = 'none';
  document.getElementById('middle_display').style.display = 'none';
});

// update territorial display
socket.on('update_trty_display', function(data){
  for (trty_name in data){
    // changed properties
    let changes = data[trty_name];
    // update property one by one
    for (field in changes){
      territories[trty_name][field] = changes[field];
    }
  }
});

  // Mouse events
function mouseWheel(event) {
    // Check if the mouse is within the canvas bounds
    if (mouseX >= 0 && mouseX <= width && mouseY >= 0 && mouseY <= height) {
      event.preventDefault(); 
      // Adjust the scale factor based on the mouse scroll direction
      if (event.delta > 0) {
        // Zoom out (reduce scale factor)
        scaleFactor *= 0.9; // You can adjust the zoom speed by changing the multiplier
      } else {
        // Zoom in (increase scale factor)
        scaleFactor *= 1.1; // You can adjust the zoom speed by changing the multiplier
      }
  
      // Limit the scale factor to prevent zooming too far in or out
      scaleFactor = constrain(scaleFactor, 0.5, 3); // Adjust the range as needed
    }
  }
  
  function mousePressed() {
    if(mouseX <= width && mouseY <= height){
      isDragging = true;
      previousMouseX = mouseX;
      previousMouseY = mouseY;
    }
  }
  
  function mouseReleased() {
    isDragging = false;
  }
  
  function mouseDragged() {
    if (isDragging) {
      let dx = mouseX - previousMouseX;
      let dy = mouseY - previousMouseY;
  
      offsetX += dx;
      offsetY += dy;
  
      previousMouseX = mouseX;
      previousMouseY = mouseY;
  
    }
  }
  
  function mouseClicked() {
    // Check if you clicked on a polygon
    if(mouseX <= width && mouseY <= height){
      if(isMouseInsidePolygon(mouseX, mouseY, hover_over.pts)){
        // socket.emit("clicked", {"id": hover_over.id})
        socket.emit("clicked", {"id": hover_over.id})
      }
    }
  }