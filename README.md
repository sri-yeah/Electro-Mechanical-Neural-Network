# Electro-Mechanical-Neural-Network (EMNN)

The fundamentals of AI can be extremely difficult to understand, particularly the concept of Neural Networks and machine learning. 

We created an Electro-Mechanical Neural Network. This Mechanical Neural Network is a mechanical implementation of an artifical neural network. To be more specific a Multilayer Perceptron with ReLU activation functions. It can be adapted to model real valued function or logical function, like the logical AND, OR, and the exclusive or(XOR). This means that we can adapt the weights between the neurons of the network such that for a given output the network produces the correct output. E.g. we can adjust the weight such that the network models the XOR functions and outputs true if and only if one of the two inputs is true and the other false.

This is built via 3d printer and incorporate levers, which represent the neurons. These levers are linked by strings, corresponding to the connections between the neurons of a MLP. Adjusting the weight block, which connect the strings to the levers, by motor, allows to adjust the weights of the network. Thus, the effect of adapting the weights can be intuitively observed. 

---

## 🧠 Project Summary

- **Model Architecture:** 2–2–1 MLP with ReLU activation and a bias term in the input layer 
- **Components:** Levers (neurons), strings (weights), pulleys (weighted summation), motors (weight updates)  
- **Interactive Interface:** Touchscreen GUI + chatbot 
- **Main Control:** Raspberry Pi 5 + Arduino Due via UART 
- **Educational Focus:** Logic computation and forward propagation, physically observable  

---

## ⚙️ How It Works

### 🔗 Pulley System: Calculating the Weighted Sum

Each neuron’s input is calculated using a **two-stage pulley mechanism**. Strings connected to hidden-layer levers transmit forces into the output layer:

- The levers move vertically, pulling strings attached to pulleys.
- These pulleys reduce the force linearly (typically by ¼) and combine multiple inputs into a **single effective movement**.
- The result: A mechanical analogue of a **weighted sum**.

The final movement determines whether the output lever activates, corresponding to the neuron firing.

### 🔁 Motor Mechanism: Adjusting the Weights

Each string passes through a **motorized clamp** that adjusts its tension, representing different weights:

- Weights range from **-1 to 1**, with discrete steps due to mechanical resolution.
- The position of the clamp along the lever determines the torque applied (weight × input).
- Adjusting this position modifies how much influence a neuron has on the next.

### 🔌 Motor Control via Arduino Due

- The **Arduino Due** is the central motor controller.
- It stores the **current state** of weights and receives **target states** via UART from the Pi.
- For each motor:
  - Determines the **required direction** (clockwise or counterclockwise).
  - Activates the motor for a calibrated **time duration** based on the required movement.
- All logic is managed via a **state machine** on the Arduino.

---

## 🧑‍💻 User Interface & Interaction

Users interact with the EMNN through a **touchscreen interface** and **chatbot assistant**, powered by the Raspberry Pi 5.

### 👆 `display.py` (Main Script)

- Provides a **chatbot-style GUI** where users enter logic expressions (e.g. `A XOR B`).
- After hitting "Enter", the system:
  1. **Parses and simplifies** the logic expression.
  2. **Identifies** one of 16 possible 2-input logic functions.
  3. **Selects the corresponding weight preset**.

### 🧠 `weights_parser.py`

- Reduces user input into one of 16 Boolean functions.
- Maps each function to a **predefined dictionary of weights**.

### 🧭 UART Communication via `uart_comm.py`

- Sends target weights to the Arduino over **UART**.
- Arduino performs necessary motor movements to reach the desired weight configuration.

---

## 🔢 Activation Function: DoReLU

We use a simplified version of ReLU, called **Double Rectified Linear Unit (DoReLU)**:

- Inputs/outputs constrained to the [0, 1] range  
- Weights constrained between -1 and 1  
- Still enables **non-linearity**, essential for logic modelling and learning  

---

## 🧠 Logic Modelling Capabilities

With two binary inputs, the EMNN supports all **16 possible 2-input Boolean functions**. 

- Each input combination (`00`, `01`, `10`, `11`) maps to either `0` or `1`.
- Boolean algebra simplification is applied.
- The system loads one of the 16 **preset weight configurations** accordingly.

Examples include:

- AND
- OR
- NAND
- XOR
- NOR
- Constant TRUE/FALSE

---

## 📈 Project Architecture

- **Mechanical Layer:** Levers, pulleys, and strings to model neuron connections  
- **Electrical Layer:** Servo motors controlled via Arduino for weight adjustment  
- **Digital Layer:** Raspberry Pi for GUI, logic processing, and UART communication  

### Architecture Overview
```text
User → Touch Display (Raspberry Pi GUI)
     → display.py → weights_parser.py + uart_comm.py
     → Arduino Due (motor control logic)
     → Motors move → Strings pull → Pulleys sum → Levers activate
     → Physical neuron fires
```

---

🔭 Future Work

- Higher-precision weight control with better motors
- Larger scale for better control and visualisation
- LEDs to show neuron activations

---

👨‍🔬 Team
We are seven third-year EEE/EIE students at Imperial College London, in collaboration with IBM:

- Sriyesh Bogadapati
- Benjamin De Vos
- Archisha Garg
- Arjan Hayre
- Zian Lin
- Conrad Perry
- Letong Xu
  
