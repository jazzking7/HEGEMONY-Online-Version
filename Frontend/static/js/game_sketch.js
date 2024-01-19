// Display Settings
let scaleFactor = 1.0; 

let offsetX = 0;
let offsetY = 0;
let isDragging = false;
let previousMouseX;
let previousMouseY;

// Speed up clicks
let tmp_id;
let hover_over = {'id': 0, 'pts': {}};

// images
let capitalImage;
let cityImage;
let insigImage;

// tmp
let colors = [
  "#A20D1E",
  "#0074D9",
  "#00305A",
  "#F06060",
  "#F2EBBF",
  "#F3B562",];

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

function setup() {
  // var canvas = createCanvas(1000, 800);
  var canvas = createCanvas(windowWidth, windowHeight);
  currWinWid = windowWidth;
  currWinHeight = windowHeight;
  canvas.parent('canvasContainer');
  console.log("REACHED")
  capitalImage = loadImage('/static/Assets/Capital/CAD3.PNG');
  cityImage = loadImage('/static/Assets/Dev/city.png');
  insigImage = loadImage('/static/Assets/Insig/fort.PNG');
  loadMapComponents(game_settings.map)
}

async function loadMapComponents(mapName){

  await fetch(`/static/MAPS/${mapName}/properties.json`)
  .then((res) => res.json())
  .then((data) => {mapProperties = data;}).catch(e => console.error(e));

  for (let i = 1; i < mapProperties.numConts+1; i++){
    let tnames = [];
    let tneighbors = [];
    let sr_per_trty;
    let polygons = [];
    let srs = [];
    let cps = [];
    let nameSpaces = [];
    let troopSpaces = [];
    let capitalSpaces = [];
    let devSpaces = [];
    let insigSpaces = [];
    // Names and properties
    await fetch(`/static/MAPS/${mapName}/C${i}/properties.json`)
    .then((res) => res.json())
    .then((data) => {sr_per_trty = data.numSrp;}).catch(e => console.error(e));
    await fetch(`/static/MAPS/${mapName}/C${i}/c${i}tnames.txt`)
      .then((res) => res.text())
      .then((text) => {tnames = text.split(/\r?\n/).filter(n => n);}).catch((e) => console.error(e));
    await fetch(`/static/MAPS/${mapName}/C${i}/c${i}nt.txt`)
      .then((res) => res.text())
      .then((text) => {tneighbors = text.split(/\r?\n/).map(line => line.split(',')).filter(names => names.length > 0 && names[0].length > 0);})
      .catch((e) => console.error(e));
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
    for (let i = 0; i < tnames.length; i++){
      let srcs = [];
      for (let j = 0; j < sr_per_trty; j++){srcs.push(srs[sr_per_trty*i+j]);}
      territories.push(
        {
          "name": tnames[i],
          "neighbors": tneighbors[i], 
          "outline": polygons[i],
          "srcs": srcs,
          "cps": cps[i],
          "ns": nameSpaces[i],
          "ts": troopSpaces[i],
          "cs": capitalSpaces[i],
          "ds": devSpaces[i],
          "is": insigSpaces[i],
          "troops": 1000,
          "color": random(colors),
          "isCapital": true,
          "devImg": cityImage,
          "insig": insigImage
        }
      );
    }
  }
  loadJSON(`/static/MAPS/${mapName}/seaRoutes.json`, (data)=>{for(let sr of data){seaRoutes.push(sr);}});
  loadJSON(`/static/MAPS/${mapName}/contBorders.json`, (data)=>{for(let border of data){contBorders.push(border);}});
  loadJSON(`/static/MAPS/${mapName}/contBonusDisplay.json`, (data)=>{for(let display of data){contBonusBoxes.push(display);}});
}

function draw() {
  if (currWinHeight != windowHeight || currWinWid != windowWidth){
    resizeCanvas(windowWidth, windowHeight);
    currWinWid = windowWidth;
    currWinHeight = windowHeight;
  }
  // clear the background
  background(0, 150, 200);
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
    push();
    fill(trty.color)
    // update hover_over
    if(isMouseInsidePolygon(mouseX, mouseY, trty.outline))
    {
      fill(setShadowColor(trty.color));
      hover_over.id = tmp_id;
      hover_over.pts = trty.outline
    } 
    // Display territory outline
    beginShape();
    for (let p of trty.outline) {
      vertex(p.x, p.y);
    }
    endShape(CLOSE);
    pop();
    tmp_id++;

    // Display sea route coordinates
    for (let src of trty.srcs){
      push();
      fill(0,200,100);
      ellipse(src.x, src.y, 10, 10)
      pop();
    }

    // Display name
    push();
    fill(0); 
    textStyle(BOLD);
    textFont("Helvetica");
    text(trty.name, trty.ns.x, trty.ns.y);
    pop();
    
    // Display troop number
    push();
    fill(0); 
    textStyle(BOLD);
    textSize(15);
    textFont("Helvetica");
    text(trty.troops, trty.ts.x, trty.ts.y);
    pop();

    // Display capital
    if (trty.isCapital){
      push();
      drawStar(trty.cs.dx, trty.cs.dy, trty.cs.x, trty.cs.y, trty.color)
      pop();
    }

    // Display dev
    if (trty.devImg){
      push();
      image(cityImage, trty.ds.x, trty.ds.y, trty.ds.dx, trty.ds.dy)
      pop();
    }

    // Display insig
    if (trty.insig){
      push();
      image(trty.insig, trty.is.x, trty.is.y, trty.is.dx, trty.is.dy);
      pop();
    }

  }

  for (let route of seaRoutes){
    drawDottedLine(route.x1, route.y1, route.x2, route.y2);
  }

  if(showContBorders){
    for (let border of contBorders){
      push();
      fill(128,128,128,100);
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
      textSize(15);
      textAlign(CENTER, CENTER);
      text(bonus.message, bonus.cx, bonus.cy);
      pop();
    }
  }

  // Offset dragging
  translate(-offsetX, -offsetY);
  pop();
  
}

// Shadowy color
function setShadowColor(hexcode){
  let c = color(hexcode)
  c.setAlpha(100)
  return c
}

// TO BE UPDATED
function keyPressed(){
  if (key === 'c'){
    scaleFactor = 1.0;
  }
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

  push();
  fill(scolor);
  translate(centerX, centerY);
  rotate(-PI / 2); // Rotate the star to point upward

  beginShape();
  strokeWeight(3);
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
