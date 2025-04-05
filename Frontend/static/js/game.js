// Current game event -> click event
let currEvent = null;
// Deployable troops
let deployable = 0;
// Deployable reserves
let reserves = 0;
// Number of cities to be settled for ASYNC EVENT
let city_amt = 0;
// Territories controlled by player
let player_territories = [];
// Game settings
let game_settings;
// Game_sketch.js started running
let sketch_running = false;

// Timeout bar
let timeoutBar;
// Interval of countdown
let current_interval = null;

// Progression bars for mission
let misProgBar;
let lossProg;

// ShortCut sliders
let curr_slider = "";
let curr_slider_val = "";

// Laplace Mode
let laplace_mode = false;
// Arsenal of Underworld
let minefields_amount = 0;
let US_usages = 0;
// Loan Shark
let in_debt = false;

$(document).ready(async function() {
  
  // Hide control buttons
  $('#btn-diplomatic, #btn-sep-auth, #btn-skill, #btn-reserve, #btn-debt').hide();

  // Load in gameStyle.css
  var newLink = $('<link>', {
      rel: 'stylesheet',
      href: URL_FRONTEND + "/static/css/gameStyle.css"
  });
  $('#initial_styling').replaceWith(newLink);

  // Get game settings
  game_settings = await get_game_settings();

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

    // Load p5.js libraries
  // $.getScript('https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.8.0/p5.js', function(){
  //   $.getScript('https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.8.0/addons/p5.sound.min.js');
  // });
  
  function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  function removeDynamicScripts() {
    const scriptSources = [
        'p5.min.js',
        'p5.sound.min.js',
        'game_sketch.js'
    ];

    document.querySelectorAll('script').forEach(script => {
        if (script.src && scriptSources.some(src => script.src.includes(src))) {
            script.remove();
            console.warn(`🧹 Removed script: ${script.src}`);
        }
    });
  }

  async function tryLoadSketch(maxRetries = 30) {
      let retryCount = 0;

      while (!sketch_running && retryCount < maxRetries) {
          let cacheBuster = Date.now();

          // 👇 Your exact script loading logic
          $.getScript(`${URL_FRONTEND}static/js/p5.min.js?v=${cacheBuster}`, function () {
              $.getScript(`${URL_FRONTEND}static/js/p5.sound.min.js?v=${cacheBuster}`);
          });
          loadGameSketch();

          // ⏱ Wait 0.5s before checking sketch_running
          await wait(500);

          if (!sketch_running) {
              console.warn(`⏳ sketch_running still false. Retry #${retryCount + 1}`);
              removeDynamicScripts(); 
              retryCount++;
          } else {
              console.log("✅ sketch_running is true. Sketch loaded successfully!");
              return;
          }
      }

      if (!sketch_running) {
          console.error("🚨 Sketch failed after maximum retries. Reloading page...");
          location.reload();
      }
  }

  tryLoadSketch();
});

function loadGameSketch(retries = 10) {
  let cacheBuster = new Date().getTime(); // Unique timestamp to force reload
  let scriptUrl = `${URL_FRONTEND}static/js/game_sketch.js?v=${cacheBuster}`;

  $.getScript(scriptUrl)
      .done(() => console.log("✅ game_sketch.js loaded successfully!"))
      .fail(() => {
          console.error(`❌ Failed to load game_sketch.js (Retries left: ${retries})`);

          if (retries > 0) {
              setTimeout(() => loadGameSketch(retries - 1), 1000); // Retry after 1 sec
          } else {
              console.error("🚨 game_sketch.js failed to load after 10 attempts.");
          }
      });
}

// Function to start the timeout countdown animation
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

// Function to load game settings
async function get_game_settings() {
    try {
      const gameSettings = await new Promise((resolve) => {
        socket.emit('get_game_settings');
        socket.once('game_settings', (settings) => {
          console.log("Received Data")
          console.log(settings);
          resolve(settings);
        });
      });
      return gameSettings;
    } catch (error) {
      console.error('Error fetching game settings:', error);
    }
  }

//========================= Update Game State ============================

// Start timer animation
socket.on('start_timeout', function(data){
  startTimeout(data.secs);
});

// Stop timer animation
socket.on('stop_timeout', function(){
  clearInterval(current_interval);
});

// Laplace setting
socket.on('laplace_mode', function(){
  laplace_mode = true;
});

function laplace_info_fetch(player_id){
  if (laplace_mode){
    socket.emit('laplace_info_fetch', {'pid': player_id});
  }
}

function isColorDark(hexColor) {
  // Convert hex to RGB
  let r = parseInt(hexColor.substring(1, 3), 16);
  let g = parseInt(hexColor.substring(3, 5), 16);
  let b = parseInt(hexColor.substring(5, 7), 16);
  
  // Calculate brightness
  let brightness = (0.299 * r) + (0.587 * g) + (0.114 * b);
  
  // Return true if the color is dark
  return brightness < 128;
}

socket.on('laplace_info', function(data) {
  var tcolor = 'black';
  if (isColorDark(data.color)){
    tcolor = 'rgb(245, 245, 245)'
  }
  $('#laplace_info_display').empty();
  $('#laplace_info_display').css({
    'display': 'block',
    'background-color': data.color,
    'color': tcolor,
    'overflow-y': 'auto',
    'max-height': '10em',
  });

  $.each(data.info, function(fieldName, fieldValue) {
    $('#laplace_info_display').append(`
      <div class="text-sm" style="word-wrap: break-word; max-width: 13vw;">
        <strong>${fieldName}:</strong> ${fieldValue}
      </div>
    `);
  });
});

// hide the display if clicked outside
$(document).on('click', function(event) {
  if (!$(event.target).closest('#laplace_info_display').length) {
    $('#laplace_info_display').empty().hide();
  }
});

// prevent propagation if clicked on it
$('#laplace_info_display').on('click', function(event) {
  event.stopPropagation();
});

// Player stats list initiate
socket.on('get_players_stats', function(data){
  var pList = $('#stats-list');
  pList.empty();
  $.each(data, function(p, p_info) {
    var tcolor = 'black';
    if (isColorDark(p_info.color)){
      tcolor = 'rgb(245, 245, 245)'
    }
    var pBtn = $('<button></button>')
      .attr('id', p)
      .addClass('btn game_btn mb-1')
      .css({
        'color': tcolor,
        'background-color': p_info.color,
        'width': '100%',
      })
      .html(`
        <div style="text-align: left;">
          ${p}<br>
          <div style="display: inline-block; margin-left: 10px; vertical-align: middle;">
            <img src="/static/Assets/Logo/soldier.png" alt="Soldier Logo" style="height: 20px;"> <span>${p_info.troops}</span>
          </div>
          <div style="display: inline-block; vertical-align: middle;">
            <img src="/static/Assets/Logo/territory.png" alt="Territory Logo" style="height: 20px;">  <span>${p_info.trtys}</span>
          </div>
          <br>
          <div style="display: inline-block; vertical-align: middle; direction: ltr;">
            <img src="/static/Assets/Logo/PPI.png" alt="Stats Logo" style="height: 20px;"> <span>${p_info.PPI}</span>
          </div>
        </div>
      `);
    pList.append(pBtn);
    pBtn.on('click', function() {
      laplace_info_fetch(p_info.player_id);
    });
  });
});

// Player stats list update
socket.on('update_players_stats', function(data){
  let btn = $('#' + data.name);
  btn.html(`
      <div style="text-align: left;" class="mb-1">
        ${data.name}<br>
        <div style="display: inline-block; margin-left: 10px; vertical-align: middle;">
            <img src="/static/Assets/Logo/soldier.png" alt="Soldier Logo" style="height: 20px;"><span>${data.troops}</span>
        </div>
        <div style="display: inline-block; vertical-align: middle;">
          <img src="/static/Assets/Logo/territory.png" alt="Territory Logo" style="height: 20px;"><span>${data.trtys}</span>
        </div>
        <br>
        <div style="display: inline-block; vertical-align: middle; direction: ltr;">
          <img src="/static/Assets/Logo/PPI.png" alt="Stats Logo" style="height: 20px;"><span>${data.PPI}</span>
        </div>
      </div>
  `);
});

// Update overview status
socket.on('update_global_status', function(data){
    $('#global_status').show();
    $('#game_round').text(data.game_round);
    $('#LAO').text(data.LAO);
    $('#MTO').text(data.MTO);
    $('#TIP').text(data.TIP);
    $('#SUP').text(data.SUP);
});

// Update private overview status
socket.on('private_overview', function(data){
  $('#curr_special_auth').text(data.curr_SA);
  $('#curr_reserves').text(data.curr_RS);
  $('#curr_infra').text(data.curr_infra);
  $('#curr_min_roll').text(data.curr_min_roll)
});

// update player territory list
socket.on('update_player_territories', function(data){
  player_territories = data.list;
});

// update target display
socket.on('mod_targets_to_capture', function(data){
  targetsToCapture = data.targets;
});

