from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.led_matrix.device import max7219
from time import sleep

serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial)

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

while True:
    with canvas(device) as draw:
        # draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((1, -2), "1", fill=1)
    device.contrast(1)