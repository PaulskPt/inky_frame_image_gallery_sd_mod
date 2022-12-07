
# SPDX-FileCopyrightText: Copyright (c) 2022 Pimoroni Ltd
#
# SPDX-License-Identifier: MIT
#
# An offline image gallery that switches between groups of five .jpg images
# on your SD card (copy them across by plugging your SD into a computer).
# If you want to use your own images they must be 600 x 448 pixels or smaller
# and saved as *non-progressive* jpgs
#
# Modifications by Paulus Schulinck (Github: @PaulskPt)
#  This script looks for .jpg image files in the /sd/images folder of the SD-Card
#  The script needs multiples of 5 image files.
#  If there is not a multiple of 5 images files the script will print a message and raise a RuntimeError
#  After all of the first group of five image files have been displayed,
#  the script will continue with a second group of five image files.
#  When the fifth image of the last group has been displayed,
#  the script will cycle to the first first group.
#
#  This example comes with the following image files:
#  +------+-----+-------------------------------------------+
#  | GRP  | IMG | FILENAME                                  |
# --------+-----+-------------------------------------------+
#  |  1   |  1  | /sd/images/jwst1.jpg                      |
#  +------+-----+-------------------------------------------+
#  |  1   |  2  | /sd/images/jwst2.jpg                      |
#  +------------+-------------------------------------------+
#  |  1   |  3  | /sd/images/jwst3.jpg                      |
#  +------+-----+-------------------------------------------+
#  |  1   |  4  | /sd/images/jwst4.jpg                      |
#  +------+-----+-------------------------------------------+
#  |  1   |  5  | /sd/images/jwst5.jpg                      |
#  +------+-----+-------------------------------------------+
#  |  2   |  6  | /sd/images/MSFS2020_C337H_.jpg            |
#  +------+-----+-------------------------------------------+
#  |  2   |  7  | /sd/images/MSFS2020_C337H_2.jpg           |
#  +------+-----+-------------------------------------------+
#  |  2   |  8  | /sd/images/MSFS2020_KittyHawk_E3.jpg      |
#  +------+-----+-------------------------------------------+
#  |  2   |  9  | /sd/images/MSFS2020_Pilatus_Porter_v2.jpg |
#  +------+-----+-------------------------------------------+
#  |  2   | 10  | /sd/images/MSFS2020_Porter_twilight.jpg   |
#  +------+-----+-------------------------------------------+
#
import gc, sys
from pimoroni import ShiftRegister
from picographics import PicoGraphics, DISPLAY_INKY_FRAME as DISPLAY
from machine import Pin
import jpegdec
import uos


img_dict = {}

# set up the display
#display = PicoGraphics(display=DISPLAY_INKY_FRAME)
gc.collect()
disp = PicoGraphics(DISPLAY)
WIDTH, HEIGHT = disp.get_bounds()
disp.set_font("bitmap8")
gc.collect()

# Inky Frame uses a shift register to read the buttons
SR_CLOCK = 8
SR_LATCH = 9
SR_OUT = 10

sr = ShiftRegister(SR_CLOCK, SR_LATCH, SR_OUT)
# print(f"type(ShiftRegister)= {type(sr)}")
# print(f"dir(ShiftRegister)= {dir(sr)}")
# print(f"ShiftRegister.__dict__= {sr.__dict__}")

# set up the button LEDs
button_a_led = Pin(11, Pin.OUT)
button_b_led = Pin(12, Pin.OUT)
button_c_led = Pin(13, Pin.OUT)
button_d_led = Pin(14, Pin.OUT)
button_e_led = Pin(15, Pin.OUT)

# and the activity LED
activity_led = Pin(6, Pin.OUT)

#
# List images files which are on the SD-Card
#
def disp_files():
    global img_dict
    dir = "/sd/images"
    f_lst = uos.listdir(dir)
    # print(f"f_lst= {f_lst}")
    img_dict = {}  # Empty the dictionary (it could be filled)
    grp = 1
    if isinstance(f_lst, list) and len(f_lst) > 0:
        for _ in range(len(f_lst)):
            if f_lst[_].find(".jpg") >= 0:
               img_dict[_] = f_lst[_]
        le = len(img_dict)
        if le > 0 and le % 5 == 0:
            print(f"\nThere are {le} image files (.jpg) on SD-Card in folder \'{dir}\':")
            s1 = "+-----+-----+--------------------------------------------------+"
            s2 = "| GRP | IMG | FILENAME                                         |"
            print(s1)
            print(s2)
            print(s1)
            idx = 0
            for k, v in img_dict.items():
                print("| {:2d}  | {:3d} | {:<48s} |".format(grp, idx+1, img_dict[idx][:-4]))
                print(s1)
                idx += 1
                if idx > 0 and idx % 5 == 0:
                    grp += 1
            print()
        else:
            s = "Please make it a multiple of 5 image files."
            print(s+"\n")
            disp_text(s)
            raise RuntimeError               
    else:
        print("no image files found on SD-card")
        sys.exit() 
# Create a new JPEG decoder for our PicoGraphics
j = jpegdec.JPEG(disp)  # was (display)

