/*
Shannon's Bird Cage

Here is the circuit used for the game.

8   ● = ● = ● = ●   
7   |   |   |   |   
6   ● - ● - ● - ●   
5   |   |   |   |   
4   ● - ● - ● - ●   
3   |   |   |   |   
2   ● - ● - ● - ●   
1   |   |   |   |   
0   ● = ● = ● = ●   
    0 1 2 3 4 5 6
    A B C D E F G

Single lines are resistors, double lines
are connections (with zero resistance).

Nodes are shown as circles. Valid moves
are shown as (single) lines. One player
(the machine) is called CUT and removes
lines. The other (human) is SHORT, and
short-circuits lines.

CUT wins if the top row is separated from
the bottom row. SHORT wins if the top
row is connected to the bottom (with
zero resistance).

The top row is connected to a 5V supply,
the bottom row is connected to ground via
a resistor (to avoid a real short circuit
if SHORT wins).

This program measures the voltage at the nodes
and uses Shannon's heuristic to choose the
next move - this is the one that has the maximum
voltage drop between adjoining nodes.

*/

// Pins used to read voltages using analogRead
byte nodePins[13] = {A1, A2, A3, A4, A5, A6, A8, A9, A10, A11, A12, A13, A15};

// The button to show the next move.
// Useful reference: http://www.gammon.com.au/switches
const byte switchPin = 8;
byte oldSwitchState = HIGH;

// An array storing the state of the circuit.
// Nodes (where i and j are both even) store the voltages measured via analogRead.
// Moves (where i+j is odd) store the voltage differences between adjoining nodes. 
int volts[9][7];

// An array storing which moves have already been made.
// A value of 1 in position i, j (where i+j is odd) means the move has been made already.
int moves[9][7];

const int maxV = 1023; // 5V represented in 10 bits

void setup() {
  Serial.begin(9600);
  Serial.println("Shannon's Bird Cage");

  for (int i = 0; i < 13; i++) {
    pinMode(nodePins[i], INPUT_PULLUP);
  }

  pinMode (switchPin, INPUT_PULLUP);

  for (int i = 0; i < 9; i++) {
    for (int j = 0; j < 7; j++) {
      volts[i][j] = -1;
      moves[i][j] = 0;
    }
  }
  // top row is always at 5V
  // (note bottom row is not at 0V, since there is a resistor to avoid shorting)
  volts[8][0] = maxV;
  volts[8][2] = maxV;
  volts[8][4] = maxV;
  volts[8][6] = maxV;
}

void loop() {
  byte switchState = digitalRead(switchPin);
  if (switchState != oldSwitchState) {
    oldSwitchState = switchState;
    delay(10); // debounce time
    if (switchState == LOW) {
      checkGameOver();
      updateVoltages();
      computeDifferences();
      displayVoltages();
      displayVoltageDifferences();
      //displayMoves();
      chooseMove();
    }
  }
}

// Return true if the position represents a node (where a voltage measurement
// is made).
boolean isNode(int i, int j) {
  return (i % 2 == 0) && (j % 2 == 0);
}

// Return true if the position represents a move.
boolean isMove(int i, int j) {
  return (i + j) % 2 == 1;
}

void checkGameOver() {
  // We know the game is over if the bottom row is either
  // 0V (CUT wins) or 5V (SHORT wins).
  
  // We need to temporarily disconnect the pull-up resistors,
  // since they will alter the voltage readings.
  for (int i = 0; i < 13; i++) {
    pinMode(nodePins[i], INPUT);
  }
  delay(10);

  int bottomRowVoltage = analogRead(A15);
  if (bottomRowVoltage == 0) {
    Serial.println("I win! (CUT)");
  } else if (bottomRowVoltage == maxV) {
    Serial.println("You win! (SHORT)");
  }

  // Re-connect pull-up resistors
  for (int i = 0; i < 13; i++) {
    pinMode(nodePins[i], INPUT_PULLUP);
  }
  delay(10);
}

// Read the voltages for all nodes
void updateVoltages() {
  volts[6][0] = analogRead(nodePins[0]);
  volts[4][0] = analogRead(nodePins[1]);
  volts[2][0] = analogRead(nodePins[2]);

  volts[2][2] = analogRead(nodePins[3]);
  volts[4][2] = analogRead(nodePins[4]);
  volts[6][2] = analogRead(nodePins[5]);

  volts[6][4] = analogRead(nodePins[6]);
  volts[4][4] = analogRead(nodePins[7]);
  volts[2][4] = analogRead(nodePins[8]);

  volts[2][6] = analogRead(nodePins[9]);
  volts[4][6] = analogRead(nodePins[10]);
  volts[6][6] = analogRead(nodePins[11]);

  // bottom row
  volts[0][0] = analogRead(nodePins[12]);
  volts[0][2] = volts[0][0];
  volts[0][4] = volts[0][0];
  volts[0][6] = volts[0][0];
}

// Compute the voltage differences for all moves (differences between nodes).
void computeDifferences() {
  for (int i = 7; i >= 1; i--) { // skip top and bottom rows
    for (int j = 0; j < 7; j++) {
      if ((i % 2 == 0) && (j % 2 == 1)) {
        volts[i][j] = abs(volts[i][j - 1] - volts[i][j + 1]);
      } else if ((i % 2 == 1) && (j % 2 == 0)) {
        volts[i][j] = abs(volts[i - 1][j] - volts[i + 1][j]);
      }
    }
  }
}

// Use the Shannon heuristic (largest voltage difference) to choose the next move.
void chooseMove() {
  int maxVoltageDiff = -1;
  int mi = -1;
  int mj = -1;
  for (int i = 7; i >= 1; i--) { // skip top and bottom rows
    for (int j = 0; j < 7; j++) {
      // check valid move, and hasn't already been played
      if (isMove(i, j) && moves[i][j] == 0) {
        if (volts[i][j] > maxVoltageDiff) {
          maxVoltageDiff = volts[i][j];
          mi = i;
          mj = j;
        }
      }
    }
  }
  moves[mi][mj] = 1;
  Serial.print("Move: ");
  Serial.print(mi);
  Serial.print(", ");
  Serial.println(mj);
}

void displayVoltages() {
  for (int i = 8; i >= 0; i--) {
    Serial.print(i);
    Serial.print("|");
    for (int j = 0; j < 7; j++) {
      if (isNode(i, j)) {
        Serial.print(volts[i][j]);
      }
      Serial.print("\t");
    }
    Serial.println();
  }
}

void displayVoltageDifferences() { 
  for (int i = 7; i >= 1; i--) {
    Serial.print(i);
    Serial.print("|");
    for (int j = 0; j < 7; j++) {
      if (isMove(i, j)) {
        Serial.print(volts[i][j]);
      }
      Serial.print("\t");
    }
    Serial.println();
  }
}

void displayMoves() {
  for (int i = 7; i >= 1; i--) {
    Serial.print(i);
    Serial.print("|");
    for (int j = 0; j < 7; j++) {
      if (isMove(i, j)) {
        Serial.print(moves[i][j]);
      }
      Serial.print("\t");
    }
    Serial.println();
  }
}
