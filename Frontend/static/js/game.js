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

// DISCOUNT
let discount = 0;

// Laplace Mode
let laplace_mode = false;
// Arsenal of Underworld
let minefields_amount = 0;
let US_usages = 0;
// Loan Shark
let in_debt = false;

let playCountdown = false;

const phaseMap = {
    'DEPLOY': { index: 1, class: 'phase-deploy', label: 'REINFORCEMENT' },
    'PREPARE': { index: 2, class: 'phase-prepare', label: 'PREPARATION' },
    'ATTACK': { index: 3, class: 'phase-attack', label: 'CONQUEST' },
    'REARRANGE': { index: 4, class: 'phase-rearrange', label: 'REARRANGEMENT' }
};

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
      if (showContBorders) {
        $(this).addClass('active');
      } else {
        $(this).removeClass('active');
      }
  });

  // Click propagation prevention
  $('#overlay_sections .card').on('click mousemove', function(event) {
      event.stopPropagation(); // Prevent click and mousemove events from reaching the background
  });

  $('#overlay_sections .bottom-action-button').on('click mousemove', function(event) {
    event.stopPropagation(); // Prevent click and mousemove events from reaching the background
  });

  $('#proceed_next_stage').on('click mousemove', function(event) {
    event.stopPropagation();
  });

  $('#control_panel').on('click mousemove', function(event) {
    event.stopPropagation();
  });

  $('#control_mechanism').on('click mousemove', function(event) {
      event.stopPropagation();
  });

  $('#your_stats, #global_overview').on('click mousemove wheel', function(event) {
    event.stopPropagation();
  });

  $('#tracker').on('click mousemove wheel', function(event) {
    event.stopPropagation();
  });

  $('#event_announcement').on('click mousemove', function(event) {
    event.stopPropagation();
  });


  async function tryLoadSketch() {
      // GAME_SKETCH LOGIC IS LOADED HERE WITH p5.js
      initializeLibraries();

  }

  tryLoadSketch();

});

function loadLibraries() {
  return new Promise((resolve) => {
    $.getScript(`${URL_FRONTEND}static/js/p5.js`, function() {
      $.getScript(`${URL_FRONTEND}static/js/p5.sound.js`, function() {
        resolve();
      });
    });
  });
}