def display_image(nr, filename):

    try:
        if nr != 99:
            print("Opening image file: {:3d} \'{:s}\'".format(nr, filename))
        # Open the JPEG file
        j.open_file(filename)
        gc.collect()
        # Decode the JPEG
        j.decode(0, 0, jpegdec.JPEG_SCALE_FULL)

        # Display the result
        disp.update()
    except OSError as e:
        print(f"Could not open file: error {e} occurred")
        return False

            
def disp_file_list():
    fn = "/sd/files_raster.jpg"
    display_image(99, fn)
    scale=2
    x = 3
    y = 58
    h = 23
    le = len(img_dict)
    grp = 1
    disp.set_pen(0)
    for k, v in img_dict.items():
        # v_width = disp.measure_text(v, scale=scale)
        # print(f"v= {v}, v_width= {v_width}")
        s = "    {:2d}    {:3d}   {:<50s}".format(grp, k+1, v[:-4])  # truncate the file suffix (.jpg)
        disp.text(s, x, y, scale=scale)
        y += h
        n = k + 1
        if n % 5 == 0:
            grp += 1
    disp.update()
    gc.collect()
            
def disp_text(txt):
    disp.set_pen(1)
    disp.clear()
    disp.set_pen(0)
    disp.text(txt, 10, HEIGHT//2-1, scale=3)
    disp.update()
    gc.collect()

"""
    By @PaulskPt:
    The boot.py tries to mount the SD-card
    Here we just check if we are able to switch to the SD-Card
    If we not succeed we will try to mount the SD-Card
"""
try:
    disp_files()
    disp_file_list()
except OSError as e:
    print(f"Error: {e}. Trying to mount SD-Card")
    from machine import SPI
    import sdcard
    # set up the SD card
    sd_spi = SPI(0, sck=Pin(18, Pin.OUT), mosi=Pin(19, Pin.OUT), miso=Pin(16, Pin.OUT))
    try:
        sd = sdcard.SDCard(sd_spi, Pin(22))
        uos.mount(sd, "/sd")
    except OSError as e:
        s = "No SD-Card found. Exiting..."
        print(s+"\n")
        disp_text(s)
        sys.exit()        
    if sd:
        disp_files()
    else:
        s = "No SD-Card found. Exiting..."
        print(s+"\n")
        disp_text(s)
        sys.exit()
        
print("Press button A...E to display an image")

gc.collect()  # Claw back some RAM!
# set up and enable vsys hold so we don't go to sleep
HOLD_VSYS_EN_PIN = 2

hold_vsys_en_pin = Pin(HOLD_VSYS_EN_PIN, Pin.OUT)
hold_vsys_en_pin.value(True)


# setup
activity_led.on()
# update the image on Inky every time it's powered up
# comment these lines out if running on battery power
# button_a_led.on()
# display_image(IMAGE_A)


files_shown_dict = {}
grp_idx = 0
curr_img = ""
msg_shown = False

while True:
    button_a_led.off()
    button_b_led.off()
    button_c_led.off()
    button_d_led.off()
    button_e_led.off()

    # read the shift register
    # we can tell which button has been pressed by checking if a specific bit is 0 or 1
    result = sr.read()  # result usually = 128. When button_a .. button_e is pressed result = 129..133
    
    # print(f"result= {result}")
    button_a = sr[7]
    button_b = sr[6]
    button_c = sr[5]
    button_d = sr[4]
    button_e = sr[3]

    # light up the activity LED when Inky is awake
    activity_led.on()
    idx = -1 # force key not found if no button was pressed

    if button_a == 1:
        button_a_led.on()
        #d_img = IMAGE_A
        idx = 0
    elif button_b == 1:
        button_b_led.on()
        #d_img = IMAGE_B
        idx = 1
    elif button_c == 1:
        button_c_led.on()
        #d_img = IMAGE_C
        idx = 2
    elif button_d == 1:
        button_d_led.on()
        #d_img = IMAGE_D
        idx = 3
    elif button_e == 1:
        button_e_led.on()
        #d_img = IMAGE_E
        idx = 4

    if idx in [0, 1, 2, 3 ,4]:  # handle only if a button was pressed
        idx2 = (grp_idx * 5) + idx
        if idx2 in img_dict.keys():
            fn = '/sd/images/'+img_dict[idx2]
            if fn == curr_img:
                if not msg_shown:
                    print(f"Image \'{curr_img}\' is being displayed")
                    msg_shown = True
                idx = -1
            else:
                msg_shown = False
                curr_img = fn
                display_image(idx2+1, fn)
                # go to sleep if on battery power
                activity_led.off()
                hold_vsys_en_pin.init(Pin.IN)
                if not idx2 in files_shown_dict.keys():
                    files_shown_dict[idx2] = curr_img
                if len(files_shown_dict) == 5:
                    print(f"Group {grp_idx+1} images shown:")
                    for k,v in files_shown_dict.items():
                        print("{:3d} {:s}".format(k+1, v))
                    grp_idx += 1
                    if (grp_idx+1) * 5 > len(img_dict):
                        grp_idx = 0
                        print(f"All images have been displayed.\nContinuing with the first group.")
                    else:
                        print(f"All images of group {grp_idx} have been displayed.\nContinuing with the next group.")
                    files_shown_dict = {}  # we start a new series
