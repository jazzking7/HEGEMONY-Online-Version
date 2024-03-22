let currEvent = null;
let deployable = 0;
let player_territories = [];
let game_settings;
let next_stage_btn;

let timeoutBar;
let current_interval = null;

$(document).ready(async function() {
  // Load in gameStyle.css
  var newLink = $('<link>', {
      rel: 'stylesheet',
      href: URL_FRONTEND + "/static/css/gameStyle.css"
  });
  $('#initial_styling').replaceWith(newLink);

  // Get game settings
  game_settings = await get_game_settings();

  // Load p5.js libraries
  $.getScript('https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.8.0/p5.js', function(){
    $.getScript('https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.8.0/addons/p5.sound.min.js');
  });

  // Load p5.js sketch
  $.getScript(URL_FRONTEND + 'static/js/game_sketch.js');

  // Load progress bar
  $.getScript('https://cdn.jsdelivr.net/npm/progressbar.js@1.1.1/dist/progressbar.min.js',
      function(){
        timeoutBar = new ProgressBar.Line('#timeout-bar', {
          strokeWidth: 0.5,
          easing: 'linear',
          duration: 1000,
          color: '#ED6A5A', 
          trailColor: 'rgba(244, 244, 244, 0)', 
          trailWidth: 0.5,
          text: {
            style: {
            }
          },
          step: (state, timeoutBar) => {
          }
        });
      }
  );

  // Show continent border toggle
  $('#btn_show_cont').click(function() {
      showContBorders = !showContBorders;
      $(this).text(showContBorders ? 'On' : 'Off');
  });

  // Click propagation prevention
  $('#overlay_sections .card').on('click mousemove', function(event) {
      event.stopPropagation(); // Prevent click and mousemove events from reaching the background
  });

  $('#overlay_sections .circular-button').on('click mousemove', function(event) {
    event.stopPropagation(); // Prevent click and mousemove events from reaching the background
  });

});

// Function to start the timeout countdown
function startTimeout(totalSeconds) {
  var progress = 1;
  timeoutBar.set(progress);
  progress -= 1 / totalSeconds; 
  timeoutBar.animate(progress);
  current_interval = setInterval(function() {
    progress -= 1 / totalSeconds; 
    timeoutBar.animate(progress); // Animate the progress bar
    if (progress <= 0) {
      clearInterval(current_interval);
      timeoutBar.set(0);
    }
  }, 1000); // Update the progress bar every second
}

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

//========================= Update Game State ============================

// start/interrupt timeout bar
socket.on('start_timeout', function(data){
  startTimeout(data.secs);
});

socket.on('stop_timeout', function(){
  clearInterval(current_interval);
})

socket.on('get_players_stats', function(data){
  var pList = $('#stats-list');
  $.each(data, function(p, p_info) {
    var pBtn = $('<button></button>')
      .attr('id', p)
      .addClass('btn game_btn')
      .css({
        'color': 'black',
        'background-color': p_info.color
      })
      .html(`
        <div style="text-align: left;">
          ${p}<br>
          <div style="display: inline-block;">
            ${p_info.trtys} <img src="/static/Assets/Logo/territory.png" alt="Territory Logo" style="height: 20px;">
          </div>
          <div style="display: inline-block;">
            ${p_info.troops} <img src="/static/Assets/Logo/soldier.png" alt="Soldier Logo" style="height: 20px;">
          </div>
        </div>
      `);
    pList.append(pBtn);
  });
});

socket.on('update_players_stats', function(data){
  let btn = $('#' + data.name);
  btn.html(`
    <div style="text-align: left;">
      ${data.name}<br>
      <div style="display: inline-block;">
        ${data.trtys} <img src="/static/Assets/Logo/territory.png" alt="Territory Logo" style="height: 20px;">
      </div>
      <div style="display: inline-block;">
        ${data.troops} <img src="/static/Assets/Logo/soldier.png" alt="Soldier Logo" style="height: 20px;">
      </div>
    </div>
  `);
});


// update player territory list
socket.on('update_player_territories', function(data){
  player_territories = data.list;
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

// update clickables
socket.on('update_clickables', function(data){
  clickables = data.trtys;
})

// changing click events
socket.on('change_click_event', function(data){
  if (data.event == 'settle_capital'){
    currEvent = settle_capital;
  } else if (data.event == 'settle_cities'){
    currEvent = settle_cities;
  } else if (data.event == 'troop_deployment'){
    currEvent = troop_deployment;
  } else if (data.event == 'conquest'){
    currEvent = conquest;
  } else if (data.event == 'rearrange') {
    currEvent = rearrange;
  } else {
    currEvent = null;
  }
});

// Clear current selection window
socket.on('clear_view', function(){
  $('#control_panel, #middle_display, #proceed_next_stage').hide();
  toHightlight = [];
  clickables = [];
});

// announcements
socket.on('set_up_announcement', function(data){
  $('#announcement').html('<h3>' + data.msg + '</h3>');
});

//===================================================================================

// Receive Mission + Display info on Mission Tracker
socket.on('get_mission', function(data) {
  $('#announcement').html('<h1>' + data.msg + '</h1>');
  socket.off('get_mission');
});

// Start Color Choosing
socket.on('choose_color', function(data){
    $('#announcement').html('<h2>' + data.msg + '</h2>');
    $('#middle_display').css('display', 'flex');
    let colorBoard = $('#middle_content');
    let disabled = false;
    colorBoard.empty();
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
      colorBoard.append(btn_c);
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
  var rgbValues = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
  var hexColor = "#" + 
      ("0" + parseInt(rgbValues[1], 10).toString(16)).slice(-2) +
      ("0" + parseInt(rgbValues[2], 10).toString(16)).slice(-2) +
      ("0" + parseInt(rgbValues[3], 10).toString(16)).slice(-2);
  return hexColor.toUpperCase();
}
function hexToRgb(hex) {
  hex = hex.replace(/^#/, '');
  var bigint = parseInt(hex, 16);
  var r = (bigint >> 16) & 255;
  var g = (bigint >> 8) & 255;
  var b = bigint & 255;
  return "rgb(" + r + ", " + g + ", " + b + ")";
}

// Starting territorial distribution
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

function settle_capital(tid){
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

function settle_cities(tid){
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

socket.on('settle_result', function(data){
  if (data.resp){
    currEvent = null;
    toHightlight = [];
  } else {
    popup("NOT YOUR TERRITORY!", 1000);
  }
});

// Choose skill
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


//============================ Turn based events ================================
socket.on("troop_deployment", function(data){
  deployable = data.amount;
  announ = document.getElementById('announcement');
  announ.innerHTML = `<h2>Deploy your troops! </h2>`
  announ.innerHTML += `<h2>` + String(data.amount) + ' deployable.' + `</h2>`;
});

socket.on('conquest', function(){
  next_stage_btn = document.getElementById('proceed_next_stage');
  next_stage_btn.style.display = 'flex';
  document.querySelector('#proceed_next_stage .text').textContent = 'Finished Conquest';
  next_stage_btn.onclick = () => {
    next_stage_btn.style.display = 'none'; 
    socket.emit("terminate_conquer_stage");
    currEvent = null;
    toHightlight = [];
    clickables = [];
  };
});

socket.on('rearrangement', function(){
  next_stage_btn = document.getElementById('proceed_next_stage');
  next_stage_btn.style.display = 'flex';
  document.querySelector('#proceed_next_stage .text').textContent = 'Finished Rearranging';
  next_stage_btn.onclick = () => {
    next_stage_btn.style.display = 'none'; 
    socket.emit("terminate_rearrangement_stage");
    currEvent = null;
    toHightlight = [];
    clickables = [];
  };
});

function troop_deployment(tid){
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

function conquest(tid){
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

function rearrange(tid){
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

//===============================================================================

//=========================== Control Buttons ===================================
btn_diplomatic = document.getElementById('btn-diplomatic');
btn_diplomatic.onclick = function () {
  document.getElementById('middle_display').style.display = 'flex';
  document.getElementById('middle_title').innerHTML = "<h4>Diplomatic Menu</h4>";
  midDis = document.getElementById('middle_content')
  midDis.innerHTML = `
  <div style="display: flex; justify-content: space-between; align-items: center;">
  <div style="display: inline-block;">
  <button class="btn" style="background-color: #BA6868; color:#FFFFFF; margin-right:1px; ">
    FORM ALLIANCE
  </button>
  </div>
  <div style="display: inline-block;">
  <button class="btn" style="background-color: #BA6868; color:#FFFFFF; margin-left:1px;">
    REQUEST SUMMIT
  </button>
  </div>
  </div>
  `
}

async function get_sep_auth(){
  let amt = await new Promise((resolve) => {
    socket.emit('get_sep_auth');
    socket.once('receive_sep_auth', (data) => {resolve(data);});
  });
  return amt.amt;
}

btn_sep_auth = document.getElementById('btn-sep-auth');
btn_sep_auth.onclick = function () {
  document.getElementById('middle_display').style.display = 'flex';
  document.getElementById('middle_title').innerHTML = "";
  get_sep_auth().then(sep_auth => {
    document.getElementById('middle_title').innerHTML = `
    <div style="padding: 1px;">
    <h5>SPECIAL AUTHORITY AVAILABLE: ${sep_auth}</h5>
    </div>`
  });
  midDis = document.getElementById('middle_content')
  midDis.innerHTML = `
  <div style="display: flex; justify-content: space-between; align-items: center;">
  <div style="display: inline-block;">
  <button class="btn" style="background-color: #58A680; color:#FFFFFF; margin-right:1px; ">
    UPGRADE INFRASTRUCTURE
  </button>
  </div>
  <div style="display: inline-block;">
  <button class="btn" style="background-color: #6067A1; color:#FFFFFF; margin-left:1px;">
    BUILD CITIES
  </button>
  </div>
  <div style="display: inline-block;">
  <button class="btn" style="background-color: #A1606C; color:#FFFFFF; margin-left:2px;">
    MOBILIZATION
  </button>
  </div>
  </div>
  `
}

btn_skill = document.getElementById('btn-skill');
btn_skill.onclick = function () {
  return;
}

async function get_reserves_amt(){
  let amt = await new Promise((resolve) => {
    socket.emit('get_reserves_amt');
    socket.once('receive_reserves_amt', (data) => {resolve(data);});
  });
  return amt.amt;
}

btn_reserves = document.getElementById("btn-reserve");
btn_reserves.onclick = function () {
  document.getElementById('middle_display').style.display = 'flex';
  document.getElementById('middle_title').innerHTML = "";
  get_reserves_amt().then(ramt => {
    document.getElementById('middle_title').innerHTML = `
    <div style="padding: 1px;">
    <h5>TROOPS AVAILABLE: ${ramt}</h5>
    </div>`
  });
  midDis = document.getElementById('middle_content')
  midDis.innerHTML = `
  <div>
  <button class="btn" style="background-color: #BB6B6B; color:#FFFFFF;">
    DEPLOY RESERVES
  </button>
  </div>
  `;
}



//===============================================================================

//============================ Mouse events =====================================
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
    if(mouseX <= width && mouseY <= height && !isMouseOverOverlay()){
      if(isMouseInsidePolygon(mouseX, mouseY, hover_over.pts)){
        let tid = hover_over.id;
        if (currEvent){
          currEvent(tid);
        } 
      }
    }
  }