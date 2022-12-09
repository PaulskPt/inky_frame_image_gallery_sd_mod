#
# An offline image gallery that switches between groups of five .jpg images
# on your SD card (copy them across by plugging your SD into a computer).
#
import gc, sys, time
from pimoroni import ShiftRegister
from picographics import PicoGraphics, DISPLAY_INKY_FRAME
from machine import Pin
import jpegdec
import uos

# set up the display
gc.collect()
disp = PicoGraphics(display=DISPLAY_INKY_FRAME)

gc.collect()

# Create a new JPEG decoder for our PicoGraphics
j = jpegdec.JPEG(disp)  # was (display)
#j = None

gc.collect()

img_dict = {  # Hard-coded list of image file names
    0: 'jwst1',
    1: 'jwst2',
    2: 'jwst3',
    3: 'jwst4',
    4: 'jwst5',
    5: 'MSFS2020_C337H_',
    6: 'MSFS2020_C337H_2',
    7: 'MSFS2020_KittyHawk_E3',
    8: 'MSFS2020_Pilatus_Porter_v2',
    9: 'MSFS2020_Porter_twilight'
}
nr_groups = len(img_dict) // 5

WIDTH, HEIGHT = disp.get_bounds()
disp.set_font("bitmap8")


# Inky Frame uses a shift register to read the buttons
SR_CLOCK = 8
SR_LATCH = 9
SR_OUT = 10
selected_group = 0

hold_vsys_en_pin = None

sr = ShiftRegister(SR_CLOCK, SR_LATCH, SR_OUT)

# set up the button LEDs
button_a_led = Pin(11, Pin.OUT)
button_b_led = Pin(12, Pin.OUT)
button_c_led = Pin(13, Pin.OUT)
button_d_led = Pin(14, Pin.OUT)
button_e_led = Pin(15, Pin.OUT)

m5_btns_present = None

# External M5Stack Dual Button
try:
    btn_blu = Pin(5, Pin.IN, Pin.PULL_UP) # GP5
    btn_red = Pin(4, Pin.IN, Pin.PULL_UP) # GP4
    m5_btns_present = True
except Exception as e:
    print(f"global(): Error while assigning m5 double button device: {e}")
    m5_btns_present = False
    raise

if m5_btns_present:
    B_RED = 0
    B_BLU = 1
    btn_press_counter = 0
    red_debounce_time = 0
    blu_debounce_time = 0
    red_int_flag = 0
    blu_int_flag = 0
else:
    B_RED = None
    B_BLUE = None
    m5btn_dict = None
    btn_press_counter = None
    red_debounce_time = None
    blu_debounce_time = None
    red_int_flag = None
    blu_int_flag = None

# the built-in LED of the Raspberry Pi Pico W
conn_led = Pin(7, Pin.OUT) 
bi_led = Pin(25, Pin.OUT)
# and the activity LED
activity_led = Pin(6, Pin.OUT)
activity_led_state = 0

gc.collect()

#
#  blink_activity_led
#
def blink_activity_led(nr_times):
    global activity_led_state
    curr_state = activity_led_state
    if nr_times is None:
        nr_times = 1
    delay = 0.5
    if curr_state == 1:
        #activity_led.off()  # first switch the led off
        conn_led.value(0)
        time.sleep(delay)
    
    for _ in range(nr_times):
        #activity_led.on()
        conn_led.value(1)       
        time.sleep(delay)
        #activity_led.off()
        conn_led.value(0)
        time.sleep(delay)
        
    if curr_state == 1:  # if the led originally was on, switch it back on
        #activity_led.on()
        conn_led.value(1)

def red_callback(btn_red):
    global red_int_flag, red_debounce_time, btn_press_counter
    if time.ticks_us() - red_debounce_time > 3000:
        print("Red button pressed.")
        red_debounce_time = time.ticks_us()
        red_int_flag=1
        btn_press_counter += 1

def blu_callback(btn_blu):
    global blu_int_flag, blu_debounce_time, btn_press_counter
    if time.ticks_us() - blu_debounce_time > 3000:
        print("Blue button pressed.")
        blu_debounce_time = time.ticks_us()
        blu_int_flag=1
        btn_press_counter += 1
        
if m5_btns_present:
    btn_red.irq(trigger=btn_red.IRQ_FALLING, handler=red_callback)
    btn_blu.irq(trigger=btn_blu.IRQ_FALLING, handler=blu_callback)    


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
    
def disp_text(txt):
    disp.set_pen(1)
    disp.clear()
    disp.set_pen(0)
    disp.text(txt, 10, HEIGHT//2-1, scale=3)
    disp.update()
    gc.collect()

def setup():
    global hold_vsys_en_pin, acitivity_led_state

    print("\nImage gallery SD modified example for Pimoroni Inky Frame")
    if m5_btns_present :
        print("BLUE button <<< Group index >>> RED button")
    print("Press button A...E to display an image")

    gc.collect()  # Claw back some RAM!
    # set up and enable vsys hold so we don't go to sleep
    HOLD_VSYS_EN_PIN = 2

    hold_vsys_en_pin = Pin(HOLD_VSYS_EN_PIN, Pin.OUT)
    hold_vsys_en_pin.value(True)
    
    # setup
    activity_led.on()
    activity_led_state = 1
    
def ck_btns():
    global button_a, button_b, button_c, button_d, button_e
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
    activity_led_state = 1
    idx = -1 # force key not found if no button was pressed

    if button_a == 1:
        button_a_led.on()
        # IMAGE_A
        return 0
    if button_b == 1:
        button_b_led.on()
        # IMAGE_B
        return 1
    if button_c == 1:
        button_c_led.on()
        # IMAGE_C
        return 2
    if button_d == 1:
        button_d_led.on()
        # IMAGE_D
        return 3
    if button_e == 1:
        button_e_led.on()
        # IMAGE_E
        return 4
    return idx

def main():
    global red_int_flag, blu_int_flag
    TAG= "main(): "
    setup()
    gc.collect()
    files_shown_dict = {}
    grp_idx = 1
    curr_img = ""
    msg1_shown = False
    msg2_shown = False
    msg3_shown = False
    print(TAG+f"Current group index = {grp_idx}")
    while True:
        
        if m5_btns_present:
            if red_int_flag is 1:
                grp_idx += 1
                if grp_idx > (nr_groups):
                    grp_idx = 1
                blink_activity_led(grp_idx)
                print(TAG+f"New group index = {grp_idx}")
                red_int_flag = 0
                print(TAG+f"red/blue button pressed {btn_press_counter} times")
                
            if blu_int_flag is 1:
                grp_idx -= 1
                if grp_idx < 1:
                    grp_idx = nr_groups
                blink_activity_led(grp_idx)
                print(TAG+f"New group index = {grp_idx}")
                blu_int_flag = 0
                print(TAG+f"red/blue button pressed {btn_press_counter} times")

        idx = ck_btns()

        if idx in [0, 1, 2, 3 ,4]:  # handle only if a button was pressed
            if not msg1_shown:
                print(TAG+f"index of keypress is: {idx}")
                msg1_shown = True
            idx2 = ((grp_idx-1) * 5) + idx
            if not msg2_shown:
                print(TAG+f"Going to show image whos index is: {idx2}")
                msg2_shown = True
            if idx2 in img_dict.keys():
                fn = '/sd/images/'+img_dict[idx2]+'.jpg'
                if fn == curr_img:
                    if not msg3_shown:
                        print(f"Image \'{curr_img}\' is being displayed")
                        msg3_shown = True
                    idx = -1
                else:
                    msg_shown = False
                    curr_img = fn
                    display_image(idx2+1, fn)
                    # go to sleep if on battery power
                    activity_led.off()
                    conn_led.value(0)
                    activity_led_state = 0
                    hold_vsys_en_pin.init(Pin.IN)
                    if not idx2 in files_shown_dict.keys():
                        files_shown_dict[idx2] = curr_img
                    if len(files_shown_dict) == 5:
                        print(f"Group {grp_idx} images shown:")
                        for k,v in files_shown_dict.items():
                            print("{:3d} {:s}".format(k+1, v))
                        grp_idx += 1
                        if (grp_idx+1) * 5 > len(img_dict):
                            grp_idx = 0
                            print(f"All images have been displayed.\nContinuing with the first group.")
                        else:
                            print(f"All images of group {grp_idx} have been displayed.\nContinuing with the next group.")
                        files_shown_dict = {}  # we start a new series
                        
if __name__ == '__main__':
    main()
