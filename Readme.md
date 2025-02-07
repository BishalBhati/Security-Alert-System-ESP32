<!DOCTYPE html>
<html>
<head>
    <title>Security Alert System using ESP32, PIR Sensor, and Buzzer</title>
</head>
<body>
    <h1>Security Alert System using ESP32, PIR Sensor, and Buzzer</h1>

    <h2>Overview</h2>
    <p>This project is a simple security alert system using an <strong>ESP32</strong>, a <strong>PIR motion sensor</strong>, and a <strong>buzzer</strong>. The system detects motion and triggers an alert by activating the buzzer. Additionally, it can send alerts via Wi-Fi to a web server or mobile device.</p>

    <h2>Features</h2>
    <ul>
        <li>Motion detection using a PIR sensor</li>
        <li>Audible alert using a buzzer</li>
        <li>ESP32-based real-time monitoring</li>
        <li>Optional Wi-Fi integration for remote alerts</li>
    </ul>

    <h2>Components Required</h2>
    <ul>
        <li>ESP32 Development Board</li>
        <li>PIR Motion Sensor (HC-SR501)</li>
        <li>Buzzer (Active or Passive)</li>
        <li>Jumper Wires</li>
        <li>Breadboard</li>
    </ul>

    <h2>Wiring Diagram</h2>
    <ul>
        <li>PIR Sensor Output (OUT) → ESP32 GPIO</li>
        <li>Buzzer Positive (+) → ESP32 GPIO</li>
        <li>GND of all components → ESP32 GND</li>
    </ul>

    <h2>Code Implementation</h2>
    <p>The system is programmed using <strong>Arduino IDE</strong>. The ESP32 continuously monitors the PIR sensor, and when motion is detected, it triggers the buzzer and optionally sends an alert over Wi-Fi.</p>

    <h2>Installation & Setup</h2>
    <ol>
        <li>Install <strong>Arduino IDE</strong> and add ESP32 board support.</li>
        <li>Connect the ESP32, PIR sensor, and buzzer as per the wiring diagram.</li>
        <li>Upload the provided code to the ESP32.</li>
        <li>Monitor alerts via serial console or web server (if enabled).</li>
    </ol>

    <h2>Usage</h2>
    <p>Once powered on, the system will monitor motion. If motion is detected, the buzzer will sound an alarm. If Wi-Fi is configured, alerts can be sent to a mobile app or web dashboard.</p>

    <h2>Future Enhancements</h2>
    <ul>
        <li>Integrate with a mobile app for remote notifications.</li>
        <li>Add a camera module for image capture.</li>
        <li>Include a real-time monitoring dashboard.</li>
    </ul>

    <h2>License</h2>
    <p>This project is open-source. Feel free to modify and improve it.</p>
</body>
</html>
