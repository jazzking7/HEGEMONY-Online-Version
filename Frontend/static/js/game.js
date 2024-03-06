$(document).ready(async function() {

    // Load in gameStyle.css
    var newLink = document.createElement('link');
    newLink.rel = 'stylesheet';
    newLink.href = URL_FRONTEND +"/static/css/gameStyle.css"; 
    var head = document.head || document.getElementsByTagName('head')[0];
    var initialLink = document.getElementById('initial_styling');
    head.replaceChild(newLink, initialLink);

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

    // Click propagation prevention
    let overlay = document.getElementById('overlay_sections');
    let cards = overlay.querySelectorAll('.card');
    for (let card of cards){
      card.addEventListener('click', function(event) {
        event.stopPropagation(); // Prevent click event from reaching the background
      });
    
      card.addEventListener('mousemove', function(event) {
        event.stopPropagation(); // Prevent mousemove event from reaching the background
      });
    }

});

let currEvent = null;
let deployable = 0;
let player_territories = [];
let game_settings;
let next_stage_btn;

async function get_game_settings() {
    try {
      const gameSettings = await new Promise((resolve) => {
        socket.emit('get_game_settings');
        socket.once('game_settings', (settings) => {
          resolve(settings);
        });
      });
      return gameSettings;
    } catch (error) {
      console.error('Error fetching game settings:', error);
    }
  }

socket.on('update_player_list', function(data){
  player_territories = data.list;
});

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

socket.on("troop_deployment", function(data){
  deployable = data.amount;
  announ = document.getElementById('announcement');
  announ.innerHTML = `<h2>Deploy your troops! </h2>`
  announ.innerHTML += `<h2>` + String(data.amount) + ' deployable.' + `</h2>`;
});

socket.on('conquest', function(){
  next_stage_btn = document.getElementById('proceed_next_stage');
  next_stage_btn.style.display = 'flex';
  next_stage_btn.innerHTML = `<h3>Finished Conquering</h3>`;
  next_stage_btn.onclick = () => {
    next_stage_btn.style.display = 'none'; 
    socket.emit("terminate_conquer_stage");
    currEvent = null;
    toHightlight = [];
    clickables = [];
  };
});

socket.on('update_clickables', function(data){
  clickables = data.trtys;
})

socket.on('rearrangement', function(){
  currEvent = 'rearrange';
  next_stage_btn = document.getElementById('proceed_next_stage');
  next_stage_btn.style.display = 'flex';
  next_stage_btn.innerHTML = `<h3>Finished Rearranging</h3>`;
  next_stage_btn.onclick = () => {
    next_stage_btn.style.display = 'none'; 
    socket.emit("terminate_rearrangement_stage");
    currEvent = null;
    toHightlight = [];
    clickables = [];
  };
});

socket.on('choose_skill', function(data){
  document.getElementById('middle_display').style.display = 'flex';
  let skill_options = document.getElementById('middle_content');
  skill_options.innerHTML = '';
  let disabled = false;
  for (let option of data.options){
    let btn_skill = document.createElement("button");
    btn_skill.className = 'btn btn-info';
    btn_skill.textContent = option;
    btn_skill.style.border = 'none';
    btn_skill.style.margin = '1px';
    btn_skill.onclick = function(){
      if(!disabled){
        disabled = true;
        btn_skill.style.border = '2px solid';
        btn_skill.style.borderColor = 'red';
        document.getElementById('control_panel').style.display = 'flex';
        document.getElementById('control_confirm').onclick = function(){
          document.getElementById('control_panel').style.display = 'none';
          socket.emit('send_skill_choice', {'choice': btn_skill.textContent})
          document.getElementById('middle_display').style.display = 'none';
        }
        document.getElementById('control_cancel').onclick = function(){
          document.getElementById('control_panel').style.display = 'none';
          disabled = false;
          btn_skill.style.border = "none";
        }
      }
    }
    skill_options.appendChild(btn_skill);
  }
});

socket.on('change_click_event', function(data){
  currEvent = data.event;
});

socket.on('capital_result', function(data){
  if (data.resp){
    currEvent = null;
    toHightlight = [];
  } else {
    popup("NOT YOUR TERRITORY!", 1000);
  }
});

socket.on('city_result', function(data){
  if (data.resp){
    currEvent = null;
    toHightlight = [];
  } else {
    popup("NOT YOUR TERRITORY!", 1000);
  }
});