async function initializeLibraries(){
  await loadLibraries();
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

    if (playCountdown) {
      var remaining = Math.round(progress * totalSeconds);
      if (remaining === 18 || remaining === 12 || remaining === 6) {
        var tmpCountdown = document.getElementById('countdown');
        tmpCountdown.volume = 0.55;
        tmpCountdown.play();
      }
    }

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

socket.on('set_countdown', function(){
  playCountdown = true;
});

// Stop timer animation
socket.on('stop_timeout', function(){
  clearInterval(current_interval);
  playCountdown = false;
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


// Prevent click and scroll propagation for laplace display
$('#laplace_info_display').on('click mousemove wheel', function(event) {
    event.stopPropagation();
});

socket.on('laplace_info', function(data) {
  var tcolor = 'rgb(245, 245, 245)';
  
  $('#laplace-content').empty();
  $('#laplace_info_display').css({
    'display': 'block'
  });

  $.each(data.info, function(fieldName, fieldValue) {
    $('#laplace-content').append(`
      <div class="laplace-info-item">
        <div class="laplace-field-name">${fieldName}</div>
        <div class="laplace-field-value">${fieldValue}</div>
      </div>
    `);
  });
});

// hide the display if clicked outside
$(document).on('click', function(event) {
  if (!$(event.target).closest('#laplace_info_display').length) {
    $('#laplace_info_display').hide();
    $('#laplace-content').empty();
  }
});

// prevent propagation if clicked on it
$('#laplace_info_display').on('click', function(event) {
  event.stopPropagation();
});



// Prevent click and scroll propagation
$('#player_info').on('click mousemove wheel', function(event) {
    event.stopPropagation();
});

// Scroll functionality
let scrollInterval = null;

$('#scroll-up').on('mousedown touchstart', function(e) {
    e.preventDefault();
    const statsList = $('#stats-list');
    scrollInterval = setInterval(() => {
        statsList.scrollTop(statsList.scrollTop() - 15);
    }, 20);
});

$('#scroll-down').on('mousedown touchstart', function(e) {
    e.preventDefault();
    const statsList = $('#stats-list');
    scrollInterval = setInterval(() => {
        statsList.scrollTop(statsList.scrollTop() + 15);
    }, 20);
});

$(document).on('mouseup touchend', function() {
    if (scrollInterval) {
        clearInterval(scrollInterval);
        scrollInterval = null;
    }
});

// Player stats list initiate
socket.on('get_players_stats', function(data){
  var pList = $('#stats-list');
  pList.empty();
  
  $.each(data, function(p, p_info) {
    var tcolor = 'rgb(245, 245, 245)';
    // if (isColorDark(p_info.color)){
    //   tcolor = 'rgb(245, 245, 245)';
    // }
    
    var pBtn = $('<button></button>')
      .attr('id', p)
      .addClass('player-stat-btn')
      .css({
        'color': tcolor
      })
      .html(`
        <div class="player-name-row">
          <div class="player-color-square" style="background-color: ${p_info.color};"></div>
          <div class="player-name">${p}</div>
        </div>
        <div class="player-stats-row">
          <div class="stat-item">
            <div class="stat-label">TERR</div>
            <div class="stat-value territory">
              <img src="/static/Assets/Logo/territory.svg" alt="Territory">
              <span>${p_info.trtys}</span>
            </div>
          </div>
          <div class="stat-item">
            <div class="stat-label">ARMY</div>
            <div class="stat-value troops">
              <img src="/static/Assets/Logo/soldier.svg" alt="Troops">
              <span>${p_info.troops}</span>
            </div>
          </div>
          <div class="stat-item">
            <div class="stat-label">PPI</div>
            <div class="stat-value power">
              <img src="/static/Assets/Logo/PPI.svg" alt="Power">
              <span>${p_info.PPI}</span>
            </div>
          </div>
        </div>
      `);
    
    pList.append(pBtn);
    
    pBtn.on('click', function(e) {
      e.stopPropagation();
      laplace_info_fetch(p_info.player_id);
    });
  });
});

// Player stats list update
socket.on('update_players_stats', function(data){
  let btn = $('#' + data.name);
  
  var tcolor = 'rgb(245, 245, 245)';
  // if (isColorDark(data.color)){
  //   tcolor = 'rgb(245, 245, 245)';
  // }
  
  btn.css('color', tcolor);
  btn.html(`
    <div class="player-name-row">
      <div class="player-color-square" style="background-color: ${data.color};"></div>
      <div class="player-name">${data.name}</div>
    </div>
    <div class="player-stats-row">
      <div class="stat-item">
        <div class="stat-label">TERR</div>
        <div class="stat-value territory">
          <img src="/static/Assets/Logo/territory.svg" alt="Territory">
          <span>${data.trtys}</span>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-label">ARMY</div>
        <div class="stat-value troops">
          <img src="/static/Assets/Logo/soldier.svg" alt="Troops">
          <span>${data.troops}</span>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-label">PPI</div>
        <div class="stat-value power">
          <img src="/static/Assets/Logo/PPI.svg" alt="Power">
          <span>${data.PPI}</span>
        </div>
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
  $('#curr_indus').text(data.curr_indus);
  $('#curr_nul_rate').text(data.curr_nul_rate);
  $('#curr_dmg_mul').text(data.curr_dmg_mul);
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
        } else if (changes[field] == 'megacity'){
          territories[tid].devImg = megacityImage;
        } else if (changes[field] == 'nexus') {
          territories[tid].devImg = nexusImage;
        } else if (changes[field] == 'bureau') {
          territories[tid].devImg = bureauImage;
        } else {
          territories[tid].devImg = null;
        }
      // Skill effects
      } else if (field == 'hasEffect') {
        if (changes[field] == 'nuke') {
          territories[tid].insig = radioImage;
        } else if (changes[field] == 'fort') {
          territories[tid].insig = fortImage;
        } else if (changes[field] == 'hall') {
          territories[tid].hallImg = hallImage;
        } else if (changes[field] == 'leyline') {
          territories[tid].leylineImg = leylineImage;
        } else if (changes[field] == 'leylineGone') {
          territories[tid].leylineImg = null;
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
  } else if (data.event == 'raise_megacities') {
    currEvent = raise_megacities;
  } else if (data.event == 'set_forts') {
    currEvent = set_forts;
  } else if (data.event == 'set_hall') {
    currEvent = set_hall;
  } else if (data.event == 'set_nexus') {
    currEvent = set_nexus;
  } else if (data.event == 'set_leyline') {
    currEvent = set_leyline;
  } else if (data.event == 'set_bureau') {
    currEvent = set_bureau;
  } else if (data.event == 'build_free_cities') {
    currEvent = build_free_cities;
  } else if (data.event == 'build_free_leyline_crosses') {
    currEvent = build_free_leyline_crosses;
  } else if (data.event == 'establish_pillars') {
    currEvent = establish_pillars;
  } else if (data.event == 'launch_orbital_strike_offturn') {
    currEvent = launch_orbital_strike_offturn;
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
  $('#control_panel, #control_mechanism, #middle_display, #proceed_next_stage').hide();
  toHighLight = [];
  otherHighlight = [];
  clickables = [];
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

// Game over
socket.on('GAME_OVER', function(data) {
  $('#gameEndSound').trigger('play');
  $('#btn-diplomatic, #btn-sep-auth, #btn-skill, #btn-reserve, #btn-debt').hide();
  currEvent = null;
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

function playTap(){
  $('#tap').prop('volume', 0.5).trigger('play');
}

function playRefuse(){
  $('#refuse').prop('volume', 0.5).trigger('play');
}

// SFX
socket.on('playSFX', function(data){
  if (data.sfx == "alarm") {
        var alarm = document.getElementById('alarm');
        alarm.volume = 0.35;
        alarm.play();
  } else if (data.sfx == "blessing") {
        var blessing = document.getElementById('blessing');
        blessing.volume = 0.35;
        blessing.play();
  } else if (data.sfx == "sanction") {
        var sanction = document.getElementById('sanction');
        sanction.volume = 0.35;
        sanction.play();
  }
})

// Explosion
socket.on('explosion_animation', function(data){
    explodeAtTerritory(data.tid, { power: 320, sparks: 56, smoke: 20, withRing: true });
});

// Nuke
socket.on('nuke_animation', function(data){
    var tid = data.tid;
    if (tid == null || tid < 0 || tid >= territories.length) return;
    const c = territories[tid].cps;   // world coords
    spawnMegaNuke(c.x, c.y);
});

// Missile
socket.on('arsenal_animation', function(data){
    var tid = data.tid;
    if (tid == null || tid < 0 || tid >= territories.length) return;
    const c = territories[tid].cps; 
    spawnCluster(c.x, c.y, 5, 100);
});


//===============================Mission Related Display=============================================


// Initiate mission tracker
socket.on('initiate_tracker', function(data){
  if (data.targets || data.misProgBar || data.misProgDesp) {
    $('.winning_condition').show();
  }
  if (data.lossProg || data.lossDesp) {
    $('.losing_condition').show();
  }
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

  if (data.renewed_targets) {
    $misTargets.empty();

    for (const target in data.renewed_targets) {
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

socket.on('set_new_announcement', function(data) {
    const announcement = $('#announcement');
    const phaseIndicators = $('#phase_indicators');
    
    if (data.async) {
        // Async message - simple display
        phaseIndicators.hide();
        announcement.html(`<div class="async-message">${data.msg}</div>`);
    } else {
        // Turn-based event with phase indicators
        phaseIndicators.show();
        
        const phase = data.curr_phase.toUpperCase();
        const phaseInfo = phaseMap[phase];
        
        if (phaseInfo) {
            // Update phase boxes
            $('.phase-box').removeClass('completed active');
            
            $('.phase-box').each(function(index) {
                const boxPhase = index + 1;
                if (boxPhase < phaseInfo.index) {
                    $(this).addClass('completed'); // Red X
                } else if (boxPhase === phaseInfo.index) {
                    $(this).addClass('active'); // Yellow pulsing
                }
                // else stays gray (default)
            });
            
            // Update phase name
            announcement.html(`
                <div class="phase-label">CURRENT PHASE</div>
                <div class="phase-name ${phaseInfo.class}">${phaseInfo.label}${data.msg}</div>
            `);
        } else {
            // Fallback for unknown phases
            phaseIndicators.hide();
            announcement.html(`<div class="async-message">${data.msg || phase}</div>`);
        }
    }
});

//======================================================================================================

//=====================================SET UP EVENTS====================================================

// Start Color Choosing
socket.on('choose_color', function(data){
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
            playRefuse();
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
              toHighLight.push(tmptid);
            }
            tmptid ++;
          }

          document.getElementById('control_panel').style.display = 'flex';
          $('#control_confirm').off('click').on('click', function(){
            document.getElementById('control_panel').style.display = 'none';
            socket.emit('send_dist_choice', {'choice': rgbToHex(btn_dist.style.backgroundColor)})
            document.getElementById('middle_display').style.display = 'none';
            toHighLight = []; 
          });
          $('#control_cancel').off('click').on('click' , function(){
            document.getElementById('control_panel').style.display = 'none';
            disabled = false;
            btn_dist.style.border = "none";
            toHighLight = [];
            playRefuse();
          });
        }
      };
      dist_choices.appendChild(btn_dist);
  }
});

// Set capital
function settle_capital(tid){
  toHighLight = [];
  document.getElementById('control_panel').style.display = 'none';
  if (player_territories.includes(tid)){
    toHighLight.push(tid);
    document.getElementById('control_panel').style.display = 'none';
    document.getElementById('control_panel').style.display = 'flex';
    $('#control_confirm').off('click').on('click', function(){
      document.getElementById('control_panel').style.display = 'none';
      socket.emit('send_capital_choice', {'choice': toHighLight[0], 'tid': tid});
      toHighLight = [];
    });
    $('#control_cancel').off('click').on('click' , function(){
      document.getElementById('control_panel').style.display = 'none';
      toHighLight = [];
      playRefuse();
    });
  }
}

// Set cities
function settle_cities(tid){
  if(player_territories.includes(tid)){
    if (toHighLight.length == 2){
      toHighLight.splice(0, 1);
    }
    if (!toHighLight.includes(tid)){
      toHighLight.push(tid);
    }
    if (toHighLight.length == 2){
        document.getElementById('control_panel').style.display = 'none';
        document.getElementById('control_panel').style.display = 'flex';
        $('#control_confirm').off('click').on('click' , function(){
        document.getElementById('control_panel').style.display = 'none';
        socket.emit('send_city_choices', {'choice': toHighLight});
        toHighLight = [];
        });
        $('#control_cancel').off('click').on('click' , function(){
        document.getElementById('control_panel').style.display = 'none';
        toHighLight = [];
        playRefuse();
        });
    }
  }
}

// Set feedback for capital and city setting events
socket.on('settle_result', function(data){
  if (data.resp){
    currEvent = null;
    toHighLight = [];
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
          playRefuse();
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
  // Add glassy + glow + font weight styling
  descBox.style.position = 'absolute';
  descBox.style.top = '20%';
  descBox.style.backdropFilter = 'blur(6px)';
  descBox.style.border = '1px solid rgba(255, 255, 255, 0.2)';
  descBox.style.boxShadow = `
    0 0 10px rgba(255, 255, 150, 0.3),
    inset 0 0 4px rgba(255, 255, 100, 0.2)
  `;
  descBox.style.fontWeight = '500'; // semi-bold
  descBox.style.textShadow = '0 0 2px rgba(255, 255, 100, 0.3)';

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
});

// Show the button that ends the preparation stage
socket.on('preparation', function(){
  $('#proceed_next_stage').show();
  $('#proceed_next_stage .button-text').text('Start Conquest');
  $('#proceed_next_stage').off('click').on('click', () => {
    $('#proceed_next_stage').hide();
    socket.emit("terminate_preparation_stage");
    currEvent = null;
    toHighLight = [];
    clickables = [];
  });
});

// Show the button that ends the conquest stage
socket.on('conquest', function(){
  $('#proceed_next_stage').show();
  $('#proceed_next_stage .button-text').text('Finish Conquest');
  $('#proceed_next_stage').off('click').on('click', () => {
    $('#proceed_next_stage').hide();

    document.getElementById('control_panel').style.display = 'none';
    document.getElementById('control_panel').style.display = 'flex';
    $('#proceed_next_stage').hide();
    $('#control_confirm').off('click').on('click' , function(){
      document.getElementById('control_panel').style.display = 'none';
      socket.emit("terminate_conquer_stage");
      currEvent = null;
      toHighLight = [];
      clickables = [];
    });
    $('#control_cancel').off('click').on('click' , function(){
      document.getElementById('control_panel').style.display = 'none';
      $('#proceed_next_stage').show();
      playRefuse();
    });

  });
});

// Show the button that ends the rearrangement stage
socket.on('rearrangement', function(){
  $('#proceed_next_stage').show();
  $('#proceed_next_stage .button-text').text('Finish Rearrangement');
  $('#proceed_next_stage').off('click').on('click', () => {
    $('#proceed_next_stage').hide();
    socket.emit("terminate_rearrangement_stage");
    currEvent = null;
    toHighLight = [];
    clickables = [];
  });
});

// Click function that handles troop deployment (for initial and turn-based troop deployment)
function troop_deployment(tid){
  toHighLight = [];
  document.getElementById('control_panel').style.display = 'none';
  document.getElementById('control_mechanism').style.display = 'none';
  if (player_territories.includes(tid)){
    toHighLight.push(tid);
    
    // Sync clicks
    socket.emit('add_click_sync', {'tid': tid});

    document.getElementById('control_mechanism').style.display = 'none';
    document.getElementById('control_mechanism').style.display = 'block';
    
    let troopInput = document.getElementById('control_slider');
    let troopValue = document.getElementById('control_value');

    troopInput.setAttribute("min", 1);
    troopInput.setAttribute("max", deployable);
    troopInput.setAttribute("value", 1);
    troopValue.textContent = 1;

    // Force reset to 1 by setting to different value first, then back to 1
    troopInput.value = 0;
    setTimeout(() => {
        troopInput.value = 1;
        troopValue.textContent = 1;
        // Reset slider background to position 0%
        troopInput.style.background = `linear-gradient(to right, rgb(34, 211, 238) 0%, rgb(34, 211, 238) 0%, rgb(51, 65, 85) 0%, rgb(51, 65, 85) 100%)`;
    }, 0);

    // Remove old event listeners to prevent duplicates
    troopInput.removeEventListener("input", troopInput.inputHandler);

    // Create new event handler
    troopInput.inputHandler = function() {
        troopValue.textContent = troopInput.value;
        const percentage = ((troopInput.value - troopInput.min) / (troopInput.max - troopInput.min)) * 100;
        troopInput.style.background = `linear-gradient(to right, rgb(34, 211, 238) 0%, rgb(34, 211, 238) ${percentage}%, rgb(51, 65, 85) ${percentage}%, rgb(51, 65, 85) 100%)`;
    };

    troopInput.addEventListener("input", troopInput.inputHandler);

    curr_slider = '#control_slider';
    curr_slider_val = '#control_value';

    document.getElementById('control_panel').style.display = 'none';
    document.getElementById('control_panel').style.display = 'flex';

    $('#control_confirm').off('click').on('click' , function(){
    document.getElementById('control_panel').style.display = 'none';
    document.getElementById('control_mechanism').style.display = 'none';
    socket.emit('send_troop_update', {'choice': toHighLight[0], 'amount': troopInput.value});
    toHighLight = [];

    curr_slider = '';
    curr_slider_val = '';

    // Sync clicks
    socket.emit('remove_click_sync', {'tid': tid});

    });
    
    $('#control_cancel').off('click').on('click' , function(){
      document.getElementById('control_mechanism').style.display = 'none';
      document.getElementById('control_panel').style.display = 'none';
      toHighLight = [];
      playRefuse();

      curr_slider = '';
      curr_slider_val = '';
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
    toHighLight = [];
    deployable = 0;
    currEvent = null;
  }
})

// Click function that handles conquest
function conquest(tid){
  if (player_territories.includes(tid)){
    document.getElementById('control_panel').style.display = 'none';
    document.getElementById('control_mechanism').style.display = 'none';
    $('#proceed_next_stage').show();
    clickables = [];
    if (toHighLight.length){
      toHighLight = [];
      // clear sync clicks
      socket.emit('clear_otherHighlights');
    }
    if (territories[tid].troops <= 1){
      popup("NOT ENOUGH TROOPS FOR BATTLE!", 1000);
      return
    }
    toHighLight.push(tid);
    // Sync clicks
    socket.emit('add_click_sync', {'tid': tid});

    clickables = territories[tid].neighbors.filter(tmp_id => territories[tid].color !== territories[tmp_id].color);
    
  } else if (clickables.includes(tid)){
    if (toHighLight.length != 2){
      toHighLight.push(tid);
      // Sync clicks
      socket.emit('add_click_sync', {'tid': tid});
    }
    if (toHighLight.length == 2){
      toHighLight[1] = tid;
      // Sync clicks
      socket.emit('clear_otherHighlights');
      for (trty of toHighLight){
        socket.emit('add_click_sync', {'tid': trty});
      }

      document.getElementById('control_mechanism').style.display = 'none';
      document.getElementById('control_mechanism').style.display = 'block';
      
      document.getElementById('control_panel').style.display = 'none';
      document.getElementById('control_panel').style.display = 'flex';
      $('#proceed_next_stage').hide();

      let troopInput = document.getElementById('control_slider');
      let troopValue = document.getElementById('control_value');

      troopInput.setAttribute("min", 1);
      troopInput.setAttribute("max", territories[toHighLight[0]].troops-1);
      troopInput.setAttribute("value", 1);
      troopValue.textContent = 1;

      troopInput.value = 0;
      setTimeout(() => {
          troopInput.value = 1;
          troopValue.textContent = 1;
          // Reset slider background to position 0%
          troopInput.style.background = `linear-gradient(to right, rgb(34, 211, 238) 0%, rgb(34, 211, 238) 0%, rgb(51, 65, 85) 0%, rgb(51, 65, 85) 100%)`;
      }, 0);

      // Remove old event listeners to prevent duplicates
      troopInput.removeEventListener("input", troopInput.inputHandler);

      // Create new event handler
      troopInput.inputHandler = function() {
          troopValue.textContent = troopInput.value;
          const percentage = ((troopInput.value - troopInput.min) / (troopInput.max - troopInput.min)) * 100;
          troopInput.style.background = `linear-gradient(to right, rgb(34, 211, 238) 0%, rgb(34, 211, 238) ${percentage}%, rgb(51, 65, 85) ${percentage}%, rgb(51, 65, 85) 100%)`;
      };

      troopInput.addEventListener("input", troopInput.inputHandler);

      curr_slider = '#control_slider';
      curr_slider_val = '#control_value';

      $('#control_confirm').off('click').on('click' , function(){
        document.getElementById('control_panel').style.display = 'none';
        document.getElementById('control_mechanism').style.display = 'none';
        socket.emit('send_battle_data', {'choice': toHighLight, 'amount': troopInput.value});
        toHighLight = [];
        // Sync clicks
        socket.emit('clear_otherHighlights');
        clickables = [];
        
        curr_slider = '';
        curr_slider_val = '';
        $('#proceed_next_stage').show();
      });
      $('#control_cancel').off('click').on('click' , function(){
        playRefuse();
        document.getElementById('control_panel').style.display = 'none';
        document.getElementById('control_mechanism').style.display = 'none';
        toHighLight = [];
        // Sync clicks
        socket.emit('clear_otherHighlights');
        clickables = [];

        curr_slider = '';
        curr_slider_val = '';

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
  if (clickables.includes(tid) && tid != toHighLight[0]){
    if (toHighLight.length != 2){
      toHighLight.push(tid);
      // Sync clicks
      socket.emit('add_click_sync', {'tid': tid});
    }
    if (toHighLight.length == 2){
      toHighLight[1] = tid;
      // Sync clicks
      socket.emit('clear_otherHighlights');
      for (trty of toHighLight){
        socket.emit('add_click_sync', {'tid': trty});
      }
      document.getElementById('control_panel').style.display = 'none';
      document.getElementById('control_panel').style.display = 'flex';

      document.getElementById('control_mechanism').style.display = 'none';
      document.getElementById('control_mechanism').style.display = 'block';

      $('#proceed_next_stage').hide();

      let troopInput = document.getElementById('control_slider');
      let troopValue = document.getElementById('control_value');

      troopInput.setAttribute("min", 1);
      troopInput.setAttribute("max", territories[toHighLight[0]].troops-1);
      troopInput.setAttribute("value", 1);
      troopValue.textContent = 1;

      // Force reset to 1 by setting to different value first, then back to 1
      troopInput.value = 0;
      setTimeout(() => {
          troopInput.value = 1;
          troopValue.textContent = 1;
          // Reset slider background to position 0%
          troopInput.style.background = `linear-gradient(to right, rgb(34, 211, 238) 0%, rgb(34, 211, 238) 0%, rgb(51, 65, 85) 0%, rgb(51, 65, 85) 100%)`;
      }, 0);

      // Remove old event listeners to prevent duplicates
      troopInput.removeEventListener("input", troopInput.inputHandler);

      // Create new event handler
      troopInput.inputHandler = function() {
          troopValue.textContent = troopInput.value;
          const percentage = ((troopInput.value - troopInput.min) / (troopInput.max - troopInput.min)) * 100;
          troopInput.style.background = `linear-gradient(to right, rgb(34, 211, 238) 0%, rgb(34, 211, 238) ${percentage}%, rgb(51, 65, 85) ${percentage}%, rgb(51, 65, 85) 100%)`;
      };

      troopInput.addEventListener("input", troopInput.inputHandler);

      curr_slider = '#control_slider';
      curr_slider_val = '#control_value';

      $('#control_confirm').off('click').on('click' , function(){
        document.getElementById('control_panel').style.display = 'none';
        document.getElementById('control_mechanism').style.display = 'none';
        socket.emit('send_rearrange_data', {'choice': toHighLight, 'amount': troopInput.value});
        toHighLight = [];
        socket.emit('clear_otherHighlights');
        clickables = [];

        curr_slider = '';
        curr_slider_val = '';
        $('#proceed_next_stage').show();
      });
      $('#control_cancel').off('click').on('click' , function(){playRefuse();
        document.getElementById('control_panel').style.display = 'none';
        document.getElementById('control_mechanism').style.display = 'none';
        toHighLight = [];
        socket.emit('clear_otherHighlights');
        clickables = [];

        curr_slider = '';
        curr_slider_val = '';
        $('#proceed_next_stage').show();
      });
   }
  }
  else if (player_territories.includes(tid)){
    document.getElementById('control_panel').style.display = 'none';
    document.getElementById('control_mechanism').style.display = 'none';
    $('#proceed_next_stage').show();
    clickables = [];
    if (territories[tid].troops == 1){
      popup("NOT ENOUGH TROOPS TO TRANSFER!", 1000);
      return;
    }
    if (toHighLight.length){
      toHighLight = [];
      socket.emit('clear_otherHighlights');
    }
    toHighLight.push(tid);
    socket.emit('add_click_sync', {'tid': tid});
    socket.emit("get_reachable_trty", {'choice': tid})
  }  
}

//=============================Concurrent Events=================================
socket.on('concurr_terminate_event_setup', function(data){
  $("#proceed_next_stage").show();
  $("#proceed_next_stage .button-text").text('DONE');
  $("#proceed_next_stage").off('click').on('click', function(){
    socket.emit('signal_concurr_end', {'pid': data.pid});
    $("#proceed_next_stage").hide(); 
    currEvent = null;
    toHighLight = [];
    clickables = [];
  });
});


//==============================INNER ASYNC======================================

// Set the button that can trigger a stop to the async event
socket.on('async_terminate_button_setup', function(){
    $("#proceed_next_stage").show();
    $("#proceed_next_stage .button-text").text('DONE');
    $("#proceed_next_stage").off('click').on('click', function(){
      socket.emit('signal_async_end');
      $("#proceed_next_stage").hide(); 
      currEvent = null;
      toHighLight = [];
      clickables = [];
    });
});

// Set and display the reserve amount for reserve deployment event
socket.on("reserve_deployment", function(data){
  reserves = data.amount;
});

// Set and display the city amount for city settlement event
socket.on('build_cities', function(data){
  city_amt = data.amount;
})

socket.on('set_forts', function(data){
  city_amt = data.amount;
  clickables = [];
  toHighLight = [];
  clickables = data.flist;
})

socket.on('set_hall', function(data){
  city_amt = data.amount;
  clickables = [];
  toHighLight = [];
  clickables = data.flist;
})

socket.on('set_nexus', function(data){
  city_amt = data.amount;
  clickables = [];
  toHighLight = [];
  clickables = data.flist;
})

socket.on('set_leyline', function(data){
  city_amt = data.amount;
  clickables = [];
  toHighLight = [];
  clickables = data.flist;
})

socket.on('set_bureau', function(data){
  city_amt = data.amount;
  clickables = [];
  toHighLight = [];
  clickables = data.flist;
})

// Set and display the city amount for megacity settlement event
socket.on('raise_megacities', function(data){
  city_amt = data.amount;
  clickables = [];
  toHighLight = [];
  clickables = data.clist;
})

// Warning during city settlement
socket.on('update_settle_status', function(data){
  popup(data.msg, 3000);
})

// Click function for reserve deployment
function deploy_reserves(tid){
  toHighLight = [];
  document.getElementById('control_panel').style.display = 'none';
  document.getElementById('control_mechanism').style.display = 'none';
  if (player_territories.includes(tid)){
    toHighLight.push(tid);
    document.getElementById('control_panel').style.display = 'none';
    document.getElementById('control_panel').style.display = 'flex';

    document.getElementById('control_mechanism').style.display = 'none';
    document.getElementById('control_mechanism').style.display = 'block';

    let troopInput = document.getElementById('control_slider');
    let troopValue = document.getElementById('control_value');

    troopInput.setAttribute("min", 1);
    troopInput.setAttribute("max", reserves);
    troopInput.setAttribute("value", 1);
    troopValue.textContent = 1;

    // Force reset to 1 by setting to different value first, then back to 1
    troopInput.value = 0;
    setTimeout(() => {
        troopInput.value = 1;
        troopValue.textContent = 1;
        // Reset slider background to position 0%
        troopInput.style.background = `linear-gradient(to right, rgb(34, 211, 238) 0%, rgb(34, 211, 238) 0%, rgb(51, 65, 85) 0%, rgb(51, 65, 85) 100%)`;
    }, 0);

    // Remove old event listeners to prevent duplicates
    troopInput.removeEventListener("input", troopInput.inputHandler);

    // Create new event handler
    troopInput.inputHandler = function() {
        troopValue.textContent = troopInput.value;
        const percentage = ((troopInput.value - troopInput.min) / (troopInput.max - troopInput.min)) * 100;
        troopInput.style.background = `linear-gradient(to right, rgb(34, 211, 238) 0%, rgb(34, 211, 238) ${percentage}%, rgb(51, 65, 85) ${percentage}%, rgb(51, 65, 85) 100%)`;
    };

    troopInput.addEventListener("input", troopInput.inputHandler);

    curr_slider = '#control_slider';
    curr_slider_val = '#control_value';

    $('#control_confirm').off('click').on('click' , function(){
    document.getElementById('control_panel').style.display = 'none';
    document.getElementById('control_mechanism').style.display = 'none';
    socket.emit('send_reserves_deployed', {'choice': toHighLight[0], 'amount': troopInput.value});
    toHighLight = [];
    curr_slider = '';
    curr_slider_val = '';
    });
    $('#control_cancel').off('click').on('click' , function(){playRefuse();
      document.getElementById('control_panel').style.display = 'none';
      document.getElementById('control_mechanism').style.display = 'none';
      toHighLight = [];
      curr_slider = '';
      curr_slider_val = '';
    });
  }
}

// Click function to handle async city settlement
function build_cities(tid){
  if(player_territories.includes(tid) && city_amt >= 1){
    if (toHighLight.length == city_amt){
      toHighLight.splice(0, 1);
    }
    if (!toHighLight.includes(tid)){
      toHighLight.push(tid);
    }
    if (toHighLight.length == city_amt){
        $('#control_panel').hide();
        document.getElementById('control_mechanism').style.display = 'none';
        $('#control_panel').show();
        $('#control_confirm').off('click').on('click', function(){
          $('#control_panel').hide();
          socket.emit('settle_cities', {'choice': toHighLight});
          toHighLight = [];
        });
        $('#control_cancel').off('click').on('click', function(){playRefuse();
          $('#control_panel').hide();
          toHighLight = [];
        });
    }
  }
}

function raise_megacities(tid){
  if(clickables.includes(tid) && city_amt >= 1){
    if (toHighLight.length == city_amt){
      toHighLight.splice(0, 1);
    }
    if (!toHighLight.includes(tid)){
      toHighLight.push(tid);
    }
    if (toHighLight.length == city_amt){
        $('#control_panel').hide();
        document.getElementById('control_mechanism').style.display = 'none';
        $('#control_panel').show();
        $('#control_confirm').off('click').on('click', function(){
          $('#control_panel').hide();
          socket.emit('settle_megacities', {'choice': toHighLight});
          toHighLight = [];
        });
        $('#control_cancel').off('click').on('click', function(){playRefuse();
          $('#control_panel').hide();
          toHighLight = [];
        });
    }
  }
}

function set_forts(tid){
  if(clickables.includes(tid) && city_amt >= 1){
    if (toHighLight.length == city_amt){
      toHighLight.splice(0, 1);
    }
    if (!toHighLight.includes(tid)){
      toHighLight.push(tid);
    }
    if (toHighLight.length == city_amt){
        $('#control_panel').hide();
        document.getElementById('control_mechanism').style.display = 'none';
        $('#control_panel').show();
        $('#control_confirm').off('click').on('click', function(){
          $('#control_panel').hide();
          socket.emit('settle_forts', {'choice': toHighLight});
          toHighLight = [];
        });
        $('#control_cancel').off('click').on('click', function(){playRefuse();
          $('#control_panel').hide();
          toHighLight = [];
        });
    }
  }
}

function set_hall(tid){
  if(clickables.includes(tid) && city_amt >= 1){
    if (toHighLight.length == city_amt){
      toHighLight.splice(0, 1);
    }
    if (!toHighLight.includes(tid)){
      toHighLight.push(tid);
    }
    if (toHighLight.length == city_amt){
        $('#control_panel').hide();
        document.getElementById('control_mechanism').style.display = 'none';
        $('#control_panel').show();
        $('#control_confirm').off('click').on('click', function(){
          $('#control_panel').hide();
          socket.emit('settle_hall', {'choice': toHighLight});
          toHighLight = [];
        });
        $('#control_cancel').off('click').on('click', function(){playRefuse();
          $('#control_panel').hide();
          toHighLight = [];
        });
    }
  }
}

function set_nexus(tid){
  if(clickables.includes(tid) && city_amt >= 1){
    if (toHighLight.length == city_amt){
      toHighLight.splice(0, 1);
    }
    if (!toHighLight.includes(tid)){
      toHighLight.push(tid);
    }
    if (toHighLight.length == city_amt){
        $('#control_panel').hide();
        document.getElementById('control_mechanism').style.display = 'none';
        $('#control_panel').show();
        $('#control_confirm').off('click').on('click', function(){
          $('#control_panel').hide();
          socket.emit('settle_nexus', {'choice': toHighLight});
          toHighLight = [];
        });
        $('#control_cancel').off('click').on('click', function(){playRefuse();
          $('#control_panel').hide();
          toHighLight = [];
        });
    }
  }
}

function set_leyline(tid){
  if(clickables.includes(tid) && city_amt >= 1){
    if (toHighLight.length == city_amt){
      toHighLight.splice(0, 1);
    }
    if (!toHighLight.includes(tid)){
      toHighLight.push(tid);
    }
    if (toHighLight.length == city_amt){
        $('#control_panel').hide();
        $('#control_panel').show();
        $('#control_confirm').off('click').on('click', function(){
          $('#control_panel').hide();
          socket.emit('settle_leyline', {'choice': toHighLight});
          toHighLight = [];
        });
        $('#control_cancel').off('click').on('click', function(){playRefuse();
          $('#control_panel').hide();
          toHighLight = [];
        });
    }
  }
}

function set_bureau(tid){
  if(clickables.includes(tid) && city_amt >= 1){
    if (toHighLight.length == city_amt){
      toHighLight.splice(0, 1);
    }
    if (!toHighLight.includes(tid)){
      toHighLight.push(tid);
    }
    if (toHighLight.length == city_amt){
        $('#control_panel').hide();
        $('#control_panel').show();
        $('#control_confirm').off('click').on('click', function(){
          $('#control_panel').hide();
          socket.emit('settle_bureau', {'choice': toHighLight});
          toHighLight = [];
        });
        $('#control_cancel').off('click').on('click', function(){playRefuse();
          $('#control_panel').hide();
          toHighLight = [];
        });
    }
  }
}

//=========================== CONTROL BUTTONS ===================================

// DIPLOMATIC ACTIONS
// Add display + Functionalities to diplomatic button
btn_diplomatic = $('#btn-diplomatic');
btn_diplomatic.off('click').click(function () {
  $('#control_panel').hide();
  $('#control_mechanism').hide();
  clickables = []
  toHighLight = []
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
    document.getElementById('control_mechanism').style.display = 'none';
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
socket.on('summit_voting', function(){
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

// Summit is activated
socket.on('activate_summit', function(){
  $("#middle_display").hide();
  $('#middle_title, #middle_content').empty();
});

// Discounted price displayer
function starPrice(base) {
  const discounted = base - discount;
  return discounted > 1 ? discounted : 1;
}

// Function to get player's authority
async function get_sep_auth(){
  let amt = await new Promise((resolve) => {
    socket.emit('get_sep_auth');
    socket.once('receive_sep_auth', (data) => {resolve(data);});
  });
  return amt;
}

// SPECIAL AUTHORITY
// Add display + Functionalities to special authority button
btn_sep_auth = document.getElementById('btn-sep-auth');
btn_sep_auth.onclick = function () {
  $('#control_panel').hide();
  $('#control_mechanism').hide();
  clickables = []
  toHighLight = []
  document.getElementById('middle_display').style.display = 'flex';
  // clear title
  document.getElementById('middle_title').innerHTML = "";
  // Grab the special authority amt of the user
  get_sep_auth().then(sep_auth => {
    
    // Show the title
    document.getElementById('middle_title').innerHTML = `
    <div style="padding: 5px;">
    <h5>SPECIAL AUTHORITY AVAILABLE: ${sep_auth.amt}</h5>
    </div>`;

    discount = sep_auth.discount;
    sep_auth = sep_auth.amt

    // Show options  UPGRADE INFRASTRUCTURE | BUILD CITIES | MOBILIZATION
    midDis = document.getElementById('middle_content')
    midDis.innerHTML = `
<style>
  .scroll-wrapper {
    max-height: 250px;
    overflow-y: auto;
    padding: 0;
    margin: 0;
  }

  .button-grid {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 8px;
    padding: 4px;
  }

  .action-button {
    width: 120px;
    height: 72px;
    border-radius: 6px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.25);
    padding: 3px 4px;
    transition: transform 0.1s ease-in-out;
    overflow: hidden;
  }

  .action-button:hover {
    transform: scale(1.04);
  }

  .action-button img {
    max-height: 38px;
    max-width: 53px;
  }

  .price-tag {
    font-size: 0.85rem;
    font-weight: bold;
    margin-left: 4px;
  }

  .hover-label {
    display: none;
    position: absolute;
    bottom: 110%;
    left: 50%;
    transform: translateX(-50%);
    font-size: 0.7rem;
    padding: 3px 6px;
    border-radius: 4px;
    white-space: nowrap;
    z-index: 100;
  }

  .action-button:hover .hover-label {
    display: block;
  }

  .action-button span.small {
    margin-top: 2px;
    font-size: 0.85rem;
  }

  .cancel-btn-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 8px;
  }

  .cancel-btn {
    width: 36px;
    height: 36px;
    background-color: #B91C1C;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    display: flex;
    justify-content: center;
    align-items: center;
  }
</style>

<div class="scroll-wrapper">
  <div class="button-grid">

    <div class="text-center">
      <button id="btn-ui" class="btn d-flex flex-column align-items-center justify-content-center action-button"
              style="background-color: #58A680; color:#FFFFFF;"
              onmouseover="this.style.backgroundColor='#3F805E'; this.querySelector('.hover-label').style.backgroundColor='#3F805E'; this.querySelector('.hover-label').style.color='#FFFFFF';"
              onmouseout="this.style.backgroundColor='#58A680'; this.querySelector('.hover-label').style.backgroundColor='#58A680'; this.querySelector('.hover-label').style.color='#FFFFFF';">
        <div class="d-flex align-items-center justify-content-center">
          <img src="/static/Assets/Logo/transhubimprove.png" alt="Infrastructure">
          <span class="price-tag" style="color: #FFFFFF;">${starPrice(3)}☆</span>
        </div>
        <span class="small">INFRASTRUCTURE</span>
        <div class="hover-label">Improve transport hubs</div>
      </button>
    </div>

    <div class="text-center">
      <button id="btn-bc" class="btn d-flex flex-column align-items-center justify-content-center action-button"
              style="background-color: #6067A1; color:#FFFFFF;"
              onmouseover="this.style.backgroundColor='#484E80'; this.querySelector('.hover-label').style.backgroundColor='#484E80'; this.querySelector('.hover-label').style.color='#FFFFFF';"
              onmouseout="this.style.backgroundColor='#6067A1'; this.querySelector('.hover-label').style.backgroundColor='#6067A1'; this.querySelector('.hover-label').style.color='#FFFFFF';">
        <div class="d-flex align-items-center justify-content-center">
          <img src="/static/Assets/Logo/buildcity.png" alt="Build Cities">
          <span class="price-tag" style="color: #FFFFFF;">${starPrice(3)}☆</span>
        </div>
        <span class="small">BUILD CITIES</span>
        <div class="hover-label">Expand urban development</div>
      </button>
    </div>

    <div class="text-center">
      <button id="btn-mob" class="btn d-flex flex-column align-items-center justify-content-center action-button"
              style="background-color: #A1606C; color:#FFFFFF;"
              onmouseover="this.style.backgroundColor='#814B56'; this.querySelector('.hover-label').style.backgroundColor='#814B56'; this.querySelector('.hover-label').style.color='#FFFFFF';"
              onmouseout="this.style.backgroundColor='#A1606C'; this.querySelector('.hover-label').style.backgroundColor='#A1606C'; this.querySelector('.hover-label').style.color='#FFFFFF';">
        <div class="d-flex align-items-center justify-content-center">
          <img src="/static/Assets/Logo/reservesincrease.png" alt="Mobilization">
          <span class="price-tag" style="color: #FFFFFF;">2-15☆</span>
        </div>
        <span class="small">MOBILIZATION</span>
        <div class="hover-label">Recruit reserve forces</div>
      </button>
    </div>

    <div class="text-center">
      <button id="btn-mega" class="btn d-flex flex-column align-items-center justify-content-center action-button"
              style="background-color: #FDB13F; color:#000000;"
              onmouseover="this.style.backgroundColor='#FDBB4E'; this.querySelector('.hover-label').style.backgroundColor='#FDBB4E'; this.querySelector('.hover-label').style.color='#000000';"
              onmouseout="this.style.backgroundColor='#FDB13F'; this.querySelector('.hover-label').style.backgroundColor='#FDB13F'; this.querySelector('.hover-label').style.color='#000000';">
        <div class="d-flex align-items-center justify-content-center">
          <img src="/static/Assets/Dev/megacity.png" alt="Megacity">
          <span class="price-tag" style="color: #000000;">${starPrice(5)}☆</span>
        </div>
        <span class="small">RAISE MEGACITY</span>
        <div class="hover-label">Create economic powerhouse</div>
      </button>
    </div>

    <div class="text-center">
      <button id="btn-fort" class="btn d-flex flex-column align-items-center justify-content-center action-button"
              style="background-color: #878787; color:#FFFFFF;"
              onmouseover="this.style.backgroundColor='#444444'; this.querySelector('.hover-label').style.backgroundColor='#444444'; this.querySelector('.hover-label').style.color='#FFFFFF';"
              onmouseout="this.style.backgroundColor='#878787'; this.querySelector('.hover-label').style.backgroundColor='#878787'; this.querySelector('.hover-label').style.color='#FFFFFF';">
        <div class="d-flex align-items-center justify-content-center">
          <img src="/static/Assets/Insig/fort.png" alt="Fort">
          <span class="price-tag" style="color: #FFFFFF;">1☆</span>
        </div>
        <span class="small">SET UP FORTS</span>
        <div class="hover-label">Establish defense base</div>
      </button>
    </div>

    <div class="text-center">
      <button id="btn-hall" class="btn d-flex flex-column align-items-center justify-content-center action-button"
              style="background-color: #6C3BAA; color:#FFFFFF;"
              onmouseover="this.style.backgroundColor='#CC8899'; this.querySelector('.hover-label').style.backgroundColor='#CC8899'; this.querySelector('.hover-label').style.color='#FFFFFF';"
              onmouseout="this.style.backgroundColor='#6C3BAA'; this.querySelector('.hover-label').style.backgroundColor='#6C3BAA'; this.querySelector('.hover-label').style.color='#FFFFFF';">
        <div class="d-flex align-items-center justify-content-center">
          <img src="/static/Assets/Insig/CAD.png" alt="Hall of Governance">
          <span class="price-tag" style="color: #FFFFFF;">${starPrice(5)}☆</span>
        </div>
        <span class="small" style="font-size: 0.7rem;">HALL OF GOVERNANCE</span>
        <div class="hover-label">Extend administrative control</div>
      </button>
    </div>

    <div class="text-center">
      <button id="btn-nexus" class="btn d-flex flex-column align-items-center justify-content-center action-button"
              style="background-color: #A8DCAB; color:#000000;"
              onmouseover="this.style.backgroundColor='#8CB88E'; this.querySelector('.hover-label').style.backgroundColor='#8CB88E'; this.querySelector('.hover-label').style.color='#000000';"
              onmouseout="this.style.backgroundColor='#A8DCAB'; this.querySelector('.hover-label').style.backgroundColor='#A8DCAB'; this.querySelector('.hover-label').style.color='#000000';">
        <div class="d-flex align-items-center justify-content-center">
          <img src="/static/Assets/Dev/transhub.png" alt="Nexus">
          <span class="price-tag" style="color: #000000;">${starPrice(4)}☆</span>
        </div>
        <span class="small">LOGISTIC NEXUS</span>
        <div class="hover-label">Centralize distribution</div>
      </button>
    </div>

    <div class="text-center">
      <button id="btn-leyline" class="btn d-flex flex-column align-items-center justify-content-center action-button"
              style="background-color: #6987D5; color:#000000;"
              onmouseover="this.style.backgroundColor='#BBDFFA'; this.querySelector('.hover-label').style.backgroundColor='#BBDFFA'; this.querySelector('.hover-label').style.color='#000000';"
              onmouseout="this.style.backgroundColor='#6987D5'; this.querySelector('.hover-label').style.backgroundColor='#6987D5'; this.querySelector('.hover-label').style.color='#000000';">
        <div class="d-flex align-items-center justify-content-center">
          <img src="/static/Assets/Insig/leyline.png" alt="Leyline">
          <span class="price-tag" style="color: #000000;">${starPrice(2)}☆</span>
        </div>
        <span class="small">LEYLINE CROSS</span>
        <div class="hover-label">Channel mystic energies</div>
      </button>
    </div>

    <div class="text-center">
      <button id="btn-bureau" class="btn d-flex flex-column align-items-center justify-content-center action-button"
              style="background-color: #2C5F34; color:#FFFFFF;"
              onmouseover="this.style.backgroundColor='#5D6532'; this.querySelector('.hover-label').style.backgroundColor='#5D6532'; this.querySelector('.hover-label').style.color='#000000';"
              onmouseout="this.style.backgroundColor='#2C5F34'; this.querySelector('.hover-label').style.backgroundColor='#2C5F34'; this.querySelector('.hover-label').style.color='#000000';">
        <div class="d-flex align-items-center justify-content-center">
          <img src="/static/Assets/Insig/mobbureau.png" alt="Bureau">
          <span class="price-tag" style="color: #FFFFFF;">${starPrice(2)}☆</span>
        </div>
        <span class="small" style="font-size: 0.7rem;">MOBILIZATION BUREAU</span>
        <div class="hover-label">Enable troop call-ups</div>
      </button>
    </div>

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
      document.getElementById('control_mechanism').style.display = 'none';
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
        let curr_price = starPrice(3);
        if (sep_auth < curr_price)  {
          popup(`MINIMUM ${curr_price} STARS TO BUILD CITIES!`, 2000);
          $("#middle_display").hide()
          $("#middle_title, #middle_content").empty();
          return;
        }
        $("#middle_content").html(
          `<p>Select amount to convert:</p>
           <input type="range" id="amtSlider" min="1" max=${Math.floor(sep_auth/curr_price)} step="1" value="1">
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
      let curr_price = starPrice(3);
      if (sep_auth < curr_price){
        popup(`MINIMUM ${curr_price} STARS TO UPGRADE INFRASTRUCTURE!`, 2000);
        $("#middle_display").hide()
        $("#middle_title, #middle_content").empty();
        return;
      }
      $("#middle_content").html(
        `<p>Select amount to convert:</p>
         <input type="range" id="amtSlider" min="1" max=${Math.floor(sep_auth/curr_price)} step="1" value="1">
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

    // RAISE MEGACITY
    $("#btn-mega").off('click').on('click', function(){
      let curr_price = starPrice(5);
      if (sep_auth < curr_price){
        popup(`MINIMUM ${curr_price} STARS TO RAISE MEGACITY!`, 2000);
        $("#middle_display").hide()
        $("#middle_title, #middle_content").empty();
        return;
      }
      $("#middle_content").html(
        `<p>Select number of Megacities to raise:</p>
          <input type="range" id="amtSlider" min="1" max=${Math.floor(sep_auth/curr_price)} step="1" value="1">
          <p id="samt">1</p>
          <button id="convertBtn" class="btn btn-success btn-block">Raise</button>
        `);
        $("#amtSlider").on('input', function(){$("#samt").text($("#amtSlider").val());});
        $("#convertBtn").on('click', function(){
          hide_async_btns();
          socket.emit('send_async_event', {'name': "R_M", 'amt': $("#amtSlider").val()});
          $('#middle_display').hide()
          $('#middle_title, #middle_content').empty();
        });
    });

    // Fortified
    $("#btn-fort").off('click').on('click', function(){
      if (sep_auth < 1){
        popup('MINIMUM 1 STAR TO SET UP FORT!', 2000);
        $("#middle_display").hide()
        $("#middle_title, #middle_content").empty();
        return;
      }
      $("#middle_content").html(
        `<p>Select number of forts to set up:</p>
          <input type="range" id="amtSlider" min="1" max=${Math.floor(sep_auth/1)} step="1" value="1">
          <p id="samt">1</p>
          <button id="convertBtn" class="btn btn-success btn-block">Set Up</button>
        `);
        $("#amtSlider").on('input', function(){$("#samt").text($("#amtSlider").val());});
        $("#convertBtn").on('click', function(){
          hide_async_btns();
          socket.emit('send_async_event', {'name': "S_F", 'amt': $("#amtSlider").val()});
          $('#middle_display').hide()
          $('#middle_title, #middle_content').empty();
        });
    });

    // Hall of Governance
    $("#btn-hall").off('click').on('click', function(){
      let curr_price = starPrice(5);
      if (sep_auth < curr_price){
        popup(`MINIMUM ${curr_price} STARS TO SET UP HALL!`, 2000);
        $("#middle_display").hide()
        $("#middle_title, #middle_content").empty();
        return;
      }
      $("#middle_content").html(
        `<p>Select number of Halls of Governance to set up:</p>
          <input type="range" id="amtSlider" min="1" max=${Math.floor(sep_auth/curr_price)} step="1" value="1">
          <p id="samt">1</p>
          <button id="convertBtn" class="btn btn-success btn-block">Install</button>
        `);
        $("#amtSlider").on('input', function(){$("#samt").text($("#amtSlider").val());});
        $("#convertBtn").on('click', function(){
          hide_async_btns();
          socket.emit('send_async_event', {'name': "S_H", 'amt': $("#amtSlider").val()});
          $('#middle_display').hide()
          $('#middle_title, #middle_content').empty();
        });
    });

    // Logistic Nexus
    $("#btn-nexus").off('click').on('click', function(){
      let curr_price = starPrice(4);
      if (sep_auth < curr_price){
        popup(`MINIMUM ${curr_price} STARS TO BUILD A NEXUS!`, 2000);
        $("#middle_display").hide()
        $("#middle_title, #middle_content").empty();
        return;
      }
      $("#middle_content").html(
        `<p>Select number of Logistic Nexus:</p>
          <input type="range" id="amtSlider" min="1" max=${Math.floor(sep_auth/curr_price)} step="1" value="1">
          <p id="samt">1</p>
          <button id="convertBtn" class="btn btn-success btn-block">Build</button>
        `);
        $("#amtSlider").on('input', function(){$("#samt").text($("#amtSlider").val());});
        $("#convertBtn").on('click', function(){
          hide_async_btns();
          socket.emit('send_async_event', {'name': "L_N", 'amt': $("#amtSlider").val()});
          $('#middle_display').hide()
          $('#middle_title, #middle_content').empty();
        });
    });

    // Leyline Cross
    $("#btn-leyline").off('click').on('click', function(){
      let curr_price = starPrice(2);
      if (sep_auth < curr_price){
        popup(`MINIMUM ${curr_price} STARS TO BUILD A LEYLINE CROSS!`, 2000);
        $("#middle_display").hide()
        $("#middle_title, #middle_content").empty();
        return;
      }
      $("#middle_content").html(
        `<p>Select number of Leyline Cross:</p>
          <input type="range" id="amtSlider" min="1" max=${Math.floor(sep_auth/curr_price)} step="1" value="1">
          <p id="samt">1</p>
          <button id="convertBtn" class="btn btn-success btn-block">Settle</button>
        `);
        $("#amtSlider").on('input', function(){$("#samt").text($("#amtSlider").val());});
        $("#convertBtn").on('click', function(){
          hide_async_btns();
          socket.emit('send_async_event', {'name': "L_C", 'amt': $("#amtSlider").val()});
          $('#middle_display').hide()
          $('#middle_title, #middle_content').empty();
        });
    });

    // Mobilization Bureau
    $("#btn-bureau").off('click').on('click', function(){
      let curr_price = starPrice(2);
      if (sep_auth < curr_price){
        popup(`MINIMUM ${curr_price} STARS TO BUILD A MOBILIZATION BUREAU!`, 2000);
        $("#middle_display").hide()
        $("#middle_title, #middle_content").empty();
        return;
      }
      $("#middle_content").html(
        `<p>Select number of bureaus:</p>
          <input type="range" id="amtSlider" min="1" max=${Math.floor(sep_auth/curr_price)} step="1" value="1">
          <p id="samt">1</p>
          <button id="convertBtn" class="btn btn-success btn-block">Settle</button>
        `);
        $("#amtSlider").on('input', function(){$("#samt").text($("#amtSlider").val());});
        $("#convertBtn").on('click', function(){
          hide_async_btns();
          socket.emit('send_async_event', {'name': "M_B", 'amt': $("#amtSlider").val()});
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
  $('#control_panel').hide();
  $('#control_mechanism').hide();
  clickables = []
  toHighLight = []
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
      document.getElementById('control_mechanism').style.display = 'none';
      $('#middle_display').hide()
      $('#middle_title, #middle_content').empty()
    });

    $('#btn-skill-activate').off('click').on('click', function(){
      $('#control_panel').hide()
      document.getElementById('control_mechanism').style.display = 'none';
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
      document.getElementById('control_mechanism').style.display = 'none';
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
  $('#control_panel').hide();
  $('#control_mechanism').hide();
  clickables = []
  toHighLight = []
  socket.emit('send_async_event', {'name': "R_D"});

}

function establish_pillars(tid){
  if(player_territories.includes(tid)){
    if (!toHighLight.includes(tid)){
      toHighLight.push(tid);
    }
    if (toHighLight.length != 0){
        $('#control_panel').hide();
        document.getElementById('control_mechanism').style.display = 'none';
        $('#control_panel').show();
        $('#control_confirm').off('click').on('click', function(){
          $('#control_panel').hide();
          socket.emit('settle_pillars', {'choice': toHighLight});
          toHighLight = [];
        });
        $('#control_cancel').off('click').on('click', function(){playRefuse();
          $('#control_panel').hide();
          toHighLight = [];
        });
    }
  }
}

function build_free_leyline_crosses(tid){
  if(player_territories.includes(tid)){
    if (!toHighLight.includes(tid)){
      toHighLight.push(tid);
    }
    if (toHighLight.length != 0){
        $('#control_panel').hide();
        $('#control_panel').show();
        $('#control_confirm').off('click').on('click', function(){
          $('#control_panel').hide();
          socket.emit('build_free_leyline_crosses', {'choice': toHighLight});
          toHighLight = [];
        });
        $('#control_cancel').off('click').on('click', function(){playRefuse();
          $('#control_panel').hide();
          toHighLight = [];
        });
    }
  }
}

// Industrial Revolution -> Free city building

// Free city building for industrial revolution
function build_free_cities(tid){
  if(player_territories.includes(tid)){
    if (!toHighLight.includes(tid)){
      toHighLight.push(tid);
    }
    if (toHighLight.length != 0){
        $('#control_panel').hide();
        $('#control_panel').show();
        $('#control_confirm').off('click').on('click', function(){
          $('#control_panel').hide();
          socket.emit('build_free_cities', {'choice': toHighLight});
          toHighLight = [];
        });
        $('#control_cancel').off('click').on('click', function(){playRefuse();
          $('#control_panel').hide();
          toHighLight = [];
        });
    }
  }
}

// Orbital strike for divine punishment
socket.on('launch_orbital_strike', function(data){
  clickables = [];
  toHighLight = [];
  clickables = data.targets;
});

function launch_orbital_strike(tid){
  if(!player_territories.includes(tid)){
    if (!toHighLight.includes(tid) && clickables.includes(tid)){
      toHighLight.push(tid);
    }
    if (toHighLight.length != 0){
        $('#control_panel').hide();
        $('#control_panel').show();
        $('#control_confirm').off('click').on('click', function(){
          $('#control_panel').hide();
          socket.emit('strike_targets', {'choice': toHighLight});
          toHighLight = [];
        });
        $('#control_cancel').off('click').on('click', function(){playRefuse();
          $('#control_panel').hide();
          toHighLight = [];
        });
    }
  }
}

// Air superiority
socket.on('paratrooper_attack', function(){
  clickables = [];
  toHighLight = [];
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
    if (toHighLight.length){
      toHighLight = [];
      clickables = [];
    }
    toHighLight.push(tid);
    get_reachable_airspace(tid).then(spaces => {
      clickables = spaces
    }).catch(error => {
      console.error("Error getting reserve amount:", error); });
  } else if (!player_territories.includes(tid)){
    if (clickables.includes(tid)){
      if (toHighLight.length != 2){
        toHighLight.push(tid);
      }
      if (toHighLight.length == 2){
        toHighLight[1] = tid;

        document.getElementById('control_panel').style.display = 'none';
        document.getElementById('control_panel').style.display = 'flex';

        document.getElementById('control_mechanism').style.display = 'none';
        document.getElementById('control_mechanism').style.display = 'block';
        $('#proceed_next_stage').hide();
  
        let troopInput = document.getElementById('control_slider');
        let troopValue = document.getElementById('control_value');

        troopInput.setAttribute("min", 1);
        troopInput.setAttribute("max", territories[toHighLight[0]].troops-1);
        troopInput.setAttribute("value", 1);
        troopValue.textContent = 1;

        // Force reset to 1 by setting to different value first, then back to 1
        troopInput.value = 0;
        setTimeout(() => {
            troopInput.value = 1;
            troopValue.textContent = 1;
            // Reset slider background to position 0%
            troopInput.style.background = `linear-gradient(to right, rgb(34, 211, 238) 0%, rgb(34, 211, 238) 0%, rgb(51, 65, 85) 0%, rgb(51, 65, 85) 100%)`;
        }, 0);

        // Remove old event listeners to prevent duplicates
        troopInput.removeEventListener("input", troopInput.inputHandler);

        // Create new event handler
        troopInput.inputHandler = function() {
            troopValue.textContent = troopInput.value;
            const percentage = ((troopInput.value - troopInput.min) / (troopInput.max - troopInput.min)) * 100;
            troopInput.style.background = `linear-gradient(to right, rgb(34, 211, 238) 0%, rgb(34, 211, 238) ${percentage}%, rgb(51, 65, 85) ${percentage}%, rgb(51, 65, 85) 100%)`;
        };

        troopInput.addEventListener("input", troopInput.inputHandler);

        curr_slider = '#control_slider';
        curr_slider_val = '#control_value';
  
        $('#control_confirm').off('click').on('click' , function(){
          document.getElementById('control_panel').style.display = 'none';
          document.getElementById('control_mechanism').style.display = 'none';
          socket.emit('send_battle_stats_AS', {'choice': toHighLight, 'amount': troopInput.value});
          toHighLight = [];
          clickables = [];
          $('#proceed_next_stage').show();
        });
        $('#control_cancel').off('click').on('click' , function(){playRefuse();
          document.getElementById('control_panel').style.display = 'none';
          document.getElementById('control_mechanism').style.display = 'none';
          toHighLight = [];
          clickables = [];
          $('#proceed_next_stage').show();
        });
     }
    }
  }
}

// Collusion
socket.on('corrupt_territory', function(data){
  clickables = data.targets;
  toHighLight = [];
});

function corrupt_territory(tid){
  toHighLight = [];
  document.getElementById('control_panel').style.display = 'none';
  toHighLight.push(tid);
  document.getElementById('control_panel').style.display = 'none';
  document.getElementById('control_panel').style.display = 'flex';
  $('#proceed_next_stage').hide();
  $('#control_confirm').off('click').on('click' , function(){
    document.getElementById('control_panel').style.display = 'none';
    socket.emit('send_corrupt_territory', {'choice': toHighLight[0]});
    toHighLight = [];
  });
  $('#control_cancel').off('click').on('click' , function(){playRefuse();
    document.getElementById('control_panel').style.display = 'none';
    $('#proceed_next_stage').show();
    toHighLight = [];
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
    clickables = data.targets;
    minefields_amount = data.limits;
    toHighLight = [];
  });

  function set_minefields(tid){
    if (!clickables.includes(tid)){
      return;
    }
    document.getElementById('control_panel').style.display = 'none';
    toHighLight.push(tid);
    if (toHighLight.length > minefields_amount) {
        toHighLight.shift();
    }
    document.getElementById('control_panel').style.display = 'none';
    document.getElementById('control_panel').style.display = 'flex';
    $('#proceed_next_stage').hide();
    $('#control_confirm').off('click').on('click' , function(){
      document.getElementById('control_panel').style.display = 'none';
      socket.emit('send_minefield_choices', {'choices': toHighLight});
      toHighLight = [];
    });
    $('#control_cancel').off('click').on('click' , function(){playRefuse();
      document.getElementById('control_panel').style.display = 'none';
      $('#proceed_next_stage').show();
      toHighLight = [];
    });
  }

  // set_underground_silo
  socket.on('set_underground_silo', function(data){
    clickables = data.targets;
    toHighLight = [];
  });

  function set_underground_silo(tid){
    if (!clickables.includes(tid)){
      return;
    }
    toHighLight = [];
    document.getElementById('control_panel').style.display = 'none';
    toHighLight.push(tid);
    document.getElementById('control_panel').style.display = 'none';
    document.getElementById('control_panel').style.display = 'flex';
    $('#proceed_next_stage').hide();
    $('#control_confirm').off('click').on('click' , function(){
      document.getElementById('control_panel').style.display = 'none';
      socket.emit('send_silo_location', {'choice': toHighLight[0]});
      toHighLight = [];
    });
    $('#control_cancel').off('click').on('click' , function(){playRefuse();
      document.getElementById('control_panel').style.display = 'none';
      $('#proceed_next_stage').show();
      toHighLight = [];
    });
  }

  // launch from silo
  socket.on('underground_silo_launch', function(data){
    clickables = data.targets;
    US_usages = data.usages;
    toHighLight = [];
  });

  // launching from silo
  function underground_silo_launch(tid){
    if (!clickables.includes(tid)){
      return;
    }
    document.getElementById('control_panel').style.display = 'none';
    toHighLight.push(tid);
    if (toHighLight.length > US_usages) {
        toHighLight.shift();
    }
    document.getElementById('control_panel').style.display = 'none';
    document.getElementById('control_panel').style.display = 'flex';
    $('#proceed_next_stage').hide();
    $('#control_confirm').off('click').on('click' , function(){
      document.getElementById('control_panel').style.display = 'none';
      socket.emit('send_missile_targets', {'choices': toHighLight});
      toHighLight = [];
    });
    $('#control_cancel').off('click').on('click' , function(){playRefuse();
      document.getElementById('control_panel').style.display = 'none';
      $('#proceed_next_stage').show();
      toHighLight = [];
    });
  }

  // orbital strike
  socket.on('launch_orbital_strike_offturn', function(data){
    clickables = data.targets;
    US_usages = data.usages;
    toHighLight = [];
  });

  // orbital strike
  function launch_orbital_strike_offturn(tid){
    if (!clickables.includes(tid)){
      return;
    }
    document.getElementById('control_panel').style.display = 'none';
    toHighLight.push(tid);
    if (toHighLight.length > US_usages) {
        toHighLight.shift();
    }
    document.getElementById('control_panel').style.display = 'none';
    document.getElementById('control_panel').style.display = 'flex';
    $('#proceed_next_stage').hide();
    $('#control_confirm').off('click').on('click' , function(){
      document.getElementById('control_panel').style.display = 'none';
      socket.emit('send_orbital_targets', {'choices': toHighLight});
      toHighLight = [];
    });
    $('#control_cancel').off('click').on('click' , function(){playRefuse();
      document.getElementById('control_panel').style.display = 'none';
      $('#proceed_next_stage').show();
      toHighLight = [];
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
                $('#control_cancel').off('click').on('click', function(){playRefuse();
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

// laplace
socket.on('gather_intel', function(data) {

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
              document.getElementById('control_panel').style.display = 'none';
              document.getElementById('control_panel').style.display = 'flex';
              $('#proceed_next_stage').hide();

              // Confirm button action
              $('#control_confirm').off('click').on('click', function(){
                  document.getElementById('control_panel').style.display = 'none';
                  socket.emit('send_gather_target', {'choice': name});

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
              $('#control_cancel').off('click').on('click', function(){playRefuse();
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
    $('#control_panel').hide();
    $('#control_mechanism').hide();
    clickables = []
    toHighLight = []
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
        displayScaleFactor *= 0.9; // You can adjust the zoom speed by changing the multiplier
      } else {
        // Zoom in (increase scale factor)
        displayScaleFactor *= 1.1; // You can adjust the zoom speed by changing the multiplier
      }
      // Limit the scale factor to prevent zooming too far in or out
      displayScaleFactor = constrain(displayScaleFactor, 0.3, 3); // Adjust the range as needed
    }
  }

// touch pad zoom in and out
let lastTouchDist = null;

function touchMoved() {
  // Only consider pinch gesture if there are two or more touches
  if (touches.length >= 2) {
    let d = dist(touches[0].x, touches[0].y, touches[1].x, touches[1].y);

    if (lastTouchDist !== null) {
      let zoomChange = d - lastTouchDist;

      if (abs(zoomChange) > 1) { // threshold to ignore tiny finger jitters
        if (zoomChange > 0) {
          // Zoom in
          displayScaleFactor *= 1.05;
        } else {
          // Zoom out
          displayScaleFactor *= 0.95;
        }

        // Clamp zoom level
        displayScaleFactor = constrain(displayScaleFactor, 0.4, 3);
      }
    }

    lastTouchDist = d;
  }

  return false; // prevent default scrolling
}

function touchEnded() {
  // Reset distance when touches end
  lastTouchDist = null;
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

  // if (mouseButton === LEFT && hover_over.id != null){
  //   explodeAtTerritory(hover_over.id, { power: 300, sparks: 60, smoke: 20, withRing: true });
  //   addShake(12, 250);
  //   triggerFlash(200, 120);
  // } 
  // else 
  //   if (mouseButton === LEFT && hover_over.id != null){
  //   const c = territories[hover_over.id].cps;
  //   spawnMegaNuke(width/2 - offsetX, height/2 - offsetY);
  //   //spawnLineBlast(0,0,width/2,height/2);
  // }
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
        playTap();
        currEvent(tid);
      } 
    }
  }
}

  // TO BE UPDATED
function keyPressed(){
  if (key === 'c'){
    displayScaleFactor = 1.0;
  }

  // shortcut for fast max deployment
  if (key === 'a'){
    if (curr_slider && curr_slider_val) {

      let $slider = $(curr_slider);
      let $sliderValue = $(curr_slider_val);

      $slider.val($slider.attr('max'));
      $sliderValue.text($slider.attr('max'));

      let slider = document.getElementById('control_slider');
      const percentage = (($slider.attr('max') - slider.min) / (slider.max - slider.min)) * 100;
      slider.style.background = `linear-gradient(to right, rgb(34, 211, 238) 0%, rgb(34, 211, 238) ${percentage}%, rgb(51, 65, 85) ${percentage}%, rgb(51, 65, 85) 100%)`;
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

      let slider = document.getElementById('control_slider');
      const percentage = ((halfMax - slider.min) / (slider.max - slider.min)) * 100;
      slider.style.background = `linear-gradient(to right, rgb(34, 211, 238) 0%, rgb(34, 211, 238) ${percentage}%, rgb(51, 65, 85) ${percentage}%, rgb(51, 65, 85) 100%)`;
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

      let slider = document.getElementById('control_slider');
      const percentage = ((thirdMax - slider.min) / (slider.max - slider.min)) * 100;
      slider.style.background = `linear-gradient(to right, rgb(34, 211, 238) 0%, rgb(34, 211, 238) ${percentage}%, rgb(51, 65, 85) ${percentage}%, rgb(51, 65, 85) 100%)`;
    }
  }

}