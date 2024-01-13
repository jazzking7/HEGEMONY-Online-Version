$(document).ready(async function() {

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
      console.log(hover_over.id);
      if(isMouseInsidePolygon(mouseX, mouseY, hover_over.pts)){
        // socket.emit("clicked", {"id": hover_over.id})
        socket.emit("clicked", {"id": hover_over.id})
      }
    }
  }