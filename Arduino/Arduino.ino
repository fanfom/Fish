#include <Keyboard.h>
#include <Mouse.h>
#include <MouseTo.h>

const float CORRECTION_FACTOR = 1;


void setup() {
  Serial.begin(9600);
  Serial.setTimeout(10);
  Keyboard.begin();
  Mouse.begin();
  
  MouseTo.setCorrectionFactor(CORRECTION_FACTOR);
}

void movetopos(int x1, int y1, int x2, int y2) {
    const int deltaX = abs(x2 - x1);
    const int deltaY = abs(y2 - y1);
    const int signX = x1 < x2 ? 2 : -2;
    const int signY = y1 < y2 ? 2 : -2;
    //
    int error = deltaX - deltaY;
    //
    while((((x1 > x2)&&signX==-2)||(x1<x2&&signX==2)) || (((y1 > y2)&&signY==-2)||(y1<y2&&signY==2)))
   {
        
        const int error2 = error * 2;
        //
        if(error2 > -deltaY) 
        {
            error -= deltaY;
            x1 += signX;
            Mouse.move(signX,0);
        }
        if(error2 < deltaX) 
        {
            error += deltaX;
            y1 += signY;
            Mouse.move(0,signY);
        }
     }
}
void moveTo(int x, int y, char button) {
  MouseTo.setTarget(x, y);
  while (MouseTo.move() == false) {}
  delay(random(1000, 1500));

  Mouse.press(button);
  delay(random(120, 150));
  Mouse.release(button);
  delay(1500);
}
void pressKey(char key) {
  Keyboard.press(key);
  delay(random(60, 130));
  Keyboard.releaseAll();
}

void pressKey(char first, char second) {
  Keyboard.press(first);
  Keyboard.press(second);
  delay(random(60, 130));
  Keyboard.releaseAll();
}
void esc(){
  pressKey(0xB1);
}
void clickto(String loot){
  int sx = loot.indexOf('[') + 1;
  int sy = loot.indexOf(',');
  int p = loot.indexOf('{') + 1;
  int p2 = loot.indexOf('|');
  int p3 = loot.indexOf('}');
  int cur_positionx = loot.substring(p, p2).toInt();
  int cur_positiony = loot.substring(p2 + 1, p3).toInt();
  int x = loot.substring(sx, sy).toInt();
  int y = loot.substring(sy + 1, loot.length() - 1).toInt();
  movetopos(cur_positionx, cur_positiony, x, y);
  delay(random(130, 210));
  Mouse.press(MOUSE_LEFT);
  delay(random(100, 150));
  Mouse.release(MOUSE_LEFT);
  delay(random(100, 150));
}

void test(){
 MouseTo.setTarget(0, 0);
 while (MouseTo.move() == false) {}
 delay(1000);
 MouseTo.setTarget(1500, 0);
 while (MouseTo.move() == false) {}
 delay(1000);

}

void changeRod(String touch){

  pressKey('i'); 
  
  int sx = touch.indexOf('[') + 1;
  int sy = touch.indexOf(',');
    
  int x = touch.substring(sx, sy).toInt();
  int y = touch.substring(sy + 1, touch.length() - 1).toInt();
  
  moveTo(x, y, MOUSE_RIGHT);

  pressKey('i');
}

void useSlot(String slot){
  int start = slot.indexOf('[');
  char key = slot.charAt(start + 1);
  pressKey(key);
}
void milk(){
  for (int i=0;i<7;i++){
    Mouse.press(MOUSE_LEFT);
    delay(500+random(1,50));
    Mouse.release(MOUSE_LEFT);
    delay(random(200,300));
    Mouse.press(MOUSE_RIGHT);
    delay(500+random(1,50));
    Mouse.release(MOUSE_RIGHT);
    delay(random(200,300));
  }
}
void go(String go){
  int p = go.indexOf('{') + 1;
  int p2 = go.indexOf('}');
  int time = go.substring(p,p2).toInt();
  Keyboard.press('w');
  delay(time+random(0,3));
  Keyboard.release('w');
}
  
void beer(String beer){
  useSlot("[0]");
  int p = beer.indexOf('{') + 1;
  int p2 = beer.indexOf('|');
  int p3 = beer.indexOf('}');
  int cur_positionx = beer.substring(p,p2).toInt();
  int cur_positiony = beer.substring(p2+1,p3).toInt();
  movetopos(cur_positionx,cur_positiony,1507, 857);
  delay(random(130, 210));
  Mouse.press(MOUSE_LEFT);
  delay(random(100, 150));
  Mouse.release(MOUSE_LEFT);
  delay(random(100, 150));
  delay(1000);
  movetopos(1507,857,1152,454);
  delay(random(130, 210));
  Mouse.press(MOUSE_LEFT);
  delay(random(100, 150));
  Mouse.release(MOUSE_LEFT);
  delay(random(100, 150));
  Keyboard.press(0xB1);
  delay(random(100,150));
  Keyboard.release(0xB1);
  delay(random(100,150));
  Keyboard.press(0xB1);
  delay(random(100,150));
  Keyboard.release(0xB1);
  delay(random(100,150));
}

void takeLoot(String loot){

  int sx = loot.indexOf('[') + 1;
  int sy = loot.indexOf(',');
  int p = loot.indexOf('{') + 1;
  int p2 = loot.indexOf('|');
  int p3 = loot.indexOf('}');
  int cur_positionx = loot.substring(p,p2).toInt();
  int cur_positiony = loot.substring(p2+1,p3).toInt();
  int x = loot.substring(sx, sy).toInt();
  int y = loot.substring(sy + 1, loot.length() - 1).toInt();
  movetopos(cur_positionx,cur_positiony,x,y);
  delay(random(130, 210));
  Mouse.press(MOUSE_RIGHT);
  delay(random(100, 150));
  Mouse.release(MOUSE_RIGHT);
  delay(random(100, 150));
}
void MouseMove(String loot){
  int sx = loot.indexOf('[') + 1;
  int sy = loot.indexOf(',');
  int p = loot.indexOf('{') + 1;
  int p2 = loot.indexOf('|');
  int p3 = loot.indexOf('}');
  int cur_positionx = loot.substring(p,p2).toInt();
  int cur_positiony = loot.substring(p2+1,p3).toInt();
  int x = loot.substring(sx, sy).toInt();
  int y = loot.substring(sy + 1, loot.length() - 1).toInt();
  movetopos(cur_positionx,cur_positiony,x,y);
}

char getKey(char key) {
  switch  (key) {
    case 'w': return 'w';
    case 's': return 's';
    case 'a': return 'a';
    case 'd': return 'd';
    case 'r': return 'r';
    case 'i': return 'i';
    default : return '@';
  }
}

void exitGame(){
  pressKey(0xB1);
  moveTo(373, 169, MOUSE_LEFT );
  moveTo(1227,626, MOUSE_LEFT );
  moveTo(1000,650, MOUSE_LEFT );
  pressKey(0xB1);
}

void skipCalendar(){
  pressKey(0xB1);
  pressKey(0xB1);
}

void PressCtrl(){
  delay(random(1, 20));
  Keyboard.press(0x80);
  delay(random(10, 20));
  Keyboard.release(0x80);
}

void drag_n_drop(String loot){
  int sx = loot.indexOf('[') + 1;
  int sy = loot.indexOf(',');
  int p = loot.indexOf('{') + 1;
  int p2 = loot.indexOf('|');
  int p3 = loot.indexOf('}');

  int p4 = loot.indexOf('<') + 1;
  int p5 = loot.indexOf('?');
  int p6 = loot.indexOf('>');
  
  int cur_positionx = loot.substring(p, p2).toInt();
  int cur_positiony = loot.substring(p2 + 1, p3).toInt();
  int x = loot.substring(sx, sy).toInt();
  int y = loot.substring(sy + 1, loot.length() - 1).toInt();
  int x1 = loot.substring(p4, p5).toInt();
  int y1 = loot.substring(p5+1,p6).toInt();
  movetopos(cur_positionx, cur_positiony, x, y);
  delay(random(130, 210));
  Mouse.press(MOUSE_LEFT);
  delay(random(100, 150));
  movetopos(x,y,x1,y1);
  Mouse.release(MOUSE_LEFT);
  delay(random(100, 150));
  Mouse.press(MOUSE_LEFT);
  delay(random(100, 150));
  Mouse.release(MOUSE_LEFT);
  delay(random(100, 150));
}


void loop() {

  String input = Serial.readString();
  int length = input.length();
  if (length != 0) {
    if (input.startsWith("space")) {
      Keyboard.press(0x20);
      delay(random(10,20));
      Keyboard.release(0x20);
    } else if (input.startsWith("Rod")) {
      changeRod(input);
    }
      else if (input.startsWith("Drag")) {
      drag_n_drop(input);
    }
    else if (input.startsWith("Ctrl")) {
      PressCtrl();
    }
    else if (input.startsWith("Loot")) {
      takeLoot(input);
    } else if (input.startsWith("Beer")) {
      beer(input);
    } else if (input.startsWith("Slot")) {
      useSlot(input);
    } else if (input.startsWith("test")) {
      test();
    } else if (input.startsWith("Move")) {
      MouseMove(input);
    } else if (input.startsWith("Exit")) {
      exitGame();
    } else if (input.startsWith("Esc")) {
      esc();
    } 
      else if (input.startsWith("LClick")) {
      clickto(input);
    } else if (input.startsWith("Skip_calendar")) {
      skipCalendar();
    } else {
      for (int i = 0; i < length; i++) {
        delay(random(130, 210));
        char symbol = getKey(input[i]);
        if (symbol != '@') Keyboard.press(symbol); delay(random(10, 40)); Keyboard.release(symbol);
      }
    }

    Serial.print("END");
  }

}
