// Display Settings
let scaleFactor = 1.0; 

let offsetX = 0;
let offsetY = 0;
let isDragging = false;
let previousMouseX;
let previousMouseY;

// Speed up clicks
let tmp_id = 0;
let hover_over = {'pts': [], 'id': 0};

// images
let capitalImage;
let cityImage;
let insigImage;

// Components to be displayed
let polygons = [];
let srs = [];
let nameSpaces = [];
let capitalSpaces = [];
let devSpaces = [];
let insigSpaces = [];
let territoryNames = [];
let neighborTerritoryNames = {};
let cps = [];
let seaRoutes = [];
let contBorders = [];
let contBonusBoxes = [];

// Toggles
let showContBorders = false;

async function setup() {
  var canvas = createCanvas(1000, 1000);
  canvas.parent('canvasContainer');
  console.log("REACHED")
  capitalImage = loadImage('/static/Assets/Capital/CAD3.PNG');
  cityImage = loadImage('/static/Assets/Dev/city.png');
  insigImage = loadImage('/static/Assets/Insig/insignia27.PNG');
  let tempArray = [];
  for (let i = 1; i < 7; i++){
    loadJSON(`/static/MAPS/MichaelMap1/C${i}/c${i}a.json`, loadPolygonsData);
    loadJSON(`/static/MAPS/MichaelMap1/C${i}/c${i}sr.json`, loadSR);
    loadJSON(`/static/MAPS/MichaelMap1/C${i}/displaySections/c${i}ns.json`, loadNS);
    loadJSON(`/static/MAPS/MichaelMap1/C${i}/displaySections/c${i}cs.json`, loadCS);
    loadJSON(`/static/MAPS/MichaelMap1/C${i}/displaySections/c${i}ds.json`, loadDS);
    loadJSON(`/static/MAPS/MichaelMap1/C${i}/displaySections/c${i}is.json`, loadIS);
    await fetch(`/static/MAPS/MichaelMap1/C${i}/c${i}tnames.txt`)
      .then((res) => res.text())
      .then((text) => {
        territoryNames.push(...text.split(/\r?\n/).filter(n => n));
      }).catch((e) => console.error(e));
    await fetch(`/static/MAPS/MichaelMap1/C${i}/c${i}nt.txt`)
      .then((res) => res.text())
      .then((text) => {
        tempArray.push(...text.split(/\r?\n/).filter(n => n));
      }).catch((e) => console.error(e));
  }
  for (let j = 0; j < territoryNames.length; j++){
    neighborTerritoryNames[territoryNames[j]] = tempArray[j].split(",");
  }
  loadJSON(`/static/MAPS/MichaelMap1/seaRoutes.json`, loadSeaRoutes);
  loadJSON(`/static/MAPS/MichaelMap1/contBorders.json`, loadBorders);
  loadJSON(`/static/MAPS/MichaelMap1/contBonusDisplay.json`, loadContBonus);
}

function draw() {
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
    
    offsetX = constrain(offsetX + dx, -1500, 500); // Adjust according to canvas size
    offsetY = constrain(offsetY + dy, -500, 500); // Adjust according to canvas size
  }
  // Dragging
  translate(offsetX, offsetY);
  
  // Draw elements
  tmp_id = 0;
  for (let polygon of polygons){
    push();
    if(isMouseInsidePolygon(mouseX, mouseY, polygon))
    {
      fill(255,0,0);
     hover_over.pts = polygon;
     hover_over.id = tmp_id;
    }
  beginShape();
  for (let p of polygon) {
    vertex(p.x, p.y);
  }
  endShape(CLOSE);
    pop();
    tmp_id++;
  }

  for (let coord of srs){
    push();
    fill(0,255,0)
    circle(coord.x, coord.y, 10);
    pop();
  }

  let nameIndex = 0
  for (let coord of nameSpaces){
    push();
    text(territoryNames[nameIndex], coord.x, coord.y);
    nameIndex++;
    pop();
  }

  for (let coord of capitalSpaces){
    push();
    image(capitalImage, coord.x, coord.y, coord.dx, coord.dy);
    pop();
  }

  for (let coord of devSpaces){
    push();
    image(cityImage, coord.x, coord.y, coord.dx, coord.dy);
    pop();
  }

  for (let coord of insigSpaces){
    push();
    image(insigImage, coord.x, coord.y, coord.dx, coord.dy);
    pop();
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

  
  push();
  fill(220,0,50)
  rect(25, 25, 80, 50);
  fill(0,0,0)
  textStyle(BOLD);
  text("\t\t\tSHOW\nCONTINENTS", 25, 48);
  showContBorders = (mouseX < 105 && mouseX > 25 && mouseY < 75 && mouseY > 25);

  pop();
  
}

function keyPressed(){
  if (key === 'c'){
    scaleFactor = 1.0;
  }
}

function loadPolygonsData(data){
    for (let p of data) {
    polygons.push([...p]);
  }
}

function loadSR(data){
    for (let p of data) {
    srs.push(p);
  }
}

function loadNS(data){
  for (let p of data) {
    nameSpaces.push(p)
  }
}

function loadCS(data){
  for (let c of data){
    capitalSpaces.push(c);
  }
}

function loadDS(data){
  for (let c of data){
    devSpaces.push(c);
  }
}

function loadIS(data){
  for (let i of data){
    insigSpaces.push(i);
  }
}

function loadCP(data){
    for (let p of data) {
    cps.push(p);
  }
}

function loadBorders(data){
  for (let border of data){
    contBorders.push(border);
  }
}

function loadContBonus(data){
  for (let display of data){
    contBonusBoxes.push(display);
  }
}

function loadSeaRoutes(data){
  for (let sr of data){
    seaRoutes.push(sr);
  }
}

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