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

// Components to be displayed
let polygons = [];
let srs = [];
let cps = [];
let seaRoutes = [];

function setup() {
  createCanvas(1000, 1000)
  for (let i = 1; i < 7; i++){
    loadJSON(`../MAPS/MichaelMap1/C${i}/c${i}a.json`, loadPolygonsData);
    loadJSON(`../MAPS/MichaelMap1/C${i}/c${i}sr.json`, loadSR);
  }
  loadJSON(`../MAPS/MichaelMap1/seaRoutes.json`, loadSeaRoutes);
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

  for (let route of seaRoutes){
    drawDottedLine(route.x1, route.y1, route.x2, route.y2);
  }

  // Offset dragging
  translate(-offsetX, -offsetY);
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

function loadCP(data){
    for (let p of data) {
    cps.push(p);
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