socket.on('troop_result', function(data){
  if (!data.resp){
    popup("NOT YOUR TERRITORY!", 1000);
  } else {
    toHightlight = [];
    document.getElementById('control_mechanism').innerHTML = '';
    deployable = 0;
    document.getElementById('announcement').innerHTML = `<h2>Completed, waiting for others...`;
    currEvent = null;
  }
})

// Clear current selection window
socket.on('clear_view', function(){
  socket.off('color_picked');
  socket.off('choose_color');
  document.getElementById('control_panel').style.display = 'none';
  document.getElementById('middle_display').style.display = 'none';
});

// update territorial display
socket.on('update_trty_display', function(data){
  for (tid in data){
    // changed properties
    let changes = data[tid];
    // update property one by one
    for (field in changes){
      // Dev property
      if (field == 'hasDev'){
        if (changes[field] == 'city'){
          territories[tid].devImg = cityImage;
        } else {
          territories[tid].devImg = null;
        }
      // Other properties
      } else {
        territories[tid][field] = changes[field];
      }
    }
  }
});

// Mouse events
function mouseWheel(event) {
    // Check if the mouse is within the canvas bounds
    if (mouseX >= 0 && mouseX <= width && mouseY >= 0 && mouseY <= height && !isMouseOverOverlay()) {
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
      scaleFactor = constrain(scaleFactor, 0.3, 3); // Adjust the range as needed
    }
  }
  
  function isMouseOverOverlay() {
    let overlay = document.getElementById('overlay_sections');
    let cards = overlay.querySelectorAll('.card');
    for (var card of cards){
      var overlayRect = card.getBoundingClientRect();
      if (mouseX >= overlayRect.left && mouseX <= overlayRect.right && mouseY >= overlayRect.top && mouseY <= overlayRect.bottom){
        return true;
      }
    }
    return false;
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
    console.log(territories)
    console.log(clickables)
    // Check if you clicked on a polygon
    if(mouseX <= width && mouseY <= height && !isMouseOverOverlay()){
      if(isMouseInsidePolygon(mouseX, mouseY, hover_over.pts)){
        let tid = hover_over.id;
        if (currEvent == "settle_capital"){
          toHightlight = [];
          document.getElementById('control_panel').style.display = 'none';
          if (player_territories.includes(tid)){
            toHightlight.push(tid);
            document.getElementById('control_panel').style.display = 'none';
            document.getElementById('control_panel').style.display = 'flex';
            document.getElementById('control_confirm').onclick = function(){
              document.getElementById('control_panel').style.display = 'none';
              socket.emit('send_capital_choice', {'choice': toHightlight[0], 'tid': tid});
              toHightlight = [];
            }
            document.getElementById('control_cancel').onclick = function(){
              document.getElementById('control_panel').style.display = 'none';
              toHightlight = [];
            }
          }
        } 
        else if (currEvent == "settle_cities"){
          if(player_territories.includes(tid)){
            if (toHightlight.length == 2){
              toHightlight.splice(0, 1);
            }
            if (!toHightlight.includes(tid)){
              toHightlight.push(tid);
            }
            if (toHightlight.length == 2){
                document.getElementById('control_panel').style.display = 'none';
                document.getElementById('control_panel').style.display = 'flex';
                document.getElementById('control_confirm').onclick = function(){
                document.getElementById('control_panel').style.display = 'none';
                socket.emit('send_city_choices', {'choice': toHightlight});
                toHightlight = [];
              }
              document.getElementById('control_cancel').onclick = function(){
                document.getElementById('control_panel').style.display = 'none';
                toHightlight = [];
              }
            }
          }
        }
        else if (currEvent == "troop_deployment"){
          toHightlight = [];
          document.getElementById('control_panel').style.display = 'none';
          if (player_territories.includes(tid)){
            toHightlight.push(tid);
            document.getElementById('control_panel').style.display = 'none';
            document.getElementById('control_panel').style.display = 'flex';
            let troopValue = document.createElement("p");
            let troopInput = document.createElement("input");
            troopInput.setAttribute("type", "range");
            troopInput.setAttribute("min", 1);
            troopInput.setAttribute("max", deployable);
            troopInput.setAttribute("value", 1);
            troopInput.setAttribute("step", 1);
            troopInput.style.display = "inline-block";
            troopInput.addEventListener("input",function(){troopValue.textContent = troopInput.value;});
            let c_m = document.getElementById('control_mechanism');
            c_m.innerHTML = "";
            c_m.appendChild(troopInput);
            c_m.appendChild(troopValue);
            document.getElementById('control_confirm').onclick = function(){
            document.getElementById('control_panel').style.display = 'none';
            socket.emit('send_troop_update', {'choice': toHightlight[0], 'amount': troopInput.value});
            toHightlight = [];
            }
            document.getElementById('control_cancel').onclick = function(){
              document.getElementById('control_panel').style.display = 'none';
              toHightlight = [];
            }
          }
        }
        else if (currEvent == "conquest"){
          if (player_territories.includes(tid)){
            document.getElementById('control_panel').style.display = 'none';
            next_stage_btn.style.display = 'flex';
            clickables = [];
            if (toHightlight.length){
              toHightlight = [];
            }
            if (territories[tid].troops == 1){
              popup("NOT ENOUGH TROOPS FOR BATTLE!", 1000);
              return
            }
            toHightlight.push(tid);
            clickables = territories[tid].neighbors;
          } else if (clickables.includes(tid)){
            if (toHightlight.length != 2){
              toHightlight.push(tid);
            }
            if (toHightlight.length == 2){
              toHightlight[1] = tid;
              document.getElementById('control_panel').style.display = 'none';
              document.getElementById('control_panel').style.display = 'flex';
              next_stage_btn.style.display = 'none';

              let troopValue = document.createElement("p");
              let troopInput = document.createElement("input");
              troopInput.setAttribute("type", "range");
              troopInput.setAttribute("min", 1);
              troopInput.setAttribute("max", territories[toHightlight[0]].troops-1);
              troopInput.setAttribute("value", 1);
              troopInput.setAttribute("step", 1);
              troopInput.style.display = "inline-block";
              troopInput.addEventListener("input",function(){troopValue.textContent = troopInput.value;});
              let c_m = document.getElementById('control_mechanism');
              c_m.innerHTML = "";
              c_m.appendChild(troopInput);
              c_m.appendChild(troopValue);

              document.getElementById('control_confirm').onclick = function(){
                document.getElementById('control_panel').style.display = 'none';
                socket.emit('send_battle_data', {'choice': toHightlight, 'amount': troopInput.value});
                toHightlight = [];
                clickables = [];
                next_stage_btn.style.display = 'flex';
              }
              document.getElementById('control_cancel').onclick = function(){
                document.getElementById('control_panel').style.display = 'none';
                toHightlight = [];
                clickables = [];
                next_stage_btn.style.display = 'flex';
              }
           }
          }

        }

        else if(currEvent == "rearrange"){

          if (clickables.includes(tid) && tid != toHightlight[0]){
            if (toHightlight.length != 2){
              toHightlight.push(tid);
            }
            if (toHightlight.length == 2){
              toHightlight[1] = tid;
              document.getElementById('control_panel').style.display = 'none';
              document.getElementById('control_panel').style.display = 'flex';
              next_stage_btn.style.display = 'none';

              let troopValue = document.createElement("p");
              let troopInput = document.createElement("input");
              troopInput.setAttribute("type", "range");
              troopInput.setAttribute("min", 1);
              troopInput.setAttribute("max", territories[toHightlight[0]].troops-1);
              troopInput.setAttribute("value", 1);
              troopInput.setAttribute("step", 1);
              troopInput.style.display = "inline-block";
              troopInput.addEventListener("input",function(){troopValue.textContent = troopInput.value;});
              let c_m = document.getElementById('control_mechanism');
              c_m.innerHTML = "";
              c_m.appendChild(troopInput);
              c_m.appendChild(troopValue);

              document.getElementById('control_confirm').onclick = function(){
                document.getElementById('control_panel').style.display = 'none';
                socket.emit('send_rearrange_data', {'choice': toHightlight, 'amount': troopInput.value});
                toHightlight = [];
                clickables = [];
                next_stage_btn.style.display = 'flex';
              }
              document.getElementById('control_cancel').onclick = function(){
                document.getElementById('control_panel').style.display = 'none';
                toHightlight = [];
                clickables = [];
                next_stage_btn.style.display = 'flex';
              }
           }
          }

          else if (player_territories.includes(tid)){
            document.getElementById('control_panel').style.display = 'none';
            next_stage_btn.style.display = 'flex';
            clickables = [];
            if (territories[tid].troops == 1){
              popup("NOT ENOUGH TROOPS TO TRANSFER!", 1000);
              return;
            }
            if (toHightlight.length){
              toHightlight = [];
            }
            toHightlight.push(tid);
            socket.emit("get_reachable_trty", {'choice': tid})
          }  

        }

      }
    }
  }