// UPDATE TERRITORIAL DISPLAY
// FORMAT: 
// { 
//  tid1: { property1: new_value, property2: new_value ...  }, 
//  tid2: { property1: new_value, property2: new_value ...  }, 
//  ......
// }
// property name must matches the property name used in game_sketch.js for display territory
// hasDev is used for loading different images for development
socket.on('update_trty_display', function(data){
  // Go through each territory (tid)
  for (tid in data){
    // Get the changed property list of the territory (tid)
    let changes = data[tid];
    // Update the property one by one
    for (field in changes){
      // Dev property -> CITY | MEGACITY | TRANSPORT HUB
      if (field == 'hasDev'){
        if (changes[field] == 'city'){
          territories[tid].devImg = cityImage;
        } else {
          territories[tid].devImg = null;
        }
      // Skill effects
      } else if (field == 'hasEffect') {
        if (changes[field] == 'nuke') {
          territories[tid].insig = radioImage;
        } else {
          territories[tid].insig = null;
        }
      }
      // Other properties -> Standard property
       else {
        territories[tid][field] = changes[field];
      }
    }
  }
});

// CHANGING CLICK EVENTS
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
  } else if (data.event == 'reserve_deployment') {
    currEvent = deploy_reserves;
  } else if (data.event == 'build_cities') {
    currEvent = build_cities;
  } else if (data.event == 'build_free_cities') {
    currEvent = build_free_cities;
  } else if (data.event == 'launch_orbital_strike'){
    currEvent = launch_orbital_strike;
  } else if (data.event == 'paratrooper_attack'){
    currEvent = paratrooper_attack;
  } else if (data.event == 'corrupt_territory'){
    currEvent = corrupt_territory;
  } else if (data.event == 'set_minefields'){
    currEvent = set_minefields;
  } else if (data.event == 'set_underground_silo'){
    currEvent = set_underground_silo;
  } else if (data.event == 'underground_silo_launch'){
    currEvent = underground_silo_launch;
  }
  else {
    currEvent = null;
  }
});

// CLEAR SELECTION WINDOWS
socket.on('clear_view', function(){
  $('#control_panel, #middle_display, #proceed_next_stage').hide();
  toHightlight = [];
  otherHighlight = [];
  clickables = [];
});

// set announcements
socket.on('set_up_announcement', function(data){
  $('#announcement').html('<h3>' + data.msg + '</h3>');
});

// show buttons
socket.on('signal_show_btns', function(){
  $('#btn-diplomatic, #btn-sep-auth, #btn-skill, #btn-reserve').show();
  if (in_debt) {
    $('#btn-debt').show();
  }
});

// hide buttons
socket.on('signal_hide_btns', function(){
  $('#btn-diplomatic, #btn-sep-auth, #btn-skill, #btn-reserve, #btn-debt').hide();
});

function hide_async_btns(){
  $('#btn-diplomatic, #btn-sep-auth, #btn-skill, #btn-reserve, #btn-debt').hide();
}

// Game over announcement
socket.on('GAME_OVER', function(data) {
  $('#gameEndSound').trigger('play');
  $('#btn-diplomatic, #btn-sep-auth, #btn-skill, #btn-reserve, #btn-debt').hide();
  currEvent = null;
  $('#announcement').show();
  $('#announcement').html('<h1>GAME OVER<h1>');
  $('#middle_display').css({
    'max-width': '50vw',
    'max-height': '50vh'
  });
  $('#middle_display, #middle_title, #middle_content').show();
  $('#middle_title').html('<h1 style="padding-right: 5px">FINAL VICTORS</h1>');
  $('#middle_content').html(`<div id="winners" style="display: flex; flex-direction: column; justify-content: center; align-items: center; max-height: calc(3 * 1.5em); overflow-y: auto;"></div>`);
  for (winner of data.winners) {
    var wname;
    var mission;
    for (w in winner) {
      wname = w;
      mission = winner[w];
    }
    $('#winners').append(`<div><h3>${wname} => ${mission}</h3></div>`);
  }
  $('#middle_content').append('<div id="player_overview" style="margin-top: 5px; max-height: 7em; overflow-y: auto; display: flex; flex-direction: column; align-items: flex-start;"></div>');
  for (let overview of data.player_overview) {
    let [playerName, skillName, missionName] = overview;
    $('#player_overview').append(
      `<div style="font-size: 0.875rem; word-wrap: break-word;">${playerName} had war art ${skillName} with ${missionName} as secret agenda.</div>`
    );
  }
});

// add sync click event
socket.on('add_tid_to_otherHighlight', function(data){
  otherHighlight.push(data.tid);
});

socket.on('remove_tid_from_otherHighlight', function(data){
  let toRemove = [data.tid];
  otherHighlight = otherHighlight.filter(item => !toRemove.includes(item));
});

socket.on('clear_otherHighlight', function(){
  otherHighlight = [];
});

// Popup notification
socket.on('display_new_notification', function(data){
  popup(data.msg, 2000);
})

socket.on('display_special_notification', function(data){
  special_popup(data.msg, 3000, data.t_color, data.b_color);
})

//===============================Mission Related Display=============================================

// Receive Mission + Display info on Mission Tracker
socket.on('get_mission', function(data) {
  console.log("get_mission")
  $('#announcement').html('<h1>' + data.msg + '</h1>');
  socket.off('get_mission');
});

// Initiate mission tracker
socket.on('initiate_tracker', function(data){
  $('#mission_title').text(data.title);
  // Display target, s for green, f for red
  if (data.targets){
    $('#misTargets').show();
    for (target in data.targets) {
      var tarid = target.replace(/ /g, "_");
      $('#misTargets').append(`<div id='target_${tarid}'>${target}</div>`)
      $(`#target_${tarid}`).css({
        'display': 'inline-block',
        'padding': '2px',
        'margin': '2px',
        'border-radius': '3px'
      });
      if (data.targets[target] == 's') {
        $(`#target_${tarid}`).css('background-color', '#50C878');
      } else {
        $(`#target_${tarid}`).css('background-color', '#E34234');
      }
    }
  } 
  if (data.misProgBar) {
    $('#misProgBar').show();
    misProgBar = new ProgressBar.Line('#misProgBar', {
      strokeWidth: 4,
      easing: 'easeInOut',
      duration: 1000,
      color: '#50C878',
      trailColor: '#eee',
      trailWidth: 4,
      svgStyle: {width: '100%', height: '100%'},
    });
    misProgBar.animate(data.misProgBar[0]/data.misProgBar[1]);
  }
  if (data.misProgDesp) {
    $('#misProgDesp').show();
    $('#misProgDesp').text(data.misProgDesp);
  }
  if (data.lossProg) {
    $('#lossProg').show();
    lossProg = new ProgressBar.Line('#lossProg', {
      strokeWidth: 4,
      easing: 'easeInOut',
      duration: 1000,
      color: '#880000',
      trailColor: '#eee',
      trailWidth: 4,
      svgStyle: {width: '100%', height: '100%'},
    });
    lossProg.animate(data.lossProg[0]/data.lossProg[1]);
  }
  if (data.lossDesp) {
    $('#lossDesp').show();
    $('#lossDesp').text(data.lossDesp);
  }
})

// Update mission tracker
socket.on('update_tracker', function(data) {
  const $misTargets = $('#misTargets');

  // 🔁 If there's a fresh list of targets, clear and re-add them
  if (data.renewed_targets) {
    $misTargets.empty();

    for (const target of data.renewed_targets) {
      const tarid = target.replace(/ /g, "_");
      $misTargets.append(`<div id='target_${tarid}'>${target}</div>`);
      $(`#target_${tarid}`).css({
        'display': 'inline-block',
        'padding': '2px',
        'margin': '2px',
        'border-radius': '3px',
        'background-color': '#E34234' // default color
      });
    }
  }

  if (data.targets) {
    for (const target in data.targets) {
      const tarid = target.replace(/ /g, "_");
      const existing = $(`#target_${tarid}`);

      // 🔁 If new_target flag is set and target exists, rename the old one
      if (data.new_target) {
        if (existing.length) {
          const newId = `target_${tarid}_old_${Date.now()}`;
          existing.attr('id', newId);
        }

        $misTargets.append(`<div id='target_${tarid}'>${target}</div>`);
        $(`#target_${tarid}`).css({
          'display': 'inline-block',
          'padding': '2px',
          'margin': '2px',
          'border-radius': '3px'
        });
      }

      // Update target color based on status
      if (data.targets[target] === 's') {
        $(`#target_${tarid}`).css('background-color', '#50C878'); // green
      } else {
        $(`#target_${tarid}`).css('background-color', '#E34234'); // red
      }
    }
  }

  if (data.misProgBar) {
    misProgBar.animate(data.misProgBar[0] / data.misProgBar[1]);
  }

  if (data.misProgDesp) {
    $('#misProgDesp').text(data.misProgDesp);
  }

  if (data.lossProg) {
    lossProg.animate(data.lossProg[0] / data.lossProg[1]);
  }

  if (data.lossDesp) {
    $('#lossDesp').text(data.lossDesp);
  }
});

//======================================================================================================

//=====================================SET UP EVENTS====================================================

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
          $('#control_confirm').off('click').on('click', function(){
            document.getElementById('control_panel').style.display = 'none';
            socket.emit('send_color_choice', {'choice': rgbToHex(btn_c.style.backgroundColor)})
          });
          $('#control_cancel').off('click').on('click', function(){
            document.getElementById('control_panel').style.display = 'none';
            disabled = false;
            btn_c.style.border = "none";
          });
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

// Choose territorial distribution
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

          let tmptid = 0;
          for (terri of territories) {
            if (terri.color == trty_dist){
              toHightlight.push(tmptid);
            }
            tmptid ++;
          }

          document.getElementById('control_panel').style.display = 'flex';
          $('#control_confirm').off('click').on('click', function(){
            document.getElementById('control_panel').style.display = 'none';
            socket.emit('send_dist_choice', {'choice': rgbToHex(btn_dist.style.backgroundColor)})
            document.getElementById('middle_display').style.display = 'none';
            toHightlight = []; 
          });
          $('#control_cancel').off('click').on('click' , function(){
            document.getElementById('control_panel').style.display = 'none';
            disabled = false;
            btn_dist.style.border = "none";
            toHightlight = [];
          });
        }
      };
      dist_choices.appendChild(btn_dist);
  }
});

