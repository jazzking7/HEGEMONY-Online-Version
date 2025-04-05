// Display Settings
let scaleFactor = 1.0; 

let offsetX = 0;
let offsetY = 0;
let isDragging = false;
let previousMouseX;
let previousMouseY;

// Speed up clicks
let tmp_id;
let hover_over = {'id': 0, 'pts': {}, 'name': null};

// images
let capitalImage;
let cityImage;
let insigImage;

// Components to be displayed
let territories = [];
let mapProperties;

let seaRoutes = [];
let contBorders = [];
let contBonusBoxes = [];

// canvas size
let currWinWid;
let currWinHeight;

// Toggles
let showContBorders = false;

// Highlight
let toHightlight = [];
let clickables = [];
let targetsToCapture = [];

// Other player action
let otherHighlight = [];

let ani_offset = 0;
let ani_direction = 1;

// battle casualties display
let dis_cas = false;
let cas_count = 60;
let casualties = [];
// troop addition display
let dis_add = false;
let add_count = 60;
let additions = [];

// Brightness
let dark = false;
let r;
let b;
let g;
let brightness;

function preload() {
  urbanistFont = loadFont('/static/Fonts/Urbanist-SemiBold.ttf');
  console.log("LOADED FONTS");
}

function setup() {
  var canvas = createCanvas(windowWidth, windowHeight);
  currWinWid = windowWidth;
  currWinHeight = windowHeight;
  canvas.parent('canvasContainer');
  capitalImage = loadImage('/static/Assets/Capital/CAD3.PNG');
  cityImage = loadImage('/static/Assets/Dev/city.png');
  radioImage = loadImage('/static/Assets/Insig/radio.png');
  insigImage = loadImage('/static/Assets/Insig/fort.png');
  backgroundOceanImage = loadImage('/static/Assets/Background/gameBackground1.png', img => {
    backgroundOceanImage.resize(currWinWid, currWinHeight);
  });
  console.log('LOADED IMAGES');
  sketch_running = true;
  loadMapComponents(game_settings.map, game_settings.tnames, game_settings.tneighbors, game_settings.landlocked)
}

