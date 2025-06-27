#include <Servo.h>

#define NUM_SERVOS 8
#define NUM_POSITIONS 5
#define COMMAND_BUFFER_SIZE 16

enum ServoState { IDLE, WEIGHT, OVERRIDE };

struct ServoCommand {
  char data[8];
};

struct ServoControl {
  Servo servo;
  ServoState state = IDLE;
  int positionIndex = 2;
  bool overrideActive = false;
  unsigned long moveStartTime = 0;
  unsigned long moveDuration = 0;
  int direction = 90;
};

const float positionValues[NUM_POSITIONS] = {-1.0, -0.3, 0.0, 0.5, 1.0};
const unsigned long ROTATION_TIME_UNIT = 1100;
const unsigned long OVERRIDE_PULSE_DURATION = 50;

const int PWM_STOP = 90;
const int PWM_CW = 80;
const int PWM_CCW = 100;

ServoControl servos[NUM_SERVOS];
const int servoPins[NUM_SERVOS] = {2, 3, 4, 5, 6, 7, 8, 9};

const int servoExtraSpin[NUM_SERVOS] = {300, 0, 300, 0, 0, 0, 0};

const int triggerPin = 11;
bool lastTriggerState = LOW;
bool Triggered = false;

ServoCommand commandBuffer[COMMAND_BUFFER_SIZE];
int bufferHead = 0;
int bufferTail = 0;
bool commandExecuting = false;

void setup() {
  pinMode(triggerPin, INPUT);
  Serial.begin(9600);
  Serial1.begin(9600);
  Serial2.begin(9600);

  for (int i = 0; i < NUM_SERVOS; i++) {
    servos[i].servo.attach(servoPins[i]);
    servos[i].servo.detach();
    pinMode(servoPins[i], OUTPUT);
    digitalWrite(servoPins[i], LOW);
  }

  Serial.println("System initialized All servos stay LOW");
}

void loop() {

  Triggered = true;

  int currentState = digitalRead(triggerPin);
  if (currentState == HIGH && lastTriggerState == LOW && !Triggered) {
    Serial.println("Sending Data to [UART2]...");
    Serial2.write("0000000", 7);
    delay(500);
    Serial2.write("0010000", 7);
    delay(500);
    Serial2.write("0100000", 7);
    delay(500); 
    Serial2.write("0110000", 7);
    delay(500);
    Serial2.write("1000000", 7);
    delay(500);
    Serial2.write("1010000", 7);
    delay(500); 
    Serial2.write("1100000", 7);
    delay(500); 
    Serial2.write("1110000", 7);

    
    Triggered = true;
  }
  lastTriggerState = currentState;

  handleSerial();
  processCommandBuffer();

  unsigned long now = millis();
  for (int i = 0; i < NUM_SERVOS; i++) {
    ServoControl &s = servos[i];
    if ((s.state == WEIGHT || s.state == OVERRIDE) && now - s.moveStartTime >= s.moveDuration) {
      s.servo.write(PWM_STOP);
      delay(5);
      s.servo.detach();
      digitalWrite(servoPins[i], LOW);
      if (s.state == WEIGHT) {
        s.state = IDLE;
        commandExecuting = false; // allow next command
      }
    }
  }
}

void handleSerial() {
  while (Serial1.available() >= 7) {
    if ((bufferTail + 1) % COMMAND_BUFFER_SIZE == bufferHead) {
      // buffer full, discard
      Serial.println("BUFFER FULL SKIPPING");
      return;
    }
    ServoCommand cmd;
    Serial1.readBytes(cmd.data, 7);
    cmd.data[7] = '\0';
    commandBuffer[bufferTail] = cmd;
    bufferTail = (bufferTail + 1) % COMMAND_BUFFER_SIZE;
  }
}

void processCommandBuffer() {
  if (commandExecuting || bufferHead == bufferTail) return;

  ServoCommand cmd = commandBuffer[bufferHead];
  bufferHead = (bufferHead + 1) % COMMAND_BUFFER_SIZE;

  int servoAddr = binToInt(cmd.data, 0, 3);
  int valueCode = binToInt(cmd.data, 3, 3);
  bool override = (cmd.data[6] == '1');

  if (servoAddr < 0 || servoAddr >= NUM_SERVOS || valueCode < 0 || valueCode > 7)
    return;

  ServoControl &s = servos[servoAddr];
  bool isInverted = (servoAddr == 0 || servoAddr == 1 || servoAddr == 4 || servoAddr == 7); // reverse direction

   if (override) {
    s.overrideActive = true;
    s.state = OVERRIDE;
    s.moveDuration = OVERRIDE_PULSE_DURATION;
    s.moveStartTime = millis();
    commandExecuting = true;

    if (!s.servo.attached()) s.servo.attach(servoPins[servoAddr]);

    if (valueCode == 0b100)
      s.direction = isInverted ? PWM_CW : PWM_CCW;
    else if (valueCode == 0b010)
      s.direction = PWM_STOP;
    else if (valueCode == 0b001)
      s.direction = isInverted ? PWM_CCW : PWM_CW;
    else
      s.direction = PWM_STOP;

    s.servo.write(s.direction);

    Serial.print("OVERRIDE servo "); Serial.print(servoAddr);
    Serial.print(" → PWM "); Serial.print(s.direction);
    Serial.print(" (code "); Serial.print(valueCode); Serial.println(")");

  } else {
    int targetIndex = valueCode;
    if (targetIndex < 0 || targetIndex >= NUM_POSITIONS) return;

    int currentIndex = s.positionIndex;
    int delta = targetIndex - currentIndex;
    int direction = (delta > 0) ? 1 : ((delta < 0) ? -1 : 0);

    s.positionIndex = targetIndex;
    s.overrideActive = false;
    s.state = WEIGHT;
    s.moveDuration = abs(delta) * (ROTATION_TIME_UNIT + servoExtraSpin[servoAddr]);
    s.moveStartTime = millis();
    commandExecuting = true;

    if (!s.servo.attached()) s.servo.attach(servoPins[servoAddr]);

    if (direction > 0)
      s.direction = isInverted ? PWM_CCW : PWM_CW;
    else if (direction < 0)
      s.direction = isInverted ? PWM_CW : PWM_CCW;
    else
      s.direction = PWM_STOP;

    s.servo.write(s.direction);

    Serial.print("WEIGHT servo "); Serial.print(servoAddr);
    Serial.print(" → position "); Serial.print(positionValues[targetIndex]);
    Serial.print(" | direction: "); Serial.print(s.direction);
    Serial.print(" | time: "); Serial.println(s.moveDuration);
  }
}

int binToInt(const char* data, int start, int length) {
  int val = 0;
  for (int i = 0; i < length; i++) {
    char c = data[start + i];
    if (c == '1') {
      val |= (1 << (length - 1 - i));
    } else if (c != '0') {
      return -1;
    }
  }
  return val;
}
