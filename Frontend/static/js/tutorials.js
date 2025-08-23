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
  game_settings = await get_tutorial_settings();

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
  
  function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async function tryLoadSketch() {
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
    if (progress <= 0) {
      clearInterval(current_interval);
      timeoutBar.set(0);
    }
  }, 1000); // Update the progress bar every second
}

// Function to load game settings
async function get_tutorial_settings() {
    try {
      const gameSettings = await new Promise((resolve) => {
        socket.emit('get_tutorial_settings');
        socket.once('tutorial_settings', (settings) => {
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

socket.on('send_tutorial_welcome', function () {
  const announ = document.getElementById('announcement');
  announ.innerHTML = `<h2>Welcome to Hegemony!</h2>`;

  setTimeout(() => {
    $('#middle_display, #middle_title, #middle_content').show();
    $('#middle_content').html(`
      <div style="padding: 8px; line-height: 1.5; font-size: 1.1rem;">
        <p>Welcome to the <strong>Hegemony Tutorial</strong></p>
        <p>Here, you'll be introduced to the essentials:</p>
        <ul style="margin: 5px 0; padding-left: 22px;">
          <li><strong>Game Goal</strong></li>
          <li><strong>Game Setup</strong></li>
          <li><strong>Basic Gameplay</strong></li>
        </ul>
      </div>
    `);
    $('#proceed_next_stage').show();
    $('#proceed_next_stage .text').text('Next');
    $('#proceed_next_stage')
      .off('click')
      .on('click', () => {
        $('#proceed_next_stage').hide();
        socket.emit("next_tutorial_stage", {'stage': 1});
      });
  }, 5000);
});

socket.on('show_game_goal', function () {
  const announ = document.getElementById('announcement');
  announ.innerHTML = `<h2>Game Goal</h2>`;

  $('#middle_display, #middle_title, #middle_content').show();
  $('#middle_content').html(`
    <div style="padding: 10px; line-height: 1.6; font-size: 1.1rem;">
      <p><strong>The Goal of the Game</strong></p>
      <p>
        Your ultimate objective is to complete your <strong>Secret Agenda</strong>.
        No one else knows what yours is, and it may even conflict with another player’s!
      </p>
      <p>
        Secret Agendas come in four classes:
        <strong>C, B, A,</strong> and <strong>S</strong>.
        Class <strong>C</strong> is the most peaceful, while the higher classes grow increasingly
        <em>violent</em> and <em>self-serving</em>.
      </p>
      <p>
        Only players with Agendas from the <strong>same class</strong> can possibly share victory.
        Will you form alliances, or aim to be a <em>covert solo winner</em>?
      </p>
    </div>
  `);

  $('#proceed_next_stage').show();
  $('#proceed_next_stage .text').text('Next');
  $('#proceed_next_stage')
    .off('click')
    .on('click', () => {
      $('#proceed_next_stage').hide();
      socket.emit("next_tutorial_stage", {'stage': 2});
    });

});

socket.on('show_secret_agenda', function () {
  const announ = document.getElementById('announcement');
  announ.innerHTML = `<h2>Game Goal</h2>`;

  $('#middle_display, #middle_title, #middle_content').show();
  $('#middle_content').html(`
    <div style="padding: 10px; line-height: 1.6; font-size: 1.1rem;">
      <p>
        For the purpose of this tutorial, your <strong>Secret Agenda</strong> is set to a C class agenda 
        <em>Populist</em>. To win, you must maintain the <strong>largest army</strong>
        for <strong>4 consecutive rounds</strong>.
      </p>
      <p>
        Your mission’s <strong>progression, status,</strong> and <strong>details</strong> are shown
        on the <strong>Mission Tracker</strong> located in the top-right corner.
        This is your only way of monitoring mission progress — keep an eye on it!
      </p>
    </div>
  `);

  $('#proceed_next_stage').show();
  $('#proceed_next_stage .text').text('Next');
  $('#proceed_next_stage')
    .off('click')
    .on('click', () => {
      $('#proceed_next_stage').hide();
      socket.emit("next_tutorial_stage", {'stage': 3});
    });

});

socket.on('show_game_set_up', function () {
  const announ = document.getElementById('announcement');
  announ.innerHTML = `<h2>Game Set Up</h2>`;

  $('#middle_display, #middle_title, #middle_content').show();
  $('#middle_content').html(`
    <div style="padding: 10px; line-height: 1.6; font-size: 1.1rem;">
      <p><strong>Before the Game Begins</strong></p>
      <p>Each player must complete the following steps:</p>
      <ul style="margin: 6px 0; padding-left: 22px;">
        <li>Select a <strong>color</strong> to represent themselves</li>
        <li>Claim a set of <strong>territories</strong></li>
        <li>Designate a <strong>capital</strong></li>
        <li>Build <strong>two cities</strong></li>
        <li>Pick a <strong>War Art</strong></li>
        <li>Deploy initial <strong>troops</strong></li>
      </ul>
    </div>
  `);


  $('#proceed_next_stage').show();
  $('#proceed_next_stage .text').text('Next');
  $('#proceed_next_stage')
    .off('click')
    .on('click', () => {
      $('#proceed_next_stage').hide();
      socket.emit("next_tutorial_stage", {'stage': 4});
    });

});

socket.on('pick_color', function () {
  const announ = document.getElementById('announcement');
  announ.innerHTML = `<h2>Game Setup</h2>`;

  $('#middle_display, #middle_title, #middle_content').show();

  // Reworded title
  $('#middle_title').html(`
    <h4>
      Choose your color. For this tutorial, you're locked to <strong>Royal Blue</strong>.
      Click <em>Confirm</em> to continue.
    </h4>
  `);

  // Only these two colors; selection locked to #4169E1
  const options = ["#4169E1", "#FFDE21"];
  const lockedColor = "#4169E1";

  const colorBoard = $('#middle_content');
  colorBoard.empty();

  for (let option of options) {
    const btn_c = document.createElement("button");
    btn_c.className = 'btn';
    btn_c.style.width = '2vw';
    btn_c.style.height = '2vw';
    btn_c.style.backgroundColor = option;
    btn_c.style.border = 'none';
    btn_c.style.margin = '1px';

    if (option === lockedColor) {
      // Visually indicate the locked selection
      btn_c.style.border = '2px solid';
      btn_c.style.borderColor = 'red';
      btn_c.title = 'Selected (locked for tutorial)';
    } else {
      // Disable the other color entirely
      btn_c.disabled = true;
      btn_c.style.opacity = '0.5';
      btn_c.style.cursor = 'not-allowed';
      btn_c.title = 'Locked for tutorial';
    }

    // Prevent changing selection
    btn_c.onclick = function () { return false; };

    colorBoard.append(btn_c);
  }

  // Show the control panel so the user can confirm right away
  const panel = document.getElementById('control_panel');
  panel.style.display = 'flex';

  $('#control_confirm').off('click').on('click', function () {
    panel.style.display = 'none';
    $('#middle_title').empty();
    // Proceed to next stage; color is locked so no need to pass it unless your backend expects it
    socket.emit("next_tutorial_stage", { 'stage': 5 });
  });

  $('#control_cancel').off('click').on('click', function () {
    // Just hide panel; selection remains locked
    panel.style.display = 'none';
  });
});

socket.on('claim_territories', function () {
  const announ = document.getElementById('announcement');
  announ.innerHTML = `<h2>Game Setup</h2>`;

  $('#middle_display, #middle_title, #middle_content').show();

  // Reworded title + mechanic note
  $('#middle_title').html(`
    <h5>
      Claim a set of territories. For this tutorial, you're locked to
      <strong>Teal</strong>. Once you choose a color, <strong>all territories with that color
      become yours</strong> and will be <strong>recolored to your chosen color</strong>. Click
      <em>Confirm</em> to continue.
    </h5>
  `);

  // Only these two colors; selection locked to #3B8686
  const options = ["#3B8686", "#CFF09E"];
  const lockedColor = "#3B8686";

  const colorBoard = $('#middle_content');
  colorBoard.empty();

  for (let option of options) {
    const btn_c = document.createElement("button");
    btn_c.className = 'btn';
    btn_c.style.width = '2vw';
    btn_c.style.height = '2vw';
    btn_c.style.backgroundColor = option;
    btn_c.style.border = 'none';
    btn_c.style.margin = '1px';

    if (option === lockedColor) {
      // Visually indicate the locked selection
      btn_c.style.border = '2px solid';
      btn_c.style.borderColor = 'red';
      btn_c.title = 'Selected (locked for tutorial)';
    } else {
      // Disable the other color entirely
      btn_c.disabled = true;
      btn_c.style.opacity = '0.5';
      btn_c.style.cursor = 'not-allowed';
      btn_c.title = 'Locked for tutorial';
    }

    // Prevent changing selection
    btn_c.onclick = function () { return false; };

    colorBoard.append(btn_c);
  }

  // Show control panel so the user can confirm right away
  const panel = document.getElementById('control_panel');
  panel.style.display = 'flex';

  $('#control_confirm').off('click').on('click', function () {
    panel.style.display = 'none';
    $('#middle_title').empty();
    socket.emit("next_tutorial_stage", { stage: 6});
  });

  $('#control_cancel').off('click').on('click', function () {
    panel.style.display = 'none';
  });
});


socket.on('choose_capital_tutorial', function () {
  const announ = document.getElementById('announcement');
  announ.innerHTML = `<h2>Game Setup</h2>`;

  $('#middle_display, #middle_title, #middle_content').show();
  $('#middle_content').html(`
    <div style="padding: 10px; line-height: 1.6; font-size: 1.1rem;">
      <p><strong>Designate Your Capital</strong></p>
      <p>Select one of your <strong>own territories</strong> and click <strong>Confirm</strong> to set it as your capital.</p>
      <p>Your capital gives <strong>+1 troop</strong> at the start of every turn.</p>
      <p>For this tutorial, simply click the <strong>pointed territory</strong> and then press <em>Confirm</em> to proceed.</p>
    </div>
  `);
  clickables.push(7);
});

// Set capital
function settle_capital(tid){
  if (tid == 7){
    toHightlight = [7];
    document.getElementById('control_panel').style.display = 'flex';
    $('#control_confirm').off('click').on('click', function(){
      document.getElementById('control_panel').style.display = 'none';
      socket.emit("next_tutorial_stage", { stage: 7});
      toHightlight = [];
      clickables = [];
    });
    $('#control_cancel').off('click').on('click' , function(){
    });
  }
}

socket.on('choose_city_tutorial', function () {
  const announ = document.getElementById('announcement');
  announ.innerHTML = `<h2>Game Setup</h2>`;

  $('#middle_display, #middle_title, #middle_content').show();
  $('#middle_content').html(`
    <div style="padding: 10px; line-height: 1.6; font-size: 1.1rem;">
      <p><strong>Build Your Cities</strong></p>
      <p>
        Choose <strong>two of your territories</strong> to designate as <strong>Cities</strong>.
      </p>
      <p>
        Cities provide <strong>extra troops each turn</strong> and boost your battle stats.
      </p>
      <p>
        For this tutorial, simply click on the <strong>pointed territories</strong> and then press
        <em>Confirm</em> to continue.
      </p>
    </div>
  `);

  clickables.push(8);
  clickables.push(9);
});

// Set cities
function settle_cities(tid){
  if(clickables.includes(tid)){
    if (!toHightlight.includes(tid)){
      toHightlight.push(tid);
    }
    if (toHightlight.length == 2){
        document.getElementById('control_panel').style.display = 'none';
        document.getElementById('control_panel').style.display = 'flex';
        $('#control_confirm').off('click').on('click' , function(){
        document.getElementById('control_panel').style.display = 'none';
        socket.emit("next_tutorial_stage", { stage: 8 });
        toHightlight = [];
        clickables = [];
        });
        $('#control_cancel').off('click').on('click' , function(){
        }); 
    }

  }
}

socket.on('initial_deployment_tutorial', function () {
  const announ = document.getElementById('announcement');
  announ.innerHTML = `<h2>Game Setup</h2>`;

  $('#middle_display, #middle_title, #middle_content').show();
  $('#middle_content').html(`
    <div style="padding: 10px; line-height: 1.6; font-size: 1.1rem;">
      <p><strong>Initial Deployment</strong></p>
      <p>
        In this phase, the system gives you troops to <strong>reinforce key territories</strong>.
      </p>
      <p>
        For this tutorial, you receive <strong>30 troops</strong>. Click the <strong>pointed territory</strong>
        and deploy them all, then press <em>Confirm</em>.
      </p>
    </div>
  `);


  clickables.push(7);
});

function troop_deployment(tid){
  if(clickables.includes(tid)){
    if (!toHightlight.includes(tid)){
      toHightlight.push(tid);
    }


  }
}


socket.on('initiate_tracker_for_tutorial', function(data){
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

// Start timer animation
socket.on('start_timeout', function(data){
  startTimeout(data.secs);
});

// Stop timer animation
socket.on('stop_timeout', function(){
  clearInterval(current_interval);
});


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

// hide the display if clicked outside
$(document).on('click', function(event) {
  if (!$(event.target).closest('#laplace_info_display').length) {
    $('#laplace_info_display').empty().hide();
  }
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
socket.on('change_click_event_tutorial', function(data){
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
  } else {
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

    document.getElementById('control_mechanism').innerHTML = '';
    document.getElementById('control_panel').style.display = 'none';
    document.getElementById('control_panel').style.display = 'flex';
    $('#proceed_next_stage').hide();
    $('#control_confirm').off('click').on('click' , function(){
      document.getElementById('control_panel').style.display = 'none';
      socket.emit("terminate_conquer_stage");
      currEvent = null;
      toHightlight = [];
      clickables = [];
    });
    $('#control_cancel').off('click').on('click' , function(){
      document.getElementById('control_panel').style.display = 'none';
      $('#proceed_next_stage').show();
    });

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

socket.on('set_forts', function(data){
  city_amt = data.amount;
  announ = document.getElementById('announcement');
  announ.innerHTML = `<h2>Settling new forts, ${data.amount} under construction</h2>`;
  clickables = [];
  toHightlight = [];
  clickables = data.flist;
})

socket.on('set_hall', function(data){
  city_amt = data.amount;
  announ = document.getElementById('announcement');
  announ.innerHTML = `<h2>Intalling Governance Halls, ${data.amount} under construction</h2>`;
  clickables = [];
  toHightlight = [];
  clickables = data.flist;
})

socket.on('set_nexus', function(data){
  city_amt = data.amount;
  announ = document.getElementById('announcement');
  announ.innerHTML = `<h2>Building Logistic Nexus, ${data.amount} under construction</h2>`;
  clickables = [];
  toHightlight = [];
  clickables = data.flist;
})

socket.on('set_leyline', function(data){
  city_amt = data.amount;
  announ = document.getElementById('announcement');
  announ.innerHTML = `<h2>Settling Leyline Cross, ${data.amount} under construction</h2>`;
  clickables = [];
  toHightlight = [];
  clickables = data.flist;
})

socket.on('set_bureau', function(data){
  city_amt = data.amount;
  announ = document.getElementById('announcement');
  announ.innerHTML = `<h2>Settling Mobilization Bureaux, ${data.amount} under construction</h2>`;
  clickables = [];
  toHightlight = [];
  clickables = data.flist;
})

// Set and display the city amount for megacity settlement event
socket.on('raise_megacities', function(data){
  city_amt = data.amount;
  announ = document.getElementById('announcement');
  announ.innerHTML = `<h2>Raising new megacities, ${data.amount} under construction</h2>`;
  clickables = [];
  toHightlight = [];
  clickables = data.clist;
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

function raise_megacities(tid){
  if(clickables.includes(tid) && city_amt >= 1){
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
          socket.emit('settle_megacities', {'choice': toHightlight});
          toHightlight = [];
        });
        $('#control_cancel').off('click').on('click', function(){
          $('#control_panel').hide();
          toHightlight = [];
        });
    }
  }
}

function set_forts(tid){
  if(clickables.includes(tid) && city_amt >= 1){
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
          socket.emit('settle_forts', {'choice': toHightlight});
          toHightlight = [];
        });
        $('#control_cancel').off('click').on('click', function(){
          $('#control_panel').hide();
          toHightlight = [];
        });
    }
  }
}

function set_hall(tid){
  if(clickables.includes(tid) && city_amt >= 1){
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
          socket.emit('settle_hall', {'choice': toHightlight});
          toHightlight = [];
        });
        $('#control_cancel').off('click').on('click', function(){
          $('#control_panel').hide();
          toHightlight = [];
        });
    }
  }
}

function set_nexus(tid){
  if(clickables.includes(tid) && city_amt >= 1){
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
          socket.emit('settle_nexus', {'choice': toHightlight});
          toHightlight = [];
        });
        $('#control_cancel').off('click').on('click', function(){
          $('#control_panel').hide();
          toHightlight = [];
        });
    }
  }
}

function set_leyline(tid){
  if(clickables.includes(tid) && city_amt >= 1){
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
          socket.emit('settle_leyline', {'choice': toHightlight});
          toHightlight = [];
        });
        $('#control_cancel').off('click').on('click', function(){
          $('#control_panel').hide();
          toHightlight = [];
        });
    }
  }
}

