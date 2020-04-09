# Clean resets a tag back to factory-like state
# For Mifare Classic, tag is zero'd and reformatted as Mifare Classic
# For Mifare Ultralight, tags is zero'd and left empty


import time
import binascii

from pn532pi.pn532.pn532 import pn532, PN532_MIFARE_ISO14443A_106KBPS
from pn532pi.interfaces.pn532i2c import pn532i2c
from pn532pi.interfaces.pn532spi import pn532spi
from pn532pi.interfaces.pn532hsu import pn532hsu

# Set the desired interface to True
SPI = False
I2C = False
HSU = True

if SPI:
    PN532_SPI = pn532spi(pn532spi.SS0_GPIO8)
    nfc = pn532(PN532_SPI)
elif HSU:
    PN532_HSU = pn532hsu(0)
    nfc = pn532(PN532_HSU)

elif I2C:
    PN532_I2C = pn532i2c(1)
    nfc = pn532(PN532_I2C)


password =  bytearray([ 0x12, 0x34, 0x56, 0x78])

def setup():
    print("NTAG21x R/W")
    print("-------Looking for PN532--------")

    nfc.begin()

    versiondata = nfc.getFirmwareVersion()
    if not versiondata:
        print("Didn't find PN53x board")
        raise RuntimeError("Didn't find PN53x board")  # halt

    # Got ok data, print it out!
    print("Found chip PN5 {:#x} Firmware ver. {:d}.{:d}".format((versiondata >> 24) & 0xFF, (versiondata >> 16) & 0xFF,
                                                                (versiondata >> 8) & 0xFF))

    # configure board to read RFID tags
    nfc.SAMConfig()

def loop():
    print("wait for a tag")
    # wait until a tag is present
    tagPresent = False
    while not tagPresent:
        time.sleep(.1)
        tagPresent, uid = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A_106KBPS)

    # if NTAG21x enables r/w protection, uncomment the following line 
    # nfc.ntag21x_auth(password)

    status, buf = nfc.mifareultralight_ReadPage(3)
    capacity = int(buf[2]) * 8
    print("Tag capacity {:d} bytes".format(capacity))

    for i in range(4, int(capacity/4)):
        status, buf = nfc.mifareultralight_ReadPage(i)
        print(binascii.hexlify(buf[:4]))

    # wait until the tag is removed
    while tagPresent:
        time.sleep(.1)
        tagPresent, uid = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A_106KBPS)


if __name__ == '__main__':
    setup()
    while True:
      loop()
