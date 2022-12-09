Pimoroni 'Inky Frame' Example: `image gallery sd modified`

Display image files (.jpg), which are a part of a multiple of five image files (5, 10, 15, ...).

Used hardware:

a) `Pimoroni Inky Frame (PIM 642)` <https://shop.pimoroni.com/products/inky-frame-5-7?variant=40057850331219>

b) a Personal computer running Microsoft Windows 11

Used software:

c) Thonny IDE <https://thonny.org>;

d) Pimoroni Github repo <https://github.com/pimoroni/pimoroni-pico>, especially the example: `image_gallery_sd.py`.


For installing, setting up your Inky Frame and preparing image files to use with this example,
see the `Getting Started with Inky Frame` <https://learn.pimoroni.com/article/getting-started-with-inky-frame#troubleshooting>.

Copy all the files in the /sd folder to your SD-Card.


Example description:
====================

This example is a modified version of the example:
`image_gallery_sd.py` at <https://github.com/pimoroni/pimoroni-pico/tree/main/micropython/examples/inky_frame/image_gallery>

  At boot time of the Raspberry Pi Pico W, the MicroPython system will look for a file named `boot.py`. 
  There is a `boot.py` file added to this repo. The boot.py file is such arranged that it tries to mount an SD-Card (if present).
  If it doesn't find an SD-Card, is passes control.
  Next the example script will try to mount an SD-Card. If this fails, the script will print an error message to the Inky Frame display
  (see the file /Docs/No_SD_Card_error.jpg) and to the REPL.
  Then the script will end with a sys.exit() because this example cannot run without images files on an SD-Card.
  
  At startup this example will show on the Inky Frame a list of image files found on the SD-Card in folder /sd/images.
  The function that collects and displays the list of image files on the Inky Frame uses a background image from the file: `/sd/files_raster.jpg`.
  For an example of this list see the file: `Inky_Frame_Image_Files_list.jpg` in the folder `Docs` of this repo.

  This example script looks for .jpg image files in the /sd/images folder of the SD-Card. 
  The script needs multiples of 5 image files (5, 10, 15, ...). 
  If there is not a multiple of 5 images files the script will print a message and raise a RuntimeError. 
  The images are used in groups of five image files. 
  After all of the first group of five image files have been displayed,
  the script will continue with a second group of five image files. 
  When the fifth image of the last group has been displayed,
  the script will cycle to the first first group.

  This example comes with the following image files: ```
  
    +------+-----+-------------------------------------------+
    | GRP  | IMG | FILENAME                                  |
    +------+-----+-------------------------------------------+
    |  1   |  1  | /sd/images/jwst1.jpg                      |
    +------+-----+-------------------------------------------+
    |  1   |  2  | /sd/images/jwst2.jpg                      |
    +------------+-------------------------------------------+
    |  1   |  3  | /sd/images/jwst3.jpg                      |
    +------+-----+-------------------------------------------+
    |  1   |  4  | /sd/images/jwst4.jpg                      |
    +------+-----+-------------------------------------------+
    |  1   |  5  | /sd/images/jwst5.jpg                      |
    +------+-----+-------------------------------------------+
    |  2   |  6  | /sd/images/MSFS2020_C337H_.jpg            |
    +------+-----+-------------------------------------------+
    |  2   |  7  | /sd/images/MSFS2020_C337H_2.jpg           |
    +------+-----+-------------------------------------------+
    |  2   |  8  | /sd/images/MSFS2020_KittyHawk_E3.jpg      |
    +------+-----+-------------------------------------------+
    |  2   |  9  | /sd/images/MSFS2020_Pilatus_Porter_v2.jpg |
    +------+-----+-------------------------------------------+
    |  2   | 10  | /sd/images/MSFS2020_Porter_twilight.jpg   |
    +------+-----+-------------------------------------------+ ```


Disclamer:
This example has been modified, tested on a pc running MS Windows 11 Pro with an Inky Frame connected via USB-cable.

This is a 'work-in-progress'. This example does not (yet) have a functionality to easily switch from one group of five image files to another group.
Neither exists a functionality to individually or randomly select an image file from the image files present on the SD Card.

Update 2022-12-08: succeeded to connect a M5Stack Dual Button I2C device (via a Seeed 6-port Grove Hub) to the I2C socket #1 of the Inky Frame. These two buttons are used to change the group index (up or down). The button presses are programmed through interrupts (see the image of the hardware connection in the Docs folder).

Other document sources:
A file with REPL output: `2022-12-07_21h00_image_gallery_sd_mod.py_REPL_output.txt`

NOTE ON MEMORY PROBLEMS: 

Pimoroni already indicated In their `Getting started with Inky Frame` section `Troubleshooting` sub-section `RAM PROBLEMS`.
Although this example is not using WiFi, I ran into a mmemory error at line 26 with the command: `j = jpegdec.JPEG(disp)`.
My solution: I created a `version 2`of this example in which I removed the functions: `Disp_files()`and `Disp_file_list()`. Removed a part in function `setup()`. I 'hard-coded' the list of ten image files into the script.


License: MIT (see LICENSE file)