async function loadMapComponents(mapName, tnames, tneighbors, landlocked){
  await fetch(`/static/MAPS/${mapName}/properties.json`)
  .then((res) => res.json())
  .then((data) => {mapProperties = data;}).catch(e => console.error(e));
  let t_index = 0; // index of territory -> need to make sure that all territory is loaded according to continent order
  for (let i = 1; i < mapProperties.numConts+1; i++){
    let sr_per_trty;
    let numt;
    let polygons = [];
    let srs = [];
    let cps = [];
    let nameSpaces = [];
    let troopSpaces = [];
    let capitalSpaces = [];
    let devSpaces = [];
    let insigSpaces = [];
    let sea_side_counter = 0;
    // properties.json
    await fetch(`/static/MAPS/${mapName}/C${i}/properties.json`)
    .then((res) => res.json())
    .then((data) => {sr_per_trty = data.numSrp; numt = data.numt}).catch(e => console.error(e));
    // Territory outlines, Center points, sea route coordinates
    await fetch(`/static/MAPS/${mapName}/C${i}/c${i}a.json`)
      .then((res) => res.json())
      .then((data) => {for(let trty of data){polygons.push([...trty])}}).catch(e => console.error(e));
    await fetch(`/static/MAPS/${mapName}/C${i}/c${i}sr.json`)
      .then((res) => res.json())
      .then((data) => {for(let sr of data){srs.push(sr)}}).catch(e => console.error(e));
    await fetch(`/static/MAPS/${mapName}/C${i}/c${i}cp.json`)
      .then((res) => res.json())
      .then((data) => {for(let cp of data){cps.push(cp)}}).catch(e => console.error(e));
    // Display sections
    await fetch(`/static/MAPS/${mapName}/C${i}/displaySections/c${i}ns.json`)
      .then((res) => res.json())
      .then((data) => {for(let ns of data){nameSpaces.push(ns)}}).catch(e => console.error(e));  
    await fetch(`/static/MAPS/${mapName}/C${i}/displaySections/c${i}ts.json`)
      .then((res) => res.json())
      .then((data) => {for(let ts of data){troopSpaces.push(ts)}}).catch(e => console.error(e));  
    await fetch(`/static/MAPS/${mapName}/C${i}/displaySections/c${i}cs.json`)
      .then((res) => res.json())
      .then((data) => {for(let cs of data){capitalSpaces.push(cs)}}).catch(e => console.error(e));  
    await fetch(`/static/MAPS/${mapName}/C${i}/displaySections/c${i}ds.json`)
      .then((res) => res.json())
      .then((data) => {for(let ds of data){devSpaces.push(ds)}}).catch(e => console.error(e));  
    await fetch(`/static/MAPS/${mapName}/C${i}/displaySections/c${i}is.json`)
      .then((res) => res.json())
      .then((data) => {for(let is of data){insigSpaces.push(is)}}).catch(e => console.error(e)); 
    for (let i = 0; i < numt; i++){
      let srcs = [];
      if (!(landlocked.includes(tnames[t_index]) ) ){
        for (let j = 0; j < sr_per_trty; j++){srcs.push(srs[sr_per_trty*sea_side_counter+j]);}
        sea_side_counter += 1;
      }
      territories.push({
          "name": tnames[t_index],
          "neighbors": tneighbors[t_index], 
          "outline": polygons[i],
          "srcs": srcs,
          "cps": cps[i],
          "ns": nameSpaces[i],
          "ts": troopSpaces[i],
          "cs": capitalSpaces[i],
          "ds": devSpaces[i],
          "is": insigSpaces[i],
          "troops": '',
          "color": "white",
          "capital_color": "white",
          "isCapital": false,
          "devImg": null,
          "insig": null
      });
      //console.log(territories);
      t_index += 1;
    }
  }
  loadJSON(`/static/MAPS/${mapName}/seaRoutes.json`, (data)=>{for(let sr of data){seaRoutes.push(sr);}});
  loadJSON(`/static/MAPS/${mapName}/contBorders.json`, (data)=>{for(let border of data){contBorders.push(border);}});
  loadJSON(`/static/MAPS/${mapName}/contBonusDisplay.json`, (data)=>{for(let display of data){contBonusBoxes.push(display);}});
  console.log("MAP LOADED");
  socket.emit('confirm_map_loaded');
}

