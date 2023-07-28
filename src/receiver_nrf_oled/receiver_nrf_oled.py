"""ESP32_S3_mini"""

import machine
import time
import struct
import ntptime

from sub.pin import *

import sub.lobo_sh1106_fr_buf as sh1106
from sub.writer import Writer
import sub.umr_h_10 as umr_h

import sub.lobo_nrf24l01 as nrf24l01

import sub.credentials_wifi as credentials_wifi
import sub.lobo_wireless as wireless

machine.idle()


def nrf_setup() -> nrf24l01.NRF24L01:
    """
    Creates nrf24l01
    @return: Instance
    @rtype: nrf24l01.NRF24L01
    """
    _payload_size = 3 * 4  # 3 times 4 bytes per float

    ce = D5
    csn = D6

    # chip enable
    ce.init(mode=machine.Pin.OUT, value=0)
    # chip select NOT
    csn.init(mode=machine.Pin.OUT, value=1)

    # Enable SPI
    # SPI_PORTS = ({"ID": **2**, "SPI_SCK": SPI_SCK, "SPI_MOSI": SPI_MOSI, "SPI_MISO": SPI_MISO},)
    spi = machine.SPI(SPI_PORTS[0]["ID"])

    spi.init(
        baudrate=40000000,
        miso=SPI_PORTS[0]["SPI_MISO"],
        mosi=SPI_PORTS[0]["SPI_MOSI"],
        sck=SPI_PORTS[0]["SPI_SCK"],
    )

    # Enable nRF
    nrf = nrf24l01.NRF24L01(spi, cs=csn, ce=ce, payload_size=_payload_size)
    nrf.reg_write(0x01, 0b11111000)  # enable auto-ack on all pipes

    # Setup piping
    pipe = b"\xf5\x26\xe3\x13\xfb"
    nrf.open_rx_pipe(1, pipe)
    nrf.start_listening()

    return nrf


def receive(nrf: nrf24l01.NRF24L01, display: sh1106.SH1106_I2C = None, writer: Writer = None) -> None:
    """
    Receives and outputs data from nrf24l01
    @param nrf: From where to receive
    @type nrf: nrf24l01.NRF24L01
    @param display: Where to output
    @type display: sh1106.SH1106_I2C
    @param writer: How to output
    @type writer: Writer
    """
    # Receiver
    while True:
        if nrf.any():
            # Receive and clean the pipe
            buf = nrf.recv()
            got = struct.unpack("fff", buf)
            nrf.flush_rx()

            # Show result
            print("r {t:.1f} {p:.1f} {h:.1f}".format(t=got[0], p=got[1], h=got[2]))
            if display is not None:
                line_print(display, writer,
                           "r {t:.1f} {p:.0f} {h:.0f} {g:02d}:{m:02d}Z".format(t=got[0], p=got[1], h=got[2],
                                                                               g=time.localtime()[3],
                                                                               m=time.localtime()[4])
                           )


def sh1106_setup() -> (sh1106.SH1106_I2C, Writer):
    """
    Sets up the oled
    @return: display, Writer
    @rtype: (sh1106.SH1106_I2C, Writer)
    """
    _interface = machine.I2C(
        I2C_PORTS[0]["ID"],
        sda=I2C_PORTS[0]["I2C_SDA"],
        scl=I2C_PORTS[0]["I2C_SCL"],
        freq=1000000,
    )
    _disp = sh1106.SH1106_I2C(
        128,
        64,
        _interface,
        rotate=180
    )
    _disp.poweron()
    _disp.reset()
    _disp.contrast(128)

    _wri = Writer(_disp, umr_h, verbose=False)

    return _disp, _wri


def line_print(display: sh1106.SH1106_I2C, writer: Writer, text: str) -> None:
    """
    Prints a line at the bottom
    @param display: Where to output
    @type display: sh1106.SH1106_I2C
    @param writer: How to output
    @type writer: Writer
    @param text: String to output
    @type text: str
    """
    writer.set_textpos(
        display, display.height - display.pages - 1, 0
    )
    writer.printstring(text)
    display.show()


print("NAME: {n}\nRole: Rx".format(n=NAME))

_display, _writer = sh1106_setup()
_wlan = wireless.Wireless(ssid=credentials_wifi.ssid, password=credentials_wifi.password)

print(_wlan.connect())
assert _wlan.isconnected is True, "wireless network not connected"

ntptime.settime()

# nRF24l01
_nrf = nrf_setup()
receive(_nrf, _display, _writer)