// Set capital
function settle_capital(tid){
  toHightlight = [];
  document.getElementById('control_panel').style.display = 'none';
  if (player_territories.includes(tid)){
    toHightlight.push(tid);
    document.getElementById('control_panel').style.display = 'none';
    document.getElementById('control_panel').style.display = 'flex';
    $('#control_confirm').off('click').on('click', function(){
      document.getElementById('control_panel').style.display = 'none';
      socket.emit('send_capital_choice', {'choice': toHightlight[0], 'tid': tid});
      toHightlight = [];
    });
    $('#control_cancel').off('click').on('click' , function(){
      document.getElementById('control_panel').style.display = 'none';
      toHightlight = [];
    });
  }
}

// Set cities
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
        $('#control_confirm').off('click').on('click' , function(){
        document.getElementById('control_panel').style.display = 'none';
        socket.emit('send_city_choices', {'choice': toHightlight});
        toHightlight = [];
        });
        $('#control_cancel').off('click').on('click' , function(){
        document.getElementById('control_panel').style.display = 'none';
        toHightlight = [];
        });
    }
  }
}

// Set feedback for capital and city setting events
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
        $('#control_confirm').off('click').on('click' , function(){
          document.getElementById('control_panel').style.display = 'none';
          socket.emit('send_skill_choice', {'choice': btn_skill.textContent})
          document.getElementById('middle_display').style.display = 'none';
          let existingDesc = document.getElementById('skill_description_box');
          if (existingDesc) {
            existingDesc.remove();
          }
        });
        $('#control_cancel').off('click').on('click' , function(){
          document.getElementById('control_panel').style.display = 'none';
          disabled = false;
          btn_skill.style.border = "none";
          let existingDesc = document.getElementById('skill_description_box');
          if (existingDesc) {
            existingDesc.remove();
          }
        });
      }
    }

    btn_skill.addEventListener('mouseenter', function() {
      socket.emit('get_skill_description', { "name": btn_skill.textContent });
    });

    btn_skill.addEventListener('mouseleave', function () {
      let existingDesc = document.getElementById('skill_description_box');
      if (existingDesc) {
        existingDesc.remove();
      }
    });

    skill_options.appendChild(btn_skill);
  }
});

socket.on('display_skill_description', function (data) {
  let description = data.description;

  // Remove any existing description box
  const existingDesc = document.getElementById('skill_description_box');
  if (existingDesc) {
    existingDesc.remove();
  }

  // Create new description box
  let descBox = document.createElement('div');
  descBox.id = 'skill_description_box';
  descBox.textContent = description;

  // Use Tailwind-style classes and centered fixed positioning
  descBox.className = `
    bg-yellow-500 text-black
    p-3 rounded shadow-lg
    max-w-[40vw] max-h-[20vh] overflow-auto
    fixed top-[30%] left-1/2 transform -translate-x-1/2
    z-50
  `;
  descBox.style.position = 'absolute';
  descBox.style.top = '20%';

  document.body.appendChild(descBox);
});

//======================================================================================================

//============================ TURN BASED EVENTS =======================================================

// Play notification to signal start of turn

// SoundFX
socket.on("signal_turn_start", function(){
  document.getElementById('turn_notification').play();
});

// battle soundFX
socket.on("battle_propagation", function(data){
    if (data.battlesize) {
      var battleSFX = [document.getElementById('bigbattle'), document.getElementById('railgun')];
      var randomIndex = Math.floor(Math.random() * battleSFX.length);
      battleSFX[randomIndex].volume = 0.45;
      battleSFX[randomIndex].play();
    } else {
      var battleSFX = [document.getElementById('smallbattle'), document.getElementById('smolbattle')];
      var randomIndex = Math.floor(Math.random() * battleSFX.length);
      battleSFX[randomIndex].play();
    }
});

socket.on('selectionSoundFx', function() {
  $('#selectionSound').prop('volume', 0.5).trigger('play');
});

socket.on('cityBuildingSFX', function() {
  $('#constructionSound').prop('volume', 0.5).trigger('play');
});

// nuke soundFX
socket.on('nuclear_explosion', function(){
  nukeFX = document.getElementById('nuclearExplosion');
  nukeFX.volume = 0.5;
  nukeFX.play();
});

// casualty display
socket.on('battle_casualties', function(data){

  for (tdis in data) {
    casualties.push(data[tdis]);
  }

  dis_cas = true;
  cas_count = 30;
});

// addition display
socket.on('troop_addition_display', function(data){

  for (tdis in data) {
    additions.push(data[tdis]);
  }

  dis_add = true;
  add_count = 30;
});

// Display and update how many troops are deployable. Used both in initial deployment and turn-based troop deployment
socket.on("troop_deployment", function(data){
  deployable = data.amount;
  announ = document.getElementById('announcement');
  announ.innerHTML = `<h2>Deploy your troops! </h2>`
  announ.innerHTML += `<h2>` + String(data.amount) + ' deployable' + `</h2>`;
});

// Show the button that ends the preparation stage
socket.on('preparation', function(){
  $('#proceed_next_stage').show();
  $('#proceed_next_stage .text').text('Start Conquest');
  $('#proceed_next_stage').off('click').on('click', () => {
    $('#proceed_next_stage').hide();
    socket.emit("terminate_preparation_stage");
    currEvent = null;
    toHightlight = [];
    clickables = [];
  });
});

// Show the button that ends the conquest stage
socket.on('conquest', function(){
  $('#proceed_next_stage').show();
  $('#proceed_next_stage .text').text('Finish Conquest');
  $('#proceed_next_stage').off('click').on('click', () => {
    $('#proceed_next_stage').hide();
    socket.emit("terminate_conquer_stage");
    currEvent = null;
    toHightlight = [];
    clickables = [];
  });
});

// Show the button that ends the rearrangement stage
socket.on('rearrangement', function(){
  $('#proceed_next_stage').show();
  $('#proceed_next_stage .text').text('Finish Rearrangement');
  $('#proceed_next_stage').off('click').on('click', () => {
    $('#proceed_next_stage').hide();
    socket.emit("terminate_rearrangement_stage");
    currEvent = null;
    toHightlight = [];
    clickables = [];
  });
});

// Click function that handles troop deployment (for initial and turn-based troop deployment)
function troop_deployment(tid){
  toHightlight = [];
  document.getElementById('control_panel').style.display = 'none';
  if (player_territories.includes(tid)){
    toHightlight.push(tid);
    
    // Sync clicks
    socket.emit('add_click_sync', {'tid': tid});

    document.getElementById('control_panel').style.display = 'none';
    document.getElementById('control_panel').style.display = 'flex';
    let troopValue = document.createElement("p");
    troopValue.textContent = 1;
    let troopInput = document.createElement("input");

    // set shortcut id
    troopInput.setAttribute("id", "adjust_attack_amt");
    troopValue.setAttribute("id", "curr_attack_amt");

    curr_slider = "#adjust_attack_amt";
    curr_slider_val = "#curr_attack_amt";

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
    $('#control_confirm').off('click').on('click' , function(){
    document.getElementById('control_panel').style.display = 'none';
    socket.emit('send_troop_update', {'choice': toHightlight[0], 'amount': troopInput.value});
    toHightlight = [];

    // Sync clicks
    socket.emit('remove_click_sync', {'tid': tid});

    });
    $('#control_cancel').off('click').on('click' , function(){
      document.getElementById('control_panel').style.display = 'none';
      toHightlight = [];

      // Sync clicks
      socket.emit('remove_click_sync', {'tid': tid});

    });
  }
}

// Used in initial deployment to show waiting message when done
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

// Click function that handles conquest
function conquest(tid){
  if (player_territories.includes(tid)){
    document.getElementById('control_panel').style.display = 'none';
    $('#proceed_next_stage').show();
    clickables = [];
    if (toHightlight.length){
      toHightlight = [];
      // clear sync clicks
      socket.emit('clear_otherHighlights');
    }
    if (territories[tid].troops <= 1){
      popup("NOT ENOUGH TROOPS FOR BATTLE!", 1000);
      return
    }
    toHightlight.push(tid);
    // Sync clicks
    socket.emit('add_click_sync', {'tid': tid});

    clickables = territories[tid].neighbors.filter(tmp_id => territories[tid].color !== territories[tmp_id].color);
    
  } else if (clickables.includes(tid)){
    if (toHightlight.length != 2){
      toHightlight.push(tid);
      // Sync clicks
      socket.emit('add_click_sync', {'tid': tid});
    }
    if (toHightlight.length == 2){
      toHightlight[1] = tid;
      // Sync clicks
      socket.emit('clear_otherHighlights');
      for (trty of toHightlight){
        socket.emit('add_click_sync', {'tid': trty});
      }
      
      document.getElementById('control_panel').style.display = 'none';
      document.getElementById('control_panel').style.display = 'flex';
      $('#proceed_next_stage').hide();

      let troopValue = document.createElement("p");
      let troopInput = document.createElement("input");

      // set shortcut id
      troopInput.setAttribute("id", "adjust_attack_amt");
      troopValue.setAttribute("id", "curr_attack_amt");

      curr_slider = "#adjust_attack_amt";
      curr_slider_val = "#curr_attack_amt";

      troopInput.setAttribute("type", "range");
      troopInput.setAttribute("min", 1);
      troopInput.setAttribute("max", territories[toHightlight[0]].troops-1);
      troopInput.setAttribute("value", 1);
      troopInput.setAttribute("step", 1);
      troopInput.style.display = "inline-block";
      troopInput.addEventListener("input",function(){troopValue.textContent = troopInput.value;});
      troopValue.textContent = 1;
      let c_m = document.getElementById('control_mechanism');
      c_m.innerHTML = "";
      c_m.appendChild(troopInput);
      c_m.appendChild(troopValue);

      $('#control_confirm').off('click').on('click' , function(){
        document.getElementById('control_panel').style.display = 'none';
        socket.emit('send_battle_data', {'choice': toHightlight, 'amount': troopInput.value});
        toHightlight = [];
        // Sync clicks
        socket.emit('clear_otherHighlights');
        clickables = [];
        $('#proceed_next_stage').show();
      });
      $('#control_cancel').off('click').on('click' , function(){
        document.getElementById('control_panel').style.display = 'none';
        toHightlight = [];
        // Sync clicks
        socket.emit('clear_otherHighlights');
        clickables = [];
        $('#proceed_next_stage').show();
      });
   }
  }
}