function draw() {
  if (currWinHeight != windowHeight || currWinWid != windowWidth){
    resizeCanvas(windowWidth, windowHeight);
    currWinWid = windowWidth;
    currWinHeight = windowHeight;
  }
  // clear the background
  background(0); // Placeholder background color
  backgroundOceanImage.resize(currWinWid, currWinHeight);
  if (backgroundOceanImage) {
    let x = (width - backgroundOceanImage.width) / 2;
    let y = (height - backgroundOceanImage.height) / 2;
    image(backgroundOceanImage, x, y);
  }
  push();
  // Calculate center of canvas
  let canvasCenterX = width / 2;
  let canvasCenterY = height / 2;

  // Apply the scaling factor centered at canvas center
  translate(canvasCenterX, canvasCenterY);
  scale(scaleFactor);
  translate(-canvasCenterX, -canvasCenterY);
  if (isDragging) {
    let dx = mouseX - previousMouseX;
    let dy = mouseY - previousMouseY;
    
    offsetX = constrain(offsetX + dx, -1500, 1500); // Adjust according to canvas size
    offsetY = constrain(offsetY + dy, -1000, 1000); // Adjust according to canvas size
  }
  // Dragging
  translate(offsetX, offsetY);
  
  // Draw elements
  // Draw territories
  tmp_id = 0;
  for (let trty of territories){

    // Extract RGB values and calculate brightness
    r = red(trty.color);
    g = green(trty.color);
    b = blue(trty.color);
    brightness = (0.299 * r) + (0.587 * g) + (0.114 * b);
    dark = brightness < 128;

    push();
    fill(trty.color);
    strokeWeight(1.5);
    // update hover_over
    if(isMouseInsidePolygon(mouseX, mouseY, trty.outline))
    {
      fill(setShadowColor(trty.color));
      hover_over.id = tmp_id;
      hover_over.pts = trty.outline;
    } 
    if (targetsToCapture.includes(tmp_id)){
      stroke("#ffbf00");
      strokeWeight(4);
    }
    if (otherHighlight.includes(tmp_id)){
      stroke("black");
      strokeWeight(4);
    }
    if (toHightlight.includes(tmp_id)){
      stroke("black");
      strokeWeight(4);
    }
    // Display territory outline
    beginShape();
    for (let p of trty.outline) {
      vertex(p.x, p.y);
    }
    endShape(CLOSE);
    pop();

    // Display sea route coordinates
    if (trty.srcs.length){
      for (let src of trty.srcs){
        push();
        fill(0,200,100);
        ellipse(src.x, src.y, 10, 10)
        pop();
      }
    }

    if (scaleFactor < 0.4) {
      push();
      textFont(urbanistFont);
      if (dark) {
        fill(color(245,245,245));
      }
      textSize(35);
      textStyle(BOLD);
      text(trty.troops, trty.cps.x, trty.cps.y);
      pop();
    } else {
      // Display name
      push();
      fill(0);
      if (dark) {
        fill(color(245,245,245));
      }
      textStyle(BOLD);
      textFont(urbanistFont);
      text(trty.name, trty.ns.x, trty.ns.y);
      pop();
      
      // Display troop number
      push();
      fill(0); 
      if (dark) {
        fill(color(245,245,245));
      }
      textStyle(BOLD);
      textSize(16);
      textFont(urbanistFont);
      text(trty.troops, trty.ts.x, trty.ts.y);
      pop();

      // Display capital
      if (trty.isCapital){
        push();
        drawStar(trty.cs.dx, trty.cs.dy, trty.cs.x, trty.cs.y, trty.capital_color)
        pop();
      }

      // Display dev
      if (trty.devImg){
        push();
        image(cityImage, trty.ds.x, trty.ds.y, trty.ds.dx, trty.ds.dy)
        pop();
      }

      // Display insig  or  special display
      if (trty.insig){
        push();   
        image(trty.insig, trty.is.x, trty.is.y, trty.is.dx, trty.is.dy);
        pop();
      }
    }

    // clickable animation
    if (clickables.includes(tmp_id)){
      drawEquiTriangle(trty.cps.x, trty.cps.y+ani_offset);
    }
    tmp_id++;
  }
  // outside for loop

  // casualties display
  if (casualties.length > 0){
    for (cas of casualties) {
      if (cas_count > 0) {
        if (cas.number > 0) {
          push();
          stroke(255); // Dark red color
          strokeWeight(1); 
          fill(139, 0, 0);
          textFont(urbanistFont);
          textSize(35);
          textStyle(BOLD);
          text("-" + cas.number, territories[cas.tid].cps.x, territories[cas.tid].cps.y);
          pop();
        }
      } 
    }
  }

  // additions display
  if (additions.length > 0){
    for (adding of additions) {
      if (add_count > 0) {
        if (adding.number > 0) {
          push();
          stroke(255);
          strokeWeight(1); 
          fill(39, 165, 103);
          textFont(urbanistFont);
          textSize(35);
          textStyle(BOLD);
          text("+" + adding.number, territories[adding.tid].cps.x, territories[adding.tid].cps.y);
          pop();
        }
      } 
    }
  }
  

  for (let route of seaRoutes){
    drawDottedLine(route.x1, route.y1, route.x2, route.y2);
  }

  if(showContBorders){
    for (let border of contBorders){
      push();
      fill(128,128,128,100);
      strokeWeight(4)
      beginShape();
      for (let p of border){
        vertex(p.x, p.y);
      }
      endShape(CLOSE);
      pop();
    }
    
    for (let bonus of contBonusBoxes){
      push();
      fill(255,255,255);
      rect(bonus.x, bonus.y, bonus.dx, bonus.dy);
      fill(0,0,0);
      textStyle(BOLD);
      textFont(urbanistFont);
      textSize(15);
      textAlign(CENTER, CENTER);
      text(bonus.message, bonus.cx, bonus.cy);
      pop();
    }
  }

  // Offset dragging
  translate(-offsetX, -offsetY);
  pop();
  ani_offset += ani_direction;
  if (ani_offset == 30 || ani_offset == 0){
    ani_direction *= -1;
  }

  // casualty display counter
  if (dis_cas) {
    cas_count--;
    if (cas_count == 0) {
      dis_cas = false;
      casualties = [];
    }
  }
  
  // addition display counter
  if (dis_add){
    add_count--;
    if (add_count == 0){
      dis_add = false;
      additions = [];
    }
  }

}

