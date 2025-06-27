
# Electro-Mechanical Neural Network (EMNN)

The fundamentals of AI can be extremely difficult to understand, particularly the concept of Neural Networks and machine learning. 

We created an Electro-Mechanical Neural Network. This Mechanical Neural Network is a mechanical implementation of an artifical neural network. To be more specific a Multilayer Perceptron with ReLU activation functions. It can be adapted to model real valued function or logical function, like the logical AND, OR, and the exclusive or(XOR). This means that we can adapt the weights between the neurons of the network such that for a given output the network produces the correct output. E.g. we can adjust the weight such that the network models the XOR functions and outputs true if and only if one of the two inputs is true and the other false.

This is built via 3d printer and incorporate levers, which represent the neurons. These levers are linked by strings, corresponding to the connections between the neurons of a MLP. Adjusting the weight block, which connect the strings to the levers, by motor, allows to adjust the weights of the network. Thus, the effect of adapting the weights can be intuitively observed. 

---

## 📁 Contents

- [1. Project Overview](#1-project-overview)
- [2. Specifications & Architecture](#2-specifications--architecture)
- [3. Materials ](#3-materials)
- [4. Pulley & Lever Computation](#4-pulley--lever-computation)
- [5. Motor Weight Adjustment](#5-motor-weight-adjustment)
- [6. Embedded Control System](#6-embedded-control-system)
- [7. Arduino Multi-Servo Controller](#7-arduino-multi-servo-controller)
- [8. User Interface & Software Stack](#8-user-interface--software-stack)
- [9. Logic Function Modelling](#9-logic-function-modelling)
- [10. Design Decisions](#10-design-decisions)
- [11. Meeting Records & Rationales](#11-meeting-records--rationales)
- [12. Future Improvements](#12-future-improvements)

---

## 1. Project Overview

The Electro-Mechanical Neural Network (EMNN) is a 2–2–1 multilayer perceptron (MLP) built using physical components. It allows users to explore how neural networks process information by converting computational structures into tangible, mechanical motion.

![Hardware Setup](EMNN1.jpg)

---

## 2. Specifications & Architecture

**Neural Model**  
- Type: Multilayer Perceptron (MLP)  
- Layers: 2 input neurons (+1 bias), 2 hidden neurons, 1 output neuron  
- Activation Function: Double Rectified Linear Unit (DoReLU)  
- Weight Resolution: 5 discrete levels in range [-1, 1]  

**Mechanical**  
- Motion Type: Vertical displacement via lever rotation  
- Weighted Sum: Achieved through two-stage pulley network  
- Output Activation: Based on threshold displacement of output lever  

**Control**  
- Controller: Arduino Due  
- Motor Control: Via state machine based on input weight preset  
- Communication: UART protocol between Raspberry Pi 5 and Arduino Due  

**Interface**  
- GUI + Chatbot: Python (Touchscreen input)  
- Scripts: `display.py`, `weights_parser.py`, `uart_comm.py`

---

## 3. Materials 

| Material              | Purpose                                                                                       |
|----------------------|-----------------------------------------------------------------------------------------------|
| **PLA (3D-printed parts)** | Used for levers and movable elements. Lightweight to allow activation without affecting prior layers. |
| **T-Slot Structural Frame** | Provides rigidity to hold all layers and pulleys while being easy to work with for a potentially modular design. Designed to resist tension and maintain alignment. |
| **Fishing Wire**     | Serves as neuron-to-neuron connectors. Thin for compact routing, but strong enough for load-bearing. |

---

## 4. Pulley & Lever Computation

Each output neuron receives signals via a **pulley array** from four hidden-layer connections:

- Levers transmit vertical force based on input activation.
- Force is transferred via strings to a **two-stage pulley system**, reducing movement to ¼ and summing the total effect.
- The output lever activates when summed tension passes a threshold, mimicking neural firing.

---

## 5. Motor Weight Adjustment

Each string passes through a **motorised clamp**, with its position determining the applied weight:

- **Range:** -1 to 1, represented by 5 fixed motor positions  
- **Control:** Servo rotates clamp to change torque applied by the neuron input  
- **Effect:** Adjusts string length and thus weight influence on the connected lever

---

## 6. Embedded Control System

**Arduino Due:**
- Manages current state of each motor
- Receives updated target weights from Raspberry Pi
- Uses a **finite state machine** to:
  - Determine rotation direction
  - Execute time-based position changes
  - Store updated weight position state

**Communication Protocol:**
- UART (Serial1): Raspberry Pi → Arduino Due
- Command-based interface (7-bit messages)
- Directional motor control with fallback override mode

---

# 7. Arduino Multi-Servo Controller

The Arduino part is designed to control 8 servos using serial commands. It supports two operation modes: **positioning (WEIGHT)** and **pulse override (OVERRIDE)**. It communicates with external devices via `Serial1` (receiving commands) and `Serial2` (sending predefined sequences).

## Features

- Supports up to **8 servos**, each with **5 preset logical positions**
- Handles serial command input with a **circular buffer**
- Two modes:
  - `WEIGHT` mode: rotate servo to target position
  - `OVERRIDE` mode: send a short directional pulse
- Dynamic servo attach/detach to reduce jitter and power usage
- Optional UART-triggered command sequence (`Serial2`)
- Built-in direction inversion for specific servo IDs

---

## Hardware Setup

| Component       | Details                         |
|----------------|----------------------------------|
| Board          | Arduino with multiple Serial ports |
| Servo Pins     | Digital pins 2–9                |
| Trigger Pin    | Digital pin 11 (input)          |
| UART           | Serial1 (command in), Serial2 (sequence out) |

Servos 0, 1, 4, and 7 are direction-inverted by default.

---

## Command Format

Each command is 7 bits:

[0-2] Servo Address (3 bits)

[3-5] Value Code (3 bits)

[6] Override Flag (1 bit)


Examples:

- `0001000`: Servo 0, move to position index 4, no override
- `0110011`: Servo 3, direction code 1 (CCW), with override

---

## Modes Explained

### 1. WEIGHT Mode

- Triggered when override bit is `0`
- Interprets valueCode as a **target index (0–4)**
- Calculates time based on distance moved
- Rotates in proper direction and stops after duration

### 2. OVERRIDE Mode

- Triggered when override bit is `1`
- Interprets valueCode as **direction**
  - `100`: clockwise
  - `010`: stop
  - `001`: counter-clockwise
- Moves for a fixed 50 ms pulse, then stops

---

## Timing and Direction

- `ROTATION_TIME_UNIT = 1100 ms` per position step
- `PWM_CW = 80`, `PWM_STOP = 90`, `PWM_CCW = 100`
- Additional time offsets can be specified per servo (`servoExtraSpin[]`)

---

## Trigger Sequence (Serial2)

When pin 11 transitions from LOW to HIGH, a predefined sequence is sent over `Serial2`:

```text
0000000
0010000
0100000
...
1110000
```

---

## 8. User Interface & Software Stack

**display.py (GUI):**

* Touchscreen-based chatbot
* Accepts logic expressions like `A XOR B`
* Calls `weights_parser.py` to simplify logic
* Loads corresponding weight preset and sends to Arduino via `uart_comm.py`

**weights\_parser.py:**

* Simplifies logic using Boolean algebra
* Maps user intent to one of 16 preset logical functions

**uart\_comm.py:**

* Encodes 7-bit messages for servo control
* Sends commands via UART to the Arduino Due

---

## 9. Logic Function Modelling

With 2 binary inputs, EMNN can model all **16 possible logical functions** (`2^4`):

* Input combinations: `00`, `01`, `10`, `11`
* Output: `0` or `1` per input state
* Preset weights stored and applied based on simplified Boolean logic

Examples:

* AND
* OR
* XOR
* NAND
* NOR
* Constant TRUE or FALSE

---

## 10. Design Decisions

| Decision                              | Rationale                                                            |
| ------------------------------------- | -------------------------------------------------------------------- |
| Physical system instead of simulation | Boosts engagement, makes learning interactive                        |
| Time-based motor control              | Avoids complexity of encoders, keeps cost low                        |
| PLA parts                         | Lightweight enough for neuron levers without interfering with motion |
| DoReLU function                       | Compatible with physical constraints, yet supports non-linearity     |
| Two-layer MLP                         | Minimal yet expressive enough to model all 2-input logic functions   |

---

---

## 11. Meeting Records & Rationales

Throughout the project, we held **weekly meetings** at the end of each week to discuss progress, share design updates, and help unblock each other when facing technical or conceptual challenges. These meetings were crucial for early detection of bottlenecks and collaborative ideation, especially during integration-heavy stages. We also kept each other updated throughout the week in our group chat, for milestones achieved for motivation and to share proud achievements. 

| Week  | Key Progress |
|-------|--------------|
| Week 3 | **Frame made**: Completed initial construction of the frame using T-slot structural frame to define the neuron layout geometry. Initial dimensioning and spatial validation were performed to ensure mechanical feasibility for servo integration and interconnect routing. |
| Week 4 | **Neuron prototype**: Fabricated the first mechanical Neuron unit, focusing on evaluating material suitability and hinge actuation range. <br> **GUI design prototype**: Developed an initial GUI wireframe to establish layout, interaction flow, and design consistency for Raspberry Pi touchscreen control. |
| Week 5 | **Neuron prototype**: Iteratively improved the prototype for improved structural integrity and actuation smoothness based on early testing feedback. <br> **Chatbot prototype**: Built a lightweight chatbot interface using Python for user-driven interaction, to explain the workings of the network via speaker. <br> **Weights parser template complete**: Designed and implemented a template parser to convert logical equations into numerical weight arrays. |
| Week 6 | **Neuron final design**: Finalised geometry and mounting strategy for all Neuron units, incorporating alignment tolerances and assembly repeatability. <br> **GUI + Chatbot prototype**: Connected the initial GUI front-end to the chatbot logic pipeline to verify real-time interactivity and data flow prior to hardware integration. |
| Week 7 | **GUI + Chatbot integration with weights parser**: Linked the software stack into a continuous pipeline—GUI → chatbot → parser—to simulate full input-to-actuation data flow. <br> **Servo control for motors template on Arduino**: Developed a modular control framework on Arduino to accept incoming values and execute PWM-based servo control to enable single-weight testing. <br> **Servo control for all motors**: Mounted and wired all servos onto final neuron hardware; validated coordinated response and mechanical independence under test sequences. |
| Week 8 | **GUI redesign to final design**: Refined the UI for robustness, clarity and ergonomics. <br> **GUI + Chatbot + Weights parser on Raspi**: Deployed the integrated GUI, chatbot, and parser modules to the Raspberry Pi with local execution and event-driven logic. <br> **UART receiver first iteration on Arduino**: Implemented and tested a basic UART decoder on Arduino to parse incoming weight data and queue motor commands. <br> **UART transmitter first iteration and integration with display.py on Raspi**: Wrote UART-transmit logic within the GUI pipeline on Raspberry Pi, coupling chatbot output to hardware signals via display.py. |
| Week 9 | **UART transmitter + receiver synchronisation to final design**: Established reliable, deterministic serial communication between Raspberry Pi and Arduino with fully aligned timing and protocol handling. <br> **Weights parser template and motor controller template synchronised to final design, aligned with physical layout + wiring + physical timing requirements**: Finalised structure and synchronised data packet logic to match actual Neuron layout, cable routing, and servo feedback characteristics. <br> **Touch display, Raspi and Arduino mounted to frame**: Fully assembled and enclosed all electronic subsystems on the physical frame, with functional wiring, signal isolation, and secured modules for final testing and demos. |

Each weekly sync included:
- **Design rationale reviews**: Justification of chosen methods and hardware  
- **Debugging support**: Peer assistance in diagnosing mechanical/electrical issues  
- **Alignment on goals**: Ensured software and hardware tracks remained in sync  
- **Future planning**: Set priorities for the upcoming week’s sprint

---

## 12. Future Improvements

* Larger scale for better control and visualisation 
* Finer motor control using optical encoders or stepper motors 
* Visual LED/GUI representation of neuron states 
* Multi-output layer for more complex logic (e.g., 2-bit outputs) 
* Regression mode for real-valued input/output demonstration 

---

## 👨‍🔬 Team

We are seven third-year EEE/EIE students at Imperial College London, in collaboration with IBM:

* Sriyesh Bogadapati
* Benjamin De Vos
* Archisha Garg
* Arjan Hayre
* Zian Lin
* Conrad Perry
* Letong Xu

> *“Forget the code. Come play with intelligence.”*


