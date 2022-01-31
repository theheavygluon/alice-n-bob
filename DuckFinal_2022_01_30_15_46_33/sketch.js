var dist1;
var dist2;
var dist3;


var quack;
var squeak;
var goose;

function preload(){
  quack = loadSound('quack.mp3');
  squeak = loadSound('squeak.mp3');
  random_s = loadSound('random.mp3');
  logo = loadImage('logo.png')
}

function setup() {
  createCanvas(800, 600);
}

function draw() {
  background(255);

  image(logo, 0, 0, logo.width /1.2 , logo.height/1.2);
  
  dist1 = dist(mouseX, mouseY, 150, height/2);
  dist2 = dist(mouseX, mouseY, 400, height/2);
  dist3 = dist(mouseX, mouseY, 650, height/2);
  
  //this could be an object
  if (dist1 < 100){
    fill('red');
    textSize(40);
    text('0',130,100);
  }
  else{
    fill('yellow');
  }
   ellipse(150, height/2, 200, 200);

  if (dist2 < 100){
    fill('red');
    textSize(40);
    text('1',380,100);
  } 
  else {
    fill('blue')
  }
  ellipse(400, height/2, 200, 200);
  
  if (dist3 < 100){
    fill('red');
    textSize(40);
    text(random([0, 1]),645,100)
  } 
  else {
    fill('orange')
  }
  ellipse(650, height/2, 200, 200);

  fill('black');
  textSize(30);
  text('Quack', 80, height/4);
  text('Squeak', 325, height/4);
  text('Random', 575, height/4);
  
  textSize(20);  
  text('click on the buttons to generate your quack code', width/6, 500, );
  //text('click again to stop the sound', width/6, 550);
}

function mousePressed(){
  if (dist1 < 100){
    if (quack.isPlaying()){
      quack.stop();
    }
    else{
      quack.play();
    }
  }
  else if (dist2 < 100){
    if (squeak.isPlaying()){
      squeak.stop();
    }
    else{
      squeak.play();
    }
  }
  else if (dist3 < 100){
    if (random_s.isPlaying()){
      random_s.stop();
    }
    else{
      random_s.play();
    }
  }
}