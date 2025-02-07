# Security Alert System using ESP32, PIR Sensor, and Buzzer

## Overview
This project is a simple security alert system using an **ESP32**, a **PIR motion sensor**, and a **buzzer**. The system detects motion and triggers an alert by activating the buzzer. Additionally, it can send alerts via Wi-Fi to a web server or mobile device.

## Features
- Motion detection using a PIR sensor
- Audible alert using a buzzer
- ESP32-based real-time monitoring
- Optional Wi-Fi integration for remote alerts

## Components Required
- ESP32 Development Board
- PIR Motion Sensor (HC-SR501)
- Buzzer (Active or Passive)
- Jumper Wires
- Breadboard
- USB Type B

## Wiring Diagram
- PIR Sensor Output (OUT) → ESP32 GPIO
- Buzzer Positive (+) → ESP32 GPIO
- GND of all components → ESP32 GND

## Code Implementation
The system is programmed using **Arduino IDE**. The ESP32 continuously monitors the PIR sensor, and when motion is detected, it triggers the buzzer and optionally sends an alert over Wi-Fi.

## Installation & Setup
1. Install **Arduino IDE** and add ESP32 board support.
2. Connect the ESP32, PIR sensor, and buzzer as per the wiring diagram.
3. Upload the provided code to the ESP32.
4. Monitor alerts via serial console or web server (if enabled).

## Usage
Once powered on, the system will monitor motion. If motion is detected, the buzzer will sound an alarm. If Wi-Fi is configured, alerts can be sent to a mobile app or web dashboard.

## Future Enhancements
- Integrate with a mobile app for remote notifications.
- Add a camera module for image capture.
- Include a real-time monitoring dashboard.

## License
This project is Owned by ©Bishal Bhati