// Update clickables to include the reachable territories for rearrangement
socket.on('update_clickables', function(data){
  clickables = data.trtys;
})

// Click function that handles rearrangement
function rearrange(tid){
  if (clickables.includes(tid) && tid != toHightlight[0]){
    if (toHightlight.length != 2){
      toHightlight.push(tid);
      // Sync clicks
      socket.emit('add_click_sync', {'tid': tid});
    }
    if (toHightlight.length == 2){
      toHightlight[1] = tid;
      // Sync clicks
      socket.emit('clear_otherHighlights');
      for (trty of toHightlight){
        socket.emit('add_click_sync', {'tid': trty});
      }
      document.getElementById('control_panel').style.display = 'none';
      document.getElementById('control_panel').style.display = 'flex';
      $('#proceed_next_stage').hide();

      let troopValue = document.createElement("p");
      troopValue.textContent = 1;
      let troopInput = document.createElement("input");

      // set shortcut id
      troopInput.setAttribute("id", "adjust_attack_amt");
      troopValue.setAttribute("id", "curr_attack_amt");

      curr_slider = "#adjust_attack_amt";
      curr_slider_val = "#curr_attack_amt";


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

      $('#control_confirm').off('click').on('click' , function(){
        document.getElementById('control_panel').style.display = 'none';
        socket.emit('send_rearrange_data', {'choice': toHightlight, 'amount': troopInput.value});
        toHightlight = [];
        socket.emit('clear_otherHighlights');
        clickables = [];
        $('#proceed_next_stage').show();
      });
      $('#control_cancel').off('click').on('click' , function(){
        document.getElementById('control_panel').style.display = 'none';
        toHightlight = [];
        socket.emit('clear_otherHighlights');
        clickables = [];
        $('#proceed_next_stage').show();
      });
   }
  }
  else if (player_territories.includes(tid)){
    document.getElementById('control_panel').style.display = 'none';
    $('#proceed_next_stage').show();
    clickables = [];
    if (territories[tid].troops == 1){
      popup("NOT ENOUGH TROOPS TO TRANSFER!", 1000);
      return;
    }
    if (toHightlight.length){
      toHightlight = [];
      socket.emit('clear_otherHighlights');
    }
    toHightlight.push(tid);
    socket.emit('add_click_sync', {'tid': tid});
    socket.emit("get_reachable_trty", {'choice': tid})
  }  
}

//=============================Concurrent Events=================================
socket.on('concurr_terminate_event_setup', function(data){
  $("#proceed_next_stage").show();
  $("#proceed_next_stage .text").text('DONE');
  $("#proceed_next_stage").off('click').on('click', function(){
    socket.emit('signal_concurr_end', {'pid': data.pid});
    $("#proceed_next_stage").hide(); 
    currEvent = null;
    toHightlight = [];
    clickables = [];
  });
});


//==============================INNER ASYNC======================================

// Set the button that can trigger a stop to the async event
socket.on('async_terminate_button_setup', function(){
    $("#proceed_next_stage").show();
    $("#proceed_next_stage .text").text('DONE');
    $("#proceed_next_stage").off('click').on('click', function(){
      socket.emit('signal_async_end');
      $("#proceed_next_stage").hide(); 
      currEvent = null;
      toHightlight = [];
      clickables = [];
    });
});

// Set and display the reserve amount for reserve deployment event
socket.on("reserve_deployment", function(data){
  reserves = data.amount;
  announ = document.getElementById('announcement');
  announ.innerHTML = `<h2>Deploying reserves, ${data.amount} troops available</h2>`;
});

// Set and display the city amount for city settlement event
socket.on('build_cities', function(data){
  city_amt = data.amount;
  announ = document.getElementById('announcement');
  announ.innerHTML = `<h2>Settling new cities, ${data.amount} under construction</h2>`
})

// Warning during city settlement
socket.on('update_settle_status', function(data){
  popup(data.msg, 3000);
})

// Click function for reserve deployment
function deploy_reserves(tid){
  toHightlight = [];
  document.getElementById('control_panel').style.display = 'none';
  if (player_territories.includes(tid)){
    toHightlight.push(tid);
    document.getElementById('control_panel').style.display = 'none';
    document.getElementById('control_panel').style.display = 'flex';
    let troopValue = document.createElement("p");
    troopValue.textContent = 1;
    let troopInput = document.createElement("input");

    // set shortcut id
    troopInput.setAttribute("id", "adjust_attack_amt");
    troopValue.setAttribute("id", "curr_attack_amt");

    curr_slider = "#adjust_attack_amt";
    curr_slider_val = "#curr_attack_amt";

    troopInput.setAttribute("type", "range");
    troopInput.setAttribute("min", 1);
    troopInput.setAttribute("max", reserves);
    troopInput.setAttribute("value", 1);
    troopInput.setAttribute("step", 1);
    troopInput.style.display = "inline-block";
    troopInput.addEventListener("input",function(){troopValue.textContent = troopInput.value;});
    let c_m = document.getElementById('control_mechanism');
    c_m.innerHTML = "";
    c_m.appendChild(troopInput);
    c_m.appendChild(troopValue);
    $('#control_confirm').off('click').on('click' , function(){
    document.getElementById('control_panel').style.display = 'none';
    socket.emit('send_reserves_deployed', {'choice': toHightlight[0], 'amount': troopInput.value});
    toHightlight = [];
    });
    $('#control_cancel').off('click').on('click' , function(){
      document.getElementById('control_panel').style.display = 'none';
      toHightlight = [];
    });
  }
}

// Click function to handle async city settlement
function build_cities(tid){
  if(player_territories.includes(tid) && city_amt >= 1){
    if (toHightlight.length == city_amt){
      toHightlight.splice(0, 1);
    }
    if (!toHightlight.includes(tid)){
      toHightlight.push(tid);
    }
    if (toHightlight.length == city_amt){
        $('#control_mechanism').empty();
        $('#control_panel').hide();
        $('#control_panel').show();
        $('#control_confirm').off('click').on('click', function(){
          $('#control_panel').hide();
          socket.emit('settle_cities', {'choice': toHightlight});
          toHightlight = [];
        });
        $('#control_cancel').off('click').on('click', function(){
          $('#control_panel').hide();
          toHightlight = [];
        });
    }
  }
}

//=========================== CONTROL BUTTONS ===================================

// DIPLOMATIC ACTIONS
// Add display + Functionalities to diplomatic button
btn_diplomatic = $('#btn-diplomatic');
btn_diplomatic.off('click').click(function () {
  document.getElementById('middle_display').style.display = 'flex';
  document.getElementById('middle_title').innerHTML = `
  <div class="flex items-center justify-between relative">
    <h4 class="text-lg font-semibold text-white flex-grow text-center">DIPLOMATIC ACTIONS</h4>
  </div>
`;
  midDis = document.getElementById('middle_content')

  // Alliance   Summit   Global Ceasefire
  midDis.innerHTML = `
  <div class="d-flex justify-content-between align-items-center">
      <div class="d-inline-block text-center">
          <button class="btn d-flex flex-column align-items-center" id="btn-summit" style="background-color: #BA6868; color:#FFFFFF; margin: 0 1px;" onmouseover="this.style.backgroundColor='#9E5454'"
    onmouseout="this.style.backgroundColor='#BA6868'">
              <img src="/static/Assets/Logo/summit.png"  style="max-height: 60px;">
              <span class="small mt-1">REQUEST SUMMIT</span>
          </button>
      </div>

      <div class="d-inline-block text-center">
          <button class="btn d-flex flex-column align-items-center" id="btn-globalpeace" style="background-color: #BA6868; color:#FFFFFF; margin: 0 1px;" onmouseover="this.style.backgroundColor='#9E5454'"
    onmouseout="this.style.backgroundColor='#BA6868'">
              <img src="/static/Assets/Logo/globalpeace.png" style="max-height: 60px;">
              <span class="small mt-1">GLOBAL CEASEFIRE</span>
          </button>
      </div>
  </div>

  <div class="flex items-center justify-center mt-2">
        <button id='btn-action-cancel' class="w-9 h-9 bg-red-700 text-white font-bold rounded-lg flex items-center justify-center">
            X
        </button>
  </div>
  `;

  // close window
  $('#btn-action-cancel').off('click').on('click', function(){
    $('#control_panel').hide()
    $('#middle_display').hide()
    $('#middle_title, #middle_content').empty()
  });

  // Summit button functionality
  $('#btn-summit').off('click').on('click', function(){
    socket.emit('request_summit')
    $('#middle_display').hide()
    $('#middle_title, #middle_content').empty();
  });

  // Ceasefire button functionality
  $('#btn-globalpeace').off('click').on('click', function(){
    socket.emit('request_global_peace')
    $('#middle_display').hide()
    $('#middle_title, #middle_content').empty();
  });

});

// VOTING EVENT FOR SUMMIT
socket.on('summit_voting', function(data){
  $("#announcement").html(`<h3>${data.msg}<h3>`);
  var votingSFX = [document.getElementById('votingSound1'), document.getElementById('votingSound2')];
  var randomIndex = Math.floor(Math.random() * votingSFX.length);
  votingSFX[randomIndex].volume = 0.7;
  votingSFX[randomIndex].play();
  $("#middle_display").show();
  let middis = $('#middle_content');
  // Voting menu with options + ul showing who voted what
  middis.html(`
    <div style="display: flex; flex-direction: column; justify-content: center; align-items: center;">
      <div style="display: flex; justify-content: space-between;"> 

        <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; margin:3px; align-self: flex-start;">
          <button id='btn_yes' class='btn btn-success' style='width:8vw; height:8vw;'>Accept</button>
          <div>
          <h5>Yes</h5>
          <ul id='voted_yes' style='list-style: none; padding: 0; margin: 0;'> </ul>
          </div>
        </div>

        <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; margin:3px; align-self: flex-start;">
          <button id='btn_no' class='btn btn-danger' style='width:8vw; height:8vw;'>Reject</button>
          <div>
          <h5>No</h5>
          <ul id='voted_no' style='list-style: none; padding: 0; margin: 0;'> </ul>
          </div>
        </div>

        <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; margin:3px; align-self: flex-start;">
          <button id='btn_abs' class='btn btn-warning' style='width:8vw; height:8vw;'>Abstain</button>
          <div>
          <h5>Whatever</h5>
          <ul id='voted_abs' style='list-style: none; padding: 0; margin: 0;'> </ul>
        </div>

      </div>
    </div>
  `);
  // For yes in summit
  $("#btn_yes").off('click').on('click', function(){
    $('#btn_yes, #btn_no, #btn_abs').hide();
    socket.emit("send_summit_choice", {'choice': 'y'});
  });
  // For no in summit
  $("#btn_no").off('click').on('click', function(){
    $('#btn_yes, #btn_no, #btn_abs').hide();
    socket.emit("send_summit_choice", {'choice': 'n'});
  });
  // For whatever in summit
  $("#btn_abs").off('click').on('click', function(){
    $('#btn_yes, #btn_no, #btn_abs').hide();
    socket.emit("send_summit_choice", {'choice': 'a'});
  });
});

// Summit Failed + Display the reason
socket.on('summit_failed', function(data){
  popup(data.msg, 3000);
  $("#middle_display").hide();
  $('#middle_title, #middle_content').empty();
});

// Update summit voting result
socket.on('s_voting_fb', function(data){
  if (data.opt == 'y'){
    $('#voted_yes').append(`<li>${data.name}</li>`);
  } else if (data.opt == 'n'){
    $('#voted_no').append(`<li>${data.name}</li>`);
  } else {
    $('#voted_abs').append(`<li>${data.name}</li>`);
  }
});

// Summit is activated, display announcement
socket.on('activate_summit', function(){
  $("#middle_display").hide();
  $('#middle_title, #middle_content').empty();
  $('#announcement').html(`<h3>Summit in progress...</h3>`)
});

// Function to get player's authority
async function get_sep_auth(){
  let amt = await new Promise((resolve) => {
    socket.emit('get_sep_auth');
    socket.once('receive_sep_auth', (data) => {resolve(data);});
  });
  return amt.amt;
}

// SPECIAL AUTHORITY
// Add display + Functionalities to special authority button
btn_sep_auth = document.getElementById('btn-sep-auth');
btn_sep_auth.onclick = function () {
  document.getElementById('middle_display').style.display = 'flex';
  // clear title
  document.getElementById('middle_title').innerHTML = "";
  // Grab the special authority amt of the user
  get_sep_auth().then(sep_auth => {
    
    // Show the title
    document.getElementById('middle_title').innerHTML = `
    <div style="padding: 5px;">
    <h5>SPECIAL AUTHORITY AVAILABLE: ${sep_auth}</h5>
    </div>`;

    // Show options  UPGRADE INFRASTRUCTURE | BUILD CITIES | MOBILIZATION
    midDis = document.getElementById('middle_content')
    midDis.innerHTML = `
    <div class="d-flex justify-content-between align-items-center">
      <div class="d-inline-block text-center">
          <button class="btn d-flex flex-column align-items-center" id="btn-ui" style="background-color: #58A680; color:#FFFFFF; margin: 0 1px;" onmouseover="this.style.backgroundColor='#3F805E'"
    onmouseout="this.style.backgroundColor='#58A680'">
              <img src="/static/Assets/Logo/transhubimprove.png" alt="Upgrade Infrastructure" style="max-height: 60px;">
              <span class="small mt-1">UPGRADE INFRASTRUCTURE</span>
          </button>
      </div>

      <div class="d-inline-block text-center">
          <button class="btn d-flex flex-column align-items-center" id="btn-bc" style="background-color: #6067A1; color:#FFFFFF; margin: 0 1px;" onmouseover="this.style.backgroundColor='#484E80'"
    onmouseout="this.style.backgroundColor='#6067A1'">
              <img src="/static/Assets/Logo/buildcity.png" alt="Build Cities" style="max-height: 60px;">
              <span class="small mt-1">BUILD CITIES</span>
          </button>
      </div>

      <div class="d-inline-block text-center">
          <button class="btn d-flex flex-column align-items-center" id="btn-mob" style="background-color: #A1606C; color:#FFFFFF; margin: 0 2px;" onmouseover="this.style.backgroundColor='#814B56'"
    onmouseout="this.style.backgroundColor='#A1606C'">
              <img src="/static/Assets/Logo/reservesincrease.png" alt="Mobilization" style="max-height: 60px;">
              <span class="small mt-1">MOBILIZATION</span>
          </button>
      </div>
    </div>

    <div class="flex items-center justify-center mt-2">
        <button id='btn-action-cancel' class="w-9 h-9 bg-red-700 text-white font-bold rounded-lg flex items-center justify-center">
            X
        </button>
    </div>
    `;

    // close window
    $('#btn-action-cancel').off('click').on('click', function(){
      $('#control_panel').hide()
      $('#middle_display').hide()
      $('#middle_title, #middle_content').empty()
    });

    // MOBILIZATION
    $("#btn-mob").off('click').on('click', function(){
      if (sep_auth < 2){
        popup('MINIMUM 2 STARS TO CONVERT TROOPS!', 2000);
        $("#middle_display").hide()
        $("#middle_title, #middle_content").empty();
        return;
      }
      let max = sep_auth > 15 ? 15 : sep_auth;
      $("#middle_content").html(
        `<p>Select amount to convert:</p>
         <input type="range" id="amtSlider" min="2" max=${max} step="1" value="2">
         <p id="samt">2</p>
         <button id="convertBtn" class="btn btn-success btn-block">Convert</button>
        `);
        $("#amtSlider").on('input', function(){$("#samt").text($("#amtSlider").val());});
        $("#convertBtn").on('click', function(){
          socket.emit('convert_reserves', {'amt': $("#amtSlider").val()});
          //Shutting off
          $('#middle_display').hide()
          $('#middle_title, #middle_content').empty();
        });
    });

    // BUILD NEW CITY
    $("#btn-bc").off('click').on('click', function() {
        if (sep_auth < 3)  {
          popup('MINIMUM 3 STARS TO BUILD CITIES!', 2000);
          $("#middle_display").hide()
          $("#middle_title, #middle_content").empty();
          return;
        }
        $("#middle_content").html(
          `<p>Select amount to convert:</p>
           <input type="range" id="amtSlider" min="1" max=${Math.floor(sep_auth/3)} step="1" value="1">
           <p id="samt">1</p>
           <button id="convertBtn" class="btn btn-success btn-block">Convert</button>
          `);
          $("#amtSlider").on('input', function(){$("#samt").text($("#amtSlider").val());});
          $("#convertBtn").on('click', function(){
            hide_async_btns();
            socket.emit('send_async_event', {'name': "B_C", 'amt': $("#amtSlider").val()});
            $('#middle_display').hide()
            $('#middle_title, #middle_content').empty();
          });
    });

    // UPGRADE INFRASTRUCTURE
    $("#btn-ui").off('click').on('click', function(){
      if (sep_auth < 4){
        popup('MINIMUM 4 STARS TO UPGRADE INFRASTRUCTURE!', 2000);
        $("#middle_display").hide()
        $("#middle_title, #middle_content").empty();
        return;
      }
      $("#middle_content").html(
        `<p>Select amount to convert:</p>
         <input type="range" id="amtSlider" min="1" max=${Math.floor(sep_auth/4)} step="1" value="1">
         <p id="samt">1</p>
         <button id="convertBtn" class="btn btn-success btn-block">Convert</button>
        `);
        $("#amtSlider").on('input', function(){$("#samt").text($("#amtSlider").val());});
        $("#convertBtn").on('click', function(){
          socket.emit('upgrade_infrastructure', {'amt': $("#amtSlider").val()});
          //Shutting off
          $('#middle_display').hide()
          $('#middle_title, #middle_content').empty();
        });
    });


  });
}