// Shadowy color
function setShadowColor(hexcode){
  let c = color(hexcode)
  c.setAlpha(100)
  return c
}

// Function to check if a point is inside a polygon
function pointInPolygon(P, vertices) {
  let x = P.x, y = P.y;
  let inside = false;
  for (let i = 0, j = vertices.length - 1; i < vertices.length; j = i++) {
    let xi = vertices[i].x,
      yi = vertices[i].y;
    let xj = vertices[j].x,
      yj = vertices[j].y;
    let intersect =
      yi > y != yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi;
    if (intersect) inside = !inside;
  }
  return inside;
}

function isMouseInsidePolygon(mouseX, mouseY, polygon) {
  let resetX = mouseX - offsetX*scaleFactor;
  let resetY = mouseY - offsetY*scaleFactor;
  let translatedX = resetX - width/2;
  let translatedY = resetY - height/2;
  let scaledX = translatedX / scaleFactor;
  let scaledY = translatedY / scaleFactor;
  let finalX = scaledX + width/2;
  let finalY = scaledY + height/2;

  // Return true if inside, false otherwise
  return pointInPolygon(createVector(finalX, finalY), polygon);
}

// draw sea routes
function drawDottedLine(x1, y1, x2, y2){
  push();
  stroke(0); 
  strokeWeight(5); 
  let lineLength = dist(x1, y1, x2, y2);
  let dotSpacing = 6;
  for (let i = 0; i <= lineLength; i += dotSpacing * 2) {
    let x = map(i, 0, lineLength, x1, x2);
    let y = map(i, 0, lineLength, y1, y2);
    point(x, y);
  }
  pop();
}

// draw capitals
function drawStar(dimX, dimY, x, y, scolor) {
  let centerX = x + dimX / 2;
  let centerY = y + dimY / 2;

  let starSize = min(dimX, dimY) * 0.8; // Adjust the star size based on the smaller dimension
  let outerRadius = starSize / 2;
  let innerRadius = starSize / 4;
  let numPoints = 5;

  let r = red(scolor);
  let g = green(scolor);
  let b = blue(scolor);
  let luminance = (0.299 * r + 0.587 * g + 0.114 * b);

  push();
  fill(scolor);

  if (luminance < 100) {
    stroke(245, 245, 245); 
  } else {
    stroke(0); 
  }

  translate(centerX, centerY);
  rotate(-PI / 2); 

  beginShape();
  strokeWeight(2);
  let angle = TWO_PI / numPoints;
  for (let a = 0; a < TWO_PI; a += angle) {
    let sx = cos(a) * outerRadius;
    let sy = sin(a) * outerRadius;
    vertex(sx, sy);

    let sa = a + angle / 2;
    let mx = cos(sa) * innerRadius;
    let my = sin(sa) * innerRadius;
    vertex(mx, my);
  }
  endShape(CLOSE);
  pop();
}

// 20 side length equilateral triangle
function drawEquiTriangle(x, y) {

  let x1 = x - 10;
  let y1 = y - 17.3205; // Invert the y-coordinate

  let x2 = x + 10;
  let y2 = y - 17.3205; // Invert the y-coordinate

  let x3 = x;
  let y3 = y; 
  
  push();
  fill(255, 0, 0); // Sets the fill color (in this case, a shade of blue)
  strokeWeight(2)
  triangle(x1, y1, x2, y2, x3, y3);
  pop();
}