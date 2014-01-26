  
# GamePad Demo
# from https://github.com/teemujonkkari/gamepad-demo

GamePad demo shows how to use mobile phone browser as gamepad for playing game in your desktop browser.

## How to test

1. Install Node.js
2. Download GamePad demo to some folder
3. Browse to specified folder with Terminal/Console
4. Install required Node.js modules: $ npm install socket.io express
5. Fix right ip address for socket connection in gamepad.js
5. Launch demo: $ sudo node server.js (port 80)
6. Open game with browser: http://172.0.0.1/
7. Browse with your mobile browser to your computer's network address (http://192.168.1.20/gamepad/) to use the gamepad.

