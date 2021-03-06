import canlib
import cantools
from canlib import canlib
from canlib.canlib import ChannelData, Stat
import json


db = cantools.database.load(open("can1.dbc", "r"))
frame_ids = [ frame.frame_id for frame in db.messages ]

def send_data(ch):
    from random import randint

    N = lambda: (randint(0, 100) - 50)/50

    for s in range(0, 12):
        txFrame = db.get_message_by_name("ams_cell_temperatures")

        cantx = { "temperature_multiplexor" : s}
        for t in range(0, 5):
            cantx[f"t{t + 1}s{s + 1}"] = 40 + 10*N()
    
        tx_id = txFrame.frame_id
        tx_data = txFrame.encode(cantx)
        ch.write_raw(tx_id, tx_data)

    for s in range(0, 12):
        txFrame = db.get_message_by_name("ams_cell_voltages")

        cantx = { "voltage_multiplexor" : 2*s}
        for v in range(0, 6):
            cantx[f"v{v + 1}s{s + 1}"] = 3.8 + 0.2*N()

        tx_id = txFrame.frame_id
        tx_data = txFrame.encode(cantx)
        ch.write_raw(tx_id, tx_data)

        cantx = { "voltage_multiplexor" : 2*s+1}
        for v in range(6, 11 - (s % 2)):
            cantx[f"v{v + 1}s{s + 1}"] = 3.8 + 0.2*N()
    
        tx_id = txFrame.frame_id
        tx_data = txFrame.encode(cantx)
        ch.write_raw(tx_id, tx_data)

def send_status(ch):
    txFrame = db.get_message_by_name("ams_status_1")

    cantx = dict()
    cantx["air1_closed"]          = 0
    cantx["air2_closed"]          = 0
    cantx["sc_closed"]            = 0
    cantx["pre_charge_status"]    = 0
    cantx["ams_error"]            = 0
    cantx["imd_error"]            = 0
    cantx["state_of_charge"]      = 0.7
    cantx["min_cell_voltage"]     = 3.7
    cantx["max_cell_voltage"]     = 3.9
    cantx["min_cell_temperature"] = 28
    cantx["max_cell_temperature"] = 42
    cantx["fan_speed"]            = 60
    
    tx_id = txFrame.frame_id
    tx_data = txFrame.encode(cantx)
    ch.write_raw(tx_id, tx_data)

def cdev():
    cdev_ = dict()
    for channelNumber in range(canlib.getNumberOfChannels()):
        name = canlib.ChannelData(channelNumber).channel_name
        cdev_[name] = channelNumber

    return cdev_


virtual1 = 'Kvaser Virtual CAN Driver (channel 0)'
virtual2 = 'Kvaser Virtual CAN Driver (channel 1)'

def can_channel(device_name, bitrate):
    channel_number = cdev()[device_name]
    availability = canlib.canOPEN_ACCEPT_VIRTUAL
    driver = canlib.canDRIVER_NORMAL
    if bitrate == 1000000:
        bitrate =  canlib.canBITRATE_1M
    else:
        bitrate = canlib.canBITRATE_500K

    ch = canlib.openChannel(channel_number, availability)
    ch.setBusOutputControl(driver)
    ch.setBusParams(bitrate)
    return ch

def receive_data(ch):
    datad = dict()
    while Stat.RX_PENDING in ch.readStatus():
        rx = ch.read()
        rx_id = rx.id
        rx_data = bytes(rx.data)
    
        try:
            if rx_id in frame_ids:
                rxFrame = db.get_message_by_frame_id(rx_id)
                data = rxFrame.decode(rx_data)
                datad.update(data)
        except:
            print("ERROR")
    return datad



#ch1 = can_channel(virtual1)
#ch2 = can_channel(virtual2)
#
#ch1.busOn()
#ch2.busOn()
#
#send_status(ch2)
#print(receive_data(ch1))