// Function to grab information concerning player's skill
async function get_skill_status(){
  let skillData = await new Promise((resolve) => {
    socket.emit('get_skill_information');
    socket.once('update_skill_status', (data) => {resolve(data);});
  });
  return skillData;
}
// SKILL USAGE
// Add display + Functionalities according to user's skill
btn_skill = document.getElementById('btn-skill');
btn_skill.onclick = function () {
  document.getElementById('middle_display').style.display = 'flex';
  document.getElementById('middle_title').innerHTML = "";
   // Grab the special authority amt of the user
   get_skill_status().then(skillData => {
    
    // operational
    var op_color = skillData.operational ? '#50C878' : '#E34234';
    var op_status = skillData.operational? 'Functional' : 'Disabled';
    // limit and cooldowns
    var limit_left = "";
    var cooldown_left = "";

    var showActivateBtn = "none";

    // determine limit and cooldown display
    if (skillData.operational) {
      if (skillData.hasLimit) {
        if (!skillData.limits) {
          limit_left = "No more usage available"
        } else {
          limit_left = `${skillData.limits} usages remaining`
          if (skillData.cooldown) {
            cooldown_left = `In cooldown | ${skillData.cooldown} rounds left`
          } else {
            cooldown_left = "Ready to activate"
            showActivateBtn = "flex";
          }
        }
      }
    }

    // single-turn skill activated
    var showInUse = "none";
    if (skillData.activated) {
      showActivateBtn = "none";
      showInUse = "flex";
    }

    // show targets that have been affected by skill if there are any
    let skill_used_targets = ``
    if (skillData.forbidden_targets) {
      if (skillData.forbidden_targets.length) {
        skill_used_targets += `
          <div style="max-height: 4rem; overflow-y: auto;">
            <div class="p-1 text-center break-words whitespace-normal">${skillData.ft_msg}</div>
            <div>
        `;
        for (let target of skillData.forbidden_targets) {
          skill_used_targets += (`
            <div style="display: inline-block;
              padding: 2px; margin: 2px; border-radius: 3px; background-color:#F5B301;"
              class="text-gray-700">${target}</div>
          `);
        }
        skill_used_targets += `</div></div>`;
      }
    }

    let skill_set_integer = ``;
    let showSepActivateBtn = 'none';
    // Show integer setting
    if (skillData.intset) {
      skill_set_integer += `
        <div style="display: flex; align-items: center; gap: 0.5rem;">
          <span>Running </strong>${skillData.intset}</strong> loops per battle, change to:</span>
          <input type="number" id="skillintdata" min="1" max="100" value="${skillData.intset}" 
                 style="width: 60px; padding: 2px; border: 1px solid #ccc; border-radius: 3px;">
        </div>
      `;
      showSepActivateBtn = 'flex';
      showActivateBtn = 'none';
    }
  
    // Show the title
    document.getElementById('middle_title').innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 2px;" class="text-center">
      <h5 style="margin-right: 15px">${skillData.name}</h5>
      <h5 style="background-color: ${op_color}; border-radius: 3px;" class="p-1">${op_status}</h5>
    </div>`;

    // Description | Show limits and cooldown if there are any | Show activation button
    midDis = document.getElementById('middle_content')
    midDis.innerHTML = `

    <div class="p-2 text-center break-words whitespace-normal" 
        style="max-height: calc(1.5em * 3); overflow-y: auto; line-height: 1.5;">
        ${skillData.description}
    </div>


    <div style="display: flex; justify-content: space-between; align-items: center;">

      <div style="display: inline-block;" class="p-2 mr-2 text-center break-words whitespace=normal">
      ${limit_left}
      </div>

      <div style="display: inline-block;" class="p-2 ml-2 text-center break-words whitespace=normal">
      ${cooldown_left}
      </div>

    </div>

    ${skill_used_targets}
    ${skill_set_integer}

    <div style="display: ${showInUse};" class="flex items-center justify-center p-2">
        <h3  style="border-radius: 3px; padding:2px;" class="text-center text-lg font-bold bg-yellow-500 text-black">
            ${skillData.inUseMsg}
        </h3>
    </div>

    <div style="display: ${showActivateBtn};" class="flex items-center justify-center mt-2">
        <button id='btn-skill-activate' class="p-3 bg-yellow-500 text-black font-bold rounded-md flex items-center justify-center">
            ${skillData.btn_msg}
        </button>
    </div>

    <div style="display: ${showSepActivateBtn};" class="flex items-center justify-center mt-2">
        <button id='btn-skill-activate-sep' class="p-3 bg-yellow-500 text-black font-bold rounded-md flex items-center justify-center">
            ${skillData.btn_msg}
        </button>
    </div>


    <div class="flex items-center justify-center mt-2">
        <button id='btn-action-cancel' class="w-9 h-9 bg-red-500 text-white font-bold rounded-lg flex items-center justify-center">
            X
        </button>
    </div>
    `;

    $('#btn-action-cancel').off('click').on('click', function(){
      $('#control_panel').hide()
      $('#middle_display').hide()
      $('#middle_title, #middle_content').empty()
    });

    $('#btn-skill-activate').off('click').on('click', function(){
      $('#control_panel').hide()
      $('#middle_display').hide()
      $('#middle_title, #middle_content').empty()
      socket.emit('signal_skill_usage');
    });

    $('#btn-skill-activate-sep').off('click').on('click', function () {

      // Safely get and validate the integer input
      let inputEl = document.getElementById('skillintdata');
      let intValue = skillData.intset; // fallback default
    
      if (inputEl) {
        let parsed = parseInt(inputEl.value, 10);
        if (!isNaN(parsed) && parsed >= 1 && parsed <= 100) {
          intValue = parsed;
        }
      }
    
      // Emit skill usage signal with data
      socket.emit('signal_skill_usage_with_data', {
        'intset': intValue
      });
      // Hide UI elements
      $('#control_panel, #middle_display').hide();
      $('#middle_title, #middle_content').empty();

    });

  });

}

// Function to grab the reserve amt for the user
async function get_reserves_amt(){
  let amt = await new Promise((resolve) => {
    socket.emit('get_reserves_amt');
    socket.once('receive_reserves_amt', (data) => {resolve(data);});
  });
  return amt.amt;
}

// RESERVE DEPLOYMENT
btn_reserves = document.getElementById("btn-reserve");
btn_reserves.onclick = function () {

  socket.emit('send_async_event', {'name': "R_D"});

}

// Industrial Revolution -> Free city building
socket.on('build_free_cities', function(){
  announ = document.getElementById('announcement');
  announ.innerHTML = `<h3>Settle new cities to boost your industrial power!</h3>`
});

// Free city building for industrial revolution
function build_free_cities(tid){
  if(player_territories.includes(tid)){
    if (!toHightlight.includes(tid)){
      toHightlight.push(tid);
    }
    if (toHightlight.length != 0){
        $('#control_mechanism').empty();
        $('#control_panel').hide();
        $('#control_panel').show();
        $('#control_confirm').off('click').on('click', function(){
          $('#control_panel').hide();
          socket.emit('build_free_cities', {'choice': toHightlight});
          toHightlight = [];
        });
        $('#control_cancel').off('click').on('click', function(){
          $('#control_panel').hide();
          toHightlight = [];
        });
    }
  }
}

// Orbital strike for divine punishment
socket.on('launch_orbital_strike', function(data){
  announ = document.getElementById('announcement');
  announ.innerHTML = `<h3>SELECT ENEMY TERRITORIES TO DESTROY!</h3>`;
  clickables = [];
  toHightlight = [];
  clickables = data.targets;
});

function launch_orbital_strike(tid){
  if(!player_territories.includes(tid)){
    if (!toHightlight.includes(tid) && clickables.includes(tid)){
      toHightlight.push(tid);
    }
    if (toHightlight.length != 0){
        $('#control_mechanism').empty();
        $('#control_panel').hide();
        $('#control_panel').show();
        $('#control_confirm').off('click').on('click', function(){
          $('#control_panel').hide();
          socket.emit('strike_targets', {'choice': toHightlight});
          toHightlight = [];
        });
        $('#control_cancel').off('click').on('click', function(){
          $('#control_panel').hide();
          toHightlight = [];
        });
    }
  }
}

// Air superiority
socket.on('paratrooper_attack', function(){
  announ = document.getElementById('announcement');
  announ.innerHTML = `<h4>PARATROOPERS ON STANDBY! READY TO LAUNCH SURPRISE ATTACK!</h4>`;
  clickables = [];
  toHightlight = [];
});

// Function to grab the reserve amt for the user
async function get_reachable_airspace(tid){
  let space = await new Promise((resolve) => {
    socket.emit('get_reachable_airspace', {'origin': tid});
    socket.once('receive_reachable_airspace', (data) => {resolve(data);});
  });
  return space.spaces;
}

function paratrooper_attack(tid){
  if(player_territories.includes(tid)){
    if (toHightlight.length){
      toHightlight = [];
      clickables = [];
    }
    toHightlight.push(tid);
    get_reachable_airspace(tid).then(spaces => {
      clickables = spaces
    }).catch(error => {
      console.error("Error getting reserve amount:", error); });
  } else if (!player_territories.includes(tid)){
    if (clickables.includes(tid)){
      if (toHightlight.length != 2){
        toHightlight.push(tid);
      }
      if (toHightlight.length == 2){
        toHightlight[1] = tid;

        document.getElementById('control_panel').style.display = 'none';
        document.getElementById('control_panel').style.display = 'flex';
        $('#proceed_next_stage').hide();
  
        let troopValue = document.createElement("p");
        let troopInput = document.createElement("input");
  
        // set shortcut id
        troopInput.setAttribute("id", "adjust_attack_amt");
        troopValue.setAttribute("id", "curr_attack_amt");
  
        curr_slider = "#adjust_attack_amt";
        curr_slider_val = "#curr_attack_amt";
  
        troopInput.setAttribute("type", "range");
        troopInput.setAttribute("min", 1);
        troopInput.setAttribute("max", territories[toHightlight[0]].troops-1);
        troopInput.setAttribute("value", 1);
        troopInput.setAttribute("step", 1);
        troopInput.style.display = "inline-block";
        troopInput.addEventListener("input",function(){troopValue.textContent = troopInput.value;});
        troopValue.textContent = 1;
        let c_m = document.getElementById('control_mechanism');
        c_m.innerHTML = "";
        c_m.appendChild(troopInput);
        c_m.appendChild(troopValue);
  
        $('#control_confirm').off('click').on('click' , function(){
          document.getElementById('control_panel').style.display = 'none';
          socket.emit('send_battle_stats_AS', {'choice': toHightlight, 'amount': troopInput.value});
          toHightlight = [];
          clickables = [];
          $('#proceed_next_stage').show();
        });
        $('#control_cancel').off('click').on('click' , function(){
          document.getElementById('control_panel').style.display = 'none';
          toHightlight = [];
          clickables = [];
          $('#proceed_next_stage').show();
        });
     }
    }
  }
}

// Collusion
socket.on('corrupt_territory', function(data){
  announ = document.getElementById('announcement');
  announ.innerHTML = `<h4>CHOOSE AN ENEMY TERRITORY TO CORRUPT!</h4>`;
  clickables = data.targets;
  toHightlight = [];
});

function corrupt_territory(tid){
  toHightlight = [];
  document.getElementById('control_panel').style.display = 'none';
  toHightlight.push(tid);
  document.getElementById('control_mechanism').innerHTML = '';
  document.getElementById('control_panel').style.display = 'none';
  document.getElementById('control_panel').style.display = 'flex';
  $('#proceed_next_stage').hide();
  $('#control_confirm').off('click').on('click' , function(){
    document.getElementById('control_panel').style.display = 'none';
    socket.emit('send_corrupt_territory', {'choice': toHightlight[0]});
    toHightlight = [];
  });
  $('#control_cancel').off('click').on('click' , function(){
    document.getElementById('control_panel').style.display = 'none';
    $('#proceed_next_stage').show();
    toHightlight = [];
  });
}

// Arsenal of the Underworld
socket.on('arsenal_controls', function(data) {
  // Get the middle_display card and show it
  let middleDisplay = $('#middle_display');
  let middleTitle = $('#middle_title');
  let middleContent = $('#middle_content');
  middleDisplay.show(); // Ensure the card is visible
  middleTitle.text('Arsenal Controls'); // Set the title
  middleContent.empty(); // Clear the content

  // Create container for descriptions and buttons
  let descriptionsDiv = $('<div></div>')
      .addClass('mb-3')
      .addClass('py-1')
      .css({
          'max-height': '6rem', // Max height for 3 lines
          'overflow-y': 'auto', // Enable scrolling if content exceeds max height
          'line-height': '1.2'  // Compact line spacing
      });

  let buttonsDiv = $('<div></div>')
      .addClass('d-flex justify-content-around'); // Buttons inline with spacing

  // Descriptions
  if (data.minefields && data.minefields.length > 0) {
      data.minefields.forEach(minefield => {
          descriptionsDiv.append(
              `<p style="margin: 0.2rem 0;">${minefield[0]} has ${minefield[1]} mines active.</p>`
          );
      });
  } else {
      descriptionsDiv.append('<p style="margin: 0.2rem 0;">No active minefields.</p>');
  }

  let availableMinefields = data.minefield_limit - (data.minefields ? data.minefields.length : 0);
  if (availableMinefields < 0) {
    availableMinefields = 0;
  }
  descriptionsDiv.append(
      `<p style="margin: 0.2rem 0;">${availableMinefields} available minefield placement.</p>`
  );

  if (data.silo_usable) {
      descriptionsDiv.append(
          `<p style="margin: 0.2rem 0;">Underground Silo active in ${data.underground_silo_location} | ${data.silo_usage} usages available for this round.</p>`
      );
  } else if (data.occupied) {
      descriptionsDiv.append('<p style="margin: 0.2rem 0;">Underground Silo Occupied by enemy forces.</p>');
  } else {
      descriptionsDiv.append('<p style="margin: 0.2rem 0;">No active underground silo.</p>');
  }

  // Buttons
  if (data.set_minefields) {
      let setMinefieldsButton = $('<button></button>')
          .addClass('btn btn-primary ml-2')
          .text('Set up minefields')
          .off('click') // Clear any existing click event handlers
          .click(function() {
              socket.emit('send_async_event', {'name': 'S_M'}); 
              $('#middle_display').hide();
              $('#middle_title').empty();
              $('#middle_content').empty(); 
          });
      buttonsDiv.append(setMinefieldsButton);
  }

  if (data.silo_build) {
      let buildSiloButton = $('<button></button>')
          .addClass('btn btn-success ml-2')
          .text('Build Silo')
          .click(function() {
              socket.emit('send_async_event', {'name': 'B_S'});
              $('#middle_display').hide();
              $('#middle_title').empty();
              $('#middle_content').empty(); 
          });
      buttonsDiv.append(buildSiloButton);
  }

  if (data.silo_usage && !data.occupied) {
      let launchSiloButton = $('<button></button>')
          .addClass('btn btn-danger ml-2')
          .text('Launch from Silo')
          .click(function() {
              socket.emit('launch_silo');
              $('#middle_display').hide();
              $('#middle_title').empty();
              $('#middle_content').empty(); 
          });
      buttonsDiv.append(launchSiloButton);
  }

  middleContent.append(descriptionsDiv);
  middleContent.append(buttonsDiv);
  middleContent.append(`
    <div style="display: flex; justify-content: center; margin-top: 3px;">
        <button id='btn-action-cancel' 
                class="w-9 h-9 bg-red-600 text-white font-bold rounded-lg flex items-center justify-center">
            X
        </button>
    </div>
  `);

  $('#btn-action-cancel').off('click').on('click', function() {
      $('#control_panel').hide();
      $('#middle_display').hide();
      $('#middle_title, #middle_content').empty();
  });
});


  // Set minefields
  socket.on('set_minefields', function(data){
    announ = document.getElementById('announcement');
    announ.innerHTML = `<h4>Choose territories to set up minefields! ${data.limits} can be set.</h4>`;
    clickables = data.targets;
    minefields_amount = data.limits;
    toHightlight = [];
  });

  function set_minefields(tid){
    if (!clickables.includes(tid)){
      return;
    }
    document.getElementById('control_panel').style.display = 'none';
    toHightlight.push(tid);
    if (toHightlight.length > minefields_amount) {
        toHightlight.shift();
    }
    document.getElementById('control_mechanism').innerHTML = '';
    document.getElementById('control_panel').style.display = 'none';
    document.getElementById('control_panel').style.display = 'flex';
    $('#proceed_next_stage').hide();
    $('#control_confirm').off('click').on('click' , function(){
      document.getElementById('control_panel').style.display = 'none';
      socket.emit('send_minefield_choices', {'choices': toHightlight});
      toHightlight = [];
    });
    $('#control_cancel').off('click').on('click' , function(){
      document.getElementById('control_panel').style.display = 'none';
      $('#proceed_next_stage').show();
      toHightlight = [];
    });
  }

  // set_underground_silo
  socket.on('set_underground_silo', function(data){
    announ = document.getElementById('announcement');
    announ.innerHTML = `<h4>Choose a territory to build underground silo! Only one silo can be built.</h4>`;
    clickables = data.targets;
    toHightlight = [];
  });

  function set_underground_silo(tid){
    if (!clickables.includes(tid)){
      return;
    }
    toHightlight = [];
    document.getElementById('control_panel').style.display = 'none';
    toHightlight.push(tid);
    document.getElementById('control_mechanism').innerHTML = '';
    document.getElementById('control_panel').style.display = 'none';
    document.getElementById('control_panel').style.display = 'flex';
    $('#proceed_next_stage').hide();
    $('#control_confirm').off('click').on('click' , function(){
      document.getElementById('control_panel').style.display = 'none';
      socket.emit('send_silo_location', {'choice': toHightlight[0]});
      toHightlight = [];
    });
    $('#control_cancel').off('click').on('click' , function(){
      document.getElementById('control_panel').style.display = 'none';
      $('#proceed_next_stage').show();
      toHightlight = [];
    });
  }

  // launch from silo
  socket.on('underground_silo_launch', function(data){
    announ = document.getElementById('announcement');
    announ.innerHTML = `<h4>Launching missiles from underground silo. Choose up to ${data.usages} targets!</h4>`;
    clickables = data.targets;
    US_usages = data.usages;
    toHightlight = [];
  });

  // launching from silo
  function underground_silo_launch(tid){
    if (!clickables.includes(tid)){
      return;
    }
    document.getElementById('control_panel').style.display = 'none';
    toHightlight.push(tid);
    if (toHightlight.length > US_usages) {
        toHightlight.shift();
    }
    document.getElementById('control_mechanism').innerHTML = '';
    document.getElementById('control_panel').style.display = 'none';
    document.getElementById('control_panel').style.display = 'flex';
    $('#proceed_next_stage').hide();
    $('#control_confirm').off('click').on('click' , function(){
      document.getElementById('control_panel').style.display = 'none';
      socket.emit('send_missile_targets', {'choices': toHightlight});
      toHightlight = [];
    });
    $('#control_cancel').off('click').on('click' , function(){
      document.getElementById('control_panel').style.display = 'none';
      $('#proceed_next_stage').show();
      toHightlight = [];
    });
  }

  socket.on('play_missile_sound', function(){
    var battleSFX = [document.getElementById('missile1'), document.getElementById('missile2')];
    var randomIndex = Math.floor(Math.random() * battleSFX.length);
    battleSFX[randomIndex].volume = 0.45;
    battleSFX[randomIndex].play();
  });

  // loan shark
  socket.on('make_ransom', function(data) {
    // Set the announcement message
    announ = document.getElementById('announcement');
    announ.innerHTML = `<h4>Choose a target to send your ransomware!</h4>`;

    // Ensure required elements are visible
    let middleDisplay = $('#middle_display');
    let middleTitle = $('#middle_title');
    let middleContent = $('#middle_content');

    middleDisplay.show();
    middleTitle.empty();
    middleContent.empty();

    // Create container for buttons
    let buttonContainer = $('<div></div>')
        .addClass('d-flex flex-wrap justify-content-between')
        .css({
            'max-height': '8rem',  // Limit the height to make it scrollable if too many rows
            'overflow-y': 'auto',  // Enable vertical scrolling
            'gap': '2px'          // Space between buttons
        });

    // Variable to track the currently selected button
    let selectedButton = null;

    // Loop through each target name and create buttons
    data.targets.forEach(function(name) {
        let button = $('<button></button>')
            .addClass('btn m-2')
            .css({
                'padding': '2px',
                'text-align': 'center',
                'background-color': '#FFC107', // Bootstrap warning color
                'color': '#333333' // Dark gray text
            })
            .text(name)
            .click(function(){
                // Remove red border from previously selected button
                if (selectedButton) {
                    selectedButton.css('border', 'none');
                }

                // Highlight the current button with a red border
                $(this).css({
                    'border': '2px solid red'
                });

                // Update the reference to the selected button
                selectedButton = $(this);

                // Show the control panel
                document.getElementById('control_mechanism').innerHTML = '';
                document.getElementById('control_panel').style.display = 'none';
                document.getElementById('control_panel').style.display = 'flex';
                $('#proceed_next_stage').hide();

                // Confirm button action
                $('#control_confirm').off('click').on('click', function(){
                    document.getElementById('control_panel').style.display = 'none';
                    socket.emit('send_ransom_target', {'choice': name});

                    // Clear middle content and title
                    middleTitle.empty();
                    middleContent.empty();

                    // Remove red border from selected button
                    if (selectedButton) {
                        selectedButton.css('border', 'none');
                        selectedButton = null;
                    }
                });

                // Cancel button action
                $('#control_cancel').off('click').on('click', function(){
                    document.getElementById('control_panel').style.display = 'none';
                    $('#proceed_next_stage').show();

                    // Remove red border from selected button
                    if (selectedButton) {
                        selectedButton.css('border', 'none');
                        selectedButton = null;
                    }
                });
            });

        buttonContainer.append(button);
    });

    // Add the button container to middle_content
    middleContent.append(buttonContainer);
    if (data.targets.length === 0) {
      middleContent.append('<p>No target available.</p>');
    }  
});


socket.on('show_debt_button', function(){
  popup("Your command system is currently restricted by enemy ransomware!", 3000);
  in_debt = true;
  $('#btn-debt').show();
  $('#btn-debt').off('click').on('click', function() {
    // Ensure middle_display, middle_title, and middle_content are visible and cleared
    let middleDisplay = $('#middle_display');
    let middleTitle = $('#middle_title');
    let middleContent = $('#middle_content');
    
    middleDisplay.show();
    middleTitle.empty();
    middleContent.empty();

    // Await for the "debt_info" event from the backend
    socket.on('debt_info', function(data) {
        // Clear existing content to avoid duplicate information
        middleTitle.empty();
        middleContent.empty();

        // Display debt information in a scrollable div
        let debtInfoDiv = $('<div></div>')
            .css({
                'max-height': '6rem', // Roughly 4 lines of text (6rem = 4 * 1.5rem per line)
                'overflow-y': 'auto',
                'margin-bottom': '10px'
            })
            .html(`
                <p>Current debt amount: ${data.debt_amount} troops, which is equivalent to ${Math.ceil(data.debt_amount / 5)} ★</p>
                <p>Your current reserves: ${data.curr_reserves}</p>
                <p>Your total troops: ${data.total_troops}</p>
                <p>Your current special authority: ${data.stars}★</p>
            `);

        // Create buttons for "Pay with ★" and "Pay with Troops"
        let payWithStarsButton = $('<button></button>')
            .addClass('btn btn-warning m-2')
            .css({
                'background-color': '#FF8C00', // Dark orange
                'color': '#333333', // Dark grey text
                'width': '45%',
                'text-align': 'center'
            })
            .text('Pay with ★')
            .on('click', function() {
                socket.emit('make_debt_payment', { 'method': 'sepauth' });
                middleDisplay.hide();
                middleTitle.empty();
                middleContent.empty();
            });

        let payWithTroopsButton = $('<button></button>')
            .addClass('btn btn-warning m-2')
            .css({
                'background-color': '#FF8C00', // Dark orange
                'color': '#333333', // Dark grey text
                'width': '45%',
                'text-align': 'center'
            })
            .text('Pay with troops')
            .on('click', function() {
                socket.emit('make_debt_payment', { 'method': 'troops' });
                middleDisplay.hide();
                middleTitle.empty();
                middleContent.empty();
            });

        // Create a button container to align "Pay with ★" and "Pay with troops" side by side
        let buttonContainer = $('<div></div>')
            .addClass('d-flex justify-content-between')
            .css({
                'gap': '10px'
            });

        buttonContainer.append(payWithStarsButton);
        buttonContainer.append(payWithTroopsButton);

        // Create the close button
        let closeButton = $('<button></button>')
            .addClass('btn m-2')
            .css({
                'background-color': 'red',
                'color': 'white',
                'width': '30%', // Small width to center it properly
                'margin': '10px auto', // Center horizontally
                'display': 'block', // Makes the button a block element
                'text-align': 'center'
            })
            .text('X')
            .on('click', function() {
                middleDisplay.hide();
                middleTitle.empty();
                middleContent.empty();
            });

        // Append everything to the content
        middleTitle.text('Debt Information');
        
        // Add the debt info, button container, and close button to the middle content
        middleContent.append(debtInfoDiv);
        middleContent.append(buttonContainer);
        middleContent.append(closeButton);
    });

    // Emit the event to fetch debt info
    socket.emit('fetch_debt_info');
  });
});

socket.on('debt_off', function(){
  in_debt = false;
  $('#btn-debt').hide();
});

//========================================================================================================

//============================================= Mouse events =============================================
function mouseWheel(event) {
    // Check if the mouse is in the game map layer
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
  
// Check if the mouse is in the overlay regions
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

// Initiate dragging
function mousePressed() {
  if(mouseX <= width && mouseY <= height){
    isDragging = true;
    previousMouseX = mouseX;
    previousMouseY = mouseY;
  }
}

// Stop dragging
function mouseReleased() {
  isDragging = false;
}

// Dragging
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

// CLICK FUNCTION ON TERRITORY
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

  // TO BE UPDATED
function keyPressed(){
  if (key === 'c'){
    scaleFactor = 1.0;
  }

  // shortcut for fast max deployment
  if (key === 'a'){
    if (curr_slider && curr_slider_val) {

      let $slider = $(curr_slider);
      let $sliderValue = $(curr_slider_val);

      $slider.val($slider.attr('max'));
      $sliderValue.text($slider.attr('max'));

      curr_slider = '';
      curr_slider_val = '';
    }
  }

  if (key === 's') {
    if (curr_slider && curr_slider_val) {
  
      let $slider = $(curr_slider);
      let $sliderValue = $(curr_slider_val);
      let maxVal = parseInt($slider.attr('max'), 10);
      let halfMax = Math.round(maxVal / 2);

      if (halfMax < 1) {
        halfMax = 1;
      }
  
      $slider.val(halfMax);
      $sliderValue.text(halfMax);
  
      curr_slider = '';
      curr_slider_val = '';
    }
  }

  if (key === 'd') {
    if (curr_slider && curr_slider_val) {
  
      let $slider = $(curr_slider);
      let $sliderValue = $(curr_slider_val);
      let maxVal = parseInt($slider.attr('max'), 10);
      let thirdMax = Math.round(maxVal / 3);

      if (thirdMax < 1) {
        thirdMax = 1;
      }
  
      $slider.val(thirdMax);
      $sliderValue.text(thirdMax);
  
      curr_slider = '';
      curr_slider_val = '';
    }
  }

}