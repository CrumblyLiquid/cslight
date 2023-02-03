import numpy as np
import cv2
from PIL import ImageGrab
from screeninfo import get_monitors
import pytesseract
import phue

BRIDGE_IP = '192.168.1.150'
LIGHTS = ['Drak Celsius', 'Dráče Eda'] # Names or ids of our lights
SHOW_CAPTURE = False

bridge = phue.Bridge(BRIDGE_IP)

# Needs to be only done once (press the button on the bridge and start this script)
# bridge.connect()

print(f"Connected to bridge {bridge.get_api()['config']['name']} at {bridge.get_api()['config']['ipaddress']} (API: {bridge.get_api()['config']['apiversion']})")

# Verify we can connect to specified light
for light in LIGHTS:
    light_res = bridge.get_light(light)
    print(f"Selected light {light_res['name']}")

width = 2560
height = 1440
# Find the primary monitor and adjust w,h accordingly
for monitor in get_monitors():
    if monitor.is_primary:
        width = monitor.width
        height = monitor.height

BOX = (70, height-55, 150, height-10)

# Colour bounds for capturing digits on the HUD
LOWER = np.array([250, 200, 160])
UPPER = np.array([255, 255, 255])

last_value = 0
while True:
    img = ImageGrab.grab(BOX)
    img_rgb = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
    mask = cv2.inRange(img_rgb, LOWER, UPPER)
    if(SHOW_CAPTURE):
        cv2.imshow('cslight', mask)

    # Read number from image
    health = pytesseract.image_to_string(mask, config='--psm 7 outputbase digits')
    try:
        new_value = int(health)
    except:
        new_value = 0
    # Eliminate unnecessary calls and eliminate invalid values (valid: 0 < health <= 100)
    if(last_value != new_value and new_value!=0 and new_value <= 100):
        last_value = new_value
        for light in LIGHTS:
            bridge.set_light(light, {'transitiontime' : 1, 'on' : True, 'bri' : int(last_value*1.5)})
    if SHOW_CAPTURE and cv2.waitKey(33) & 0xFF in ( ord('q'), 27 ):
        break
