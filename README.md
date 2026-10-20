# A smart dashboard for controlling a small greenhouse.

### 1. What is it?
A web-based dashboard for a greenhouse communicating to a Raspberry Pico to control watering:

- Shows live data (water, light, temperature, humidity)
- Lets you click areas on a map to control different sections (zones)
- Built with tools to make it work smoothly in a browser

### 2. How it’s organized
- `home/page.js` = main screen with the “map” and interactive controls
- `zone/page.js` = detail screen for one greenhouse area (Zone 1/2/3/4)
- `public/instana.jpg` = background map image on home page
- `scss` style files = colors and layout (e.g., slate/dark gray background)

### 3. What the user sees
- A big map image
- Four round “hotspot” buttons (1–4) positioned on the map
- Click one and you move into that zone’s controls
- Live stats displayed (knobs, buttons) for plant environment

### 4. What it controls
- Water level (pump on/off/auto)
- Light on/off
- Temperature and humidity indicators
- Zone navigation
> 