function set_bureau(tid){
  if(clickables.includes(tid) && city_amt >= 1){
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
          socket.emit('settle_bureau', {'choice': toHightlight});
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
          <span class="price-tag" style="color: #FFFFFF;">3☆</span>
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
          <span class="price-tag" style="color: #FFFFFF;">3☆</span>
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
          <span class="price-tag" style="color: #000000;">5☆</span>
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
          <span class="price-tag" style="color: #FFFFFF;">5☆</span>
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
          <span class="price-tag" style="color: #000000;">5☆</span>
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
          <span class="price-tag" style="color: #000000;">2☆</span>
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
          <span class="price-tag" style="color: #FFFFFF;">2☆</span>
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
      if (sep_auth < 3){
        popup('MINIMUM 3 STARS TO UPGRADE INFRASTRUCTURE!', 2000);
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
          socket.emit('upgrade_infrastructure', {'amt': $("#amtSlider").val()});
          //Shutting off
          $('#middle_display').hide()
          $('#middle_title, #middle_content').empty();
        });
    });

    // RAISE MEGACITY
    $("#btn-mega").off('click').on('click', function(){
      if (sep_auth < 5){
        popup('MINIMUM 5 STARS TO RAISE MEGACITY!', 2000);
        $("#middle_display").hide()
        $("#middle_title, #middle_content").empty();
        return;
      }
      $("#middle_content").html(
        `<p>Select number of Megacities to raise:</p>
          <input type="range" id="amtSlider" min="1" max=${Math.floor(sep_auth/5)} step="1" value="1">
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
      if (sep_auth < 5){
        popup('MINIMUM 5 STARS TO SET UP HALL!', 2000);
        $("#middle_display").hide()
        $("#middle_title, #middle_content").empty();
        return;
      }
      $("#middle_content").html(
        `<p>Select number of Halls of Governance to set up:</p>
          <input type="range" id="amtSlider" min="1" max=${Math.floor(sep_auth/5)} step="1" value="1">
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
      if (sep_auth < 5){
        popup('MINIMUM 5 STARS TO BUILD A NEXUS!', 2000);
        $("#middle_display").hide()
        $("#middle_title, #middle_content").empty();
        return;
      }
      $("#middle_content").html(
        `<p>Select number of Logistic Nexus:</p>
          <input type="range" id="amtSlider" min="1" max=${Math.floor(sep_auth/5)} step="1" value="1">
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
      if (sep_auth < 2){
        popup('MINIMUM 2 STARS TO BUILD A LEYLINE CROSS!', 2000);
        $("#middle_display").hide()
        $("#middle_title, #middle_content").empty();
        return;
      }
      $("#middle_content").html(
        `<p>Select number of Leyline Cross:</p>
          <input type="range" id="amtSlider" min="1" max=${Math.floor(sep_auth/2)} step="1" value="1">
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

    // Leyline Cross
    $("#btn-bureau").off('click').on('click', function(){
      if (sep_auth < 2){
        popup('MINIMUM 2 STARS TO BUILD A MOBILIZATION BUREAU!', 2000);
        $("#middle_display").hide()
        $("#middle_title, #middle_content").empty();
        return;
      }
      $("#middle_content").html(
        `<p>Select number of bureaus:</p>
          <input type="range" id="amtSlider" min="1" max=${Math.floor(sep_auth/2)} step="1" value="1">
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
    displayScaleFactor = 1.0;
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