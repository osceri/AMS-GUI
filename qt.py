from PyQt5 import QtCore, QtGui, QtWidgets
import monitor
from CAN_backend import *

nominal_stylesheet = "background-color: rgb(80, 203, 156);\ncolor: rgb(31, 31, 31);\nborder: 4px;\nborder-radius: 4px;"
critical_stylesheet = "background-color: rgb(203, 120, 130);\ncolor: rgb(31, 31, 31);\nborder: 4px;\nborder-radius: 4px;"
color_stylesheet = lambda R, G, B: f"color: rgb(31, 31, 31);\nbackground-color: rgb({R}, {G}, {B});"
color_bar_stylesheet = lambda R, G, B: r"QProgressBar{background-color: rgb(31, 31, 31);border-radius: 4px;border: 1px solid rgb(145, 145, 145);margin-left: 8px;margin-right: 8px;}QProgressBar::chunk{background-color: " + f"rgb({R}, {G}, {B})" + r";border-radius: 4px;border: 4px;margin:2px;}"


def indexer(index):
    if index == 1:
        return ""
    else:
        return f"_{index}"

def replace_text(element, newText):
    currentHtml = element.toHtml()
    currentText = element.toPlainText()
    newHtml = currentHtml.replace(f">{currentText}</", f">{newText}</")
    element.setHtml(newHtml)

def replace_text_label(element, currentText, newText):
    current = element.text()
    new = current.replace(f">{currentText}</", f">{newText}</")
    element.setText(new)

def replace_color(element, newText):
    currentHtml = element.toHtml()
    currentText = element.toPlainText()
    newHtml = currentHtml.replace(f">{currentText}</", f">{newText}</")
    element.setHtml(newHtml)

def replace_color_label(element, newText):
    currentHtml = element.toHtml()
    currentText = element.toPlainText()
    newHtml = currentHtml.replace(f">{currentText}</", f">{newText}</")
    element.setHtml(newHtml)

voltage_lower_boundary = 2.8
voltage_upper_boundary = 4.2
temperature_lower_boundary = -20
temperature_upper_boundary = 80

def voltage_nominal(voltage):
    if voltage < voltage_lower_boundary:
        return False
    if voltage_upper_boundary < voltage:
        return False
    return True

def voltage_clamp(voltage):
    value = round(100 * (voltage - voltage_lower_boundary) / (voltage_upper_boundary - voltage_lower_boundary))
    if value < 0:
        return 0
    if 100 < value:
        return 100

    return value

def temperature_nominal(temperature):
    if temperature < temperature_lower_boundary:
        return False
    if temperature_upper_boundary < temperature:
        return False
    return True

def temperature_clamp(temperature):
    value = round(100 * (temperature - temperature_lower_boundary) / (temperature_upper_boundary - temperature_lower_boundary))
    if value < 0:
        return 0
    if 100 < value:
        return 100

    return value

R_0 = 120
G_0 = 120
B_0 = 120
R_1 = 240
G_1 = 160
B_1 = 120

def temperature_walk(DC):
    R = round(R_0 + (R_1-R_0)*DC/100)
    G = round(G_0 + (G_1-G_0)*DC/100)
    B = round(B_0 + (B_1-B_0)*DC/100)
    return R, G, B


LLLL = [ 3, 6, 9, 1, 4, 7, 10, 2, 5, 8 ]
RRRR = [ 1, 2, 2, 1, 1, 2, 2, 1, 1, 2 ]


def scfi(index):
    return (2*(index // 21) + ((index % 21) // 11) + 1, ((index % 21) % 11) + 1)

def stfi(index):
    return ((index // 5) + 1, (index % 5) + 1)

voltage_labels = [ f"v{c}s{s}" for s, c in [ scfi(index) for index in range(126) ] ]
temperature_labels = [ f"t{t}s{s}" for s, t in [ stfi(index) for index in range(60) ] ]

#def map(v, c):
#    for i in range(12):
#        for k in range(11 - (i % 2)):


from time import sleep

class Ui_MainWindow(monitor.Ui_MainWindow):
    def __init__(self, MainWindow):
        self.setupUi(MainWindow)

        for page in ["temperature", "voltage"]:
            for index in range(6):
                eval(f"replace_text(self.segment_{page}_head_entry_id{indexer(index+1)}, 'SEGMENT {index+1}')")
            for index in range(12):
                eval(f"replace_text(self.segment_{page}_entry_id{indexer(index+1)}, 'SLAVE ID: {index+1:02}')")
        for index in range(126):
            s, c = scfi(index)
            eval(f"replace_text(self.voltage_entry_name{indexer(index+1)}, 'S{s}C{c}')")
            eval(f"self.voltage_entry_value{indexer(index+1)}.setHtml('None')")
        for index in range(60):
            s, t = stfi(index)
            eval(f"replace_text(self.temperature_entry_name{indexer(index+1)}, 'S{s}T{t}')")

            ni = index % 10
            nj = 2*(index // 10)
            nt = 1 + (LLLL[ni] - 1) % 5
            ns = nj + 1 + (LLLL[ni] - 1) // 5
            eval(f"replace_text_label(self.segment_temp_node{indexer(index+1)}, 'S1T11', 'S{ns}T{nt}')")

        self.data = dict()
        self.status = dict()
        self.voltage = dict()
        self.temperature = dict()

        self.voltage = dict()
        self.voltage_slave_sum = dict()
        self.voltage_slave_min = dict()
        self.voltage_slave_max = dict()
        self.voltage_slave_nominal = dict()
        self.voltage_segment_sum = dict()
        self.voltage_segment_min = dict()
        self.voltage_segment_max = dict()
        self.voltage_segment_nominal = dict()
        self.temperature = dict()
        self.temperature_slave_max = dict()
        self.temperature_slave_nominal = dict()
        self.temperature_segment_max = dict()
        self.temperature_segment_nominal = dict()

        self.voltage_bars = dict()
        self.voltage_values = dict()
        self.voltage_slave_sum_bars = dict()
        self.voltage_slave_min_values = dict()
        self.voltage_slave_max_values = dict()
        self.voltage_slave_nominality = dict()
        self.voltage_segment_sum_values = dict()
        self.voltage_segment_sum_bars = dict()
        self.voltage_segment_min_values = dict()
        self.voltage_segment_max_values = dict()
        self.voltage_segment_nominality = dict()
        self.temperature_bars = dict()
        self.temperature_values = dict()
        self.temperature_indicator = dict()
        self.temperature_slave_max_values = dict()
        self.temperature_slave_max_bars = dict()
        self.temperature_slave_nominality = dict()
        self.temperature_segment_max_values = dict()
        self.temperature_segment_max_bars = dict()
        self.temperature_segment_nominality = dict()

        self.log = ["Monitor initialized"]
        self.ch1 = None
        self.ch2 = None
        self.set_references()

        self.update_timer = QtCore.QTimer()
        self.update_timer.start(800)
        self.update_timer.timeout.connect(self.update)

        self.update_can_config()
        self.update_can_config_timer = QtCore.QTimer()
        self.update_can_config_timer.start(1000)
        self.update_can_config_timer.timeout.connect(self.update_can_config)

        self.update_log()
        self.update_log_timer = QtCore.QTimer()
        self.update_log_timer.start(1000)
        self.update_log_timer.timeout.connect(self.update_log)

        self.ts_button.clicked.connect(self.ts_button_callback)
        self.cu_button.clicked.connect(self.cu_button_callback)
        self.ts_n_button.clicked.connect(self.ts_n_button_callback)
        self.cu_n_button.clicked.connect(self.cu_n_button_callback)


    def ts_button_callback(self):
        msg = db.get_message_by_name("dbu_status_1")
        tx = { "activate_ts_button" : 1, "ready_to_drive_button" : 0, "dbu_temperature" : 10 }
        tx_data = msg.encode(tx)
        tx_frame_id = msg.frame_id
        self.LOG("TS ACTIVATE SIGNAL SENT")
        self.ch1.write_raw(tx_frame_id, tx_data)

    def ts_n_button_callback(self):
        msg = db.get_message_by_name("dbu_status_1")
        tx = { "activate_ts_button" : 0, "ready_to_drive_button" : 0, "dbu_temperature" : 10 }
        tx_data = msg.encode(tx)
        tx_frame_id = msg.frame_id
        self.LOG("TS DEACTIVATE SIGNAL SENT")
        self.ch1.write_raw(tx_frame_id, tx_data)

    def cu_button_callback(self):
        msg = db.get_message_by_name("dbu_status_1")
        tx = { "activate_ts_button" : 1, "ready_to_drive_button" : 0, "dbu_temperature" : 10 }
        tx_data = msg.encode(tx)
        tx_frame_id = msg.frame_id
        self.LOG("CU ACTIVATE SIGNAL SENT")
        self.ch1.write_raw(tx_frame_id, tx_data)

    def cu_n_button_callback(self):
        msg = db.get_message_by_name("dbu_status_1")
        tx = { "activate_ts_button" : 0, "ready_to_drive_button" : 0, "dbu_temperature" : 10 }
        tx_data = msg.encode(tx)
        tx_frame_id = msg.frame_id
        self.LOG("CU DEACTIVATE SIGNAL SENT")
        self.ch1.write_raw(tx_frame_id, tx_data)


    def update_can_config(self):
        items = cdev()
        
        # Always keep the virtual2 bus online, in case
        if self.ch2:
            if not virtual2 in items:
                self.ch2.busOff()
                self.ch2 = None
        else:
            if virtual2 in items:
                self.ch2 = can_channel(virtual2, 500000)
                self.ch2.busOn()
                self.LOG("virtual2 connected")


        # Get current items on screen
        citems = []
        for index in range(self.CAN1_device_combo.count()):
            citems.append(self.CAN1_device_combo.itemText(index))

        # Get currently selected item
        selected = self.CAN1_device_combo.currentText()

        # If there are more or fewer items than last time, update the list but keep the current in place
        if set(items) != set(citems):
            self.CAN1_device_combo.clear()
            for index, item in enumerate(items):
                if item == virtual2:
                    continue

                if item == selected and item != '':
                    cindex = index

                self.CAN1_device_combo.addItem(item)

            cindex = None

            if cindex:
                self.CAN1_device_combo.setCurrentIndex(cindex)

        # If a device is not connected, then connect the currently selected one (if possible)
        if not self.ch1:
            if not selected == '':
                self.ch1 = can_channel(selected, 1000000)
                self.ch1.busOn()
                self.LOG("CAN1 connected")
        # If a device is connected, determine wether or not it is the currently selected one, and reconnect that one
        else:
            selected = self.CAN1_device_combo.currentText()

            if selected != self.ch1.channel_data.channel_name:
                self.ch1.busOff()
                self.ch1.close()
                self.LOG("CAN1 disconnected")
                if selected != '':
                    self.ch1 = can_channel(selected, 1000000)
                    self.ch1.busOn()
                    self.LOG("CAN1 connected")

    def update(self):
        if self.ch2:
            #send_data(self.ch2)
            #send_status(self.ch2)
            pass
        if self.ch1:
            self.data.update(receive_data(self.ch1))
            for label in voltage_labels:
                try:
                    self.voltage[label] = self.data[label]
                except:
                    pass
            for label in temperature_labels:
                try:
                    self.temperature[label] = self.data[label]
                except:
                    pass
            
        self.update_data()
        self.update_elements()


    def random_values(self):
        from random import randint

        for index in range(126):
            s, c = scfi(index)
            S = s // 2

            self.voltage[f'v{c}s{s}'] = 3.802 + (randint(0, 100) - 50)/1000

        for index in range(60):
            s, t = stfi(index)
            S = s // 2

            self.temperature[f't{t}s{s}'] = 28.97 + (randint(0, 100) - 50)



    def update_data(self):
        for k in range(6):
            S = k+1
            segment = f'S{S}'

            try:
                self.voltage_segment_sum[segment] = self.voltage[f'v1s{2*S}']
                self.voltage_segment_min[segment] = self.voltage[f'v1s{2*S}']
                self.voltage_segment_max[segment] = self.voltage[f'v1s{2*S}']
                self.voltage_segment_nominal[segment] = voltage_nominal(self.voltage[f'v1s{2*S}'])
                self.temperature_segment_max[segment] = self.temperature[f't1s{2*S}']
                self.temperature_segment_nominal[segment] = temperature_nominal(self.temperature[f't1s{2*S}'])
            except KeyError:
                pass


        for k in range(12):
            s = k+1
            slave = f's{s}'

            try:
                self.voltage_slave_sum[slave] = self.voltage[f'v1s{s}']
                self.voltage_slave_min[slave] = self.voltage[f'v1s{s}']
                self.voltage_slave_max[slave] = self.voltage[f'v1s{s}']
                self.voltage_slave_nominal[slave] = voltage_nominal(self.voltage[f'v1s{s}'])
                self.temperature_slave_max[slave] = self.temperature[f't1s{s}']
                self.temperature_slave_nominal[slave] = temperature_nominal(self.temperature[f't1s{s}'])
            except KeyError:
                pass

        for index in range(60):
            s, t = stfi(index)
            S = 1 + ((s-1) // 2)

            cell = f't{t}s{s}'
            slave = f's{s}'
            segment = f'S{S}'

            try:
                self.temperature_slave_nominal[slave] = self.temperature_slave_nominal[slave] and temperature_nominal(self.temperature[cell])
                if self.temperature_slave_max[slave] < self.temperature[cell]:
                    self.temperature_slave_max[slave] = self.temperature[cell]
            except KeyError:
                pass

            try:
                self.temperature_segment_nominal[segment] = self.temperature_segment_nominal[segment] and temperature_nominal(self.temperature[cell])
                if self.temperature_segment_max[segment] < self.temperature[cell]:
                    self.temperature_segment_max[segment] = self.temperature[cell]
            except KeyError:
                pass


        for index in range(126):
            s, c = scfi(index)
            S = 1 + ((s-1) // 2)

            cell = f'v{c}s{s}'
            slave = f's{s}'
            segment = f'S{S}'

            try:
                self.voltage_slave_sum[slave] += self.voltage[cell]
                if self.voltage[cell] < self.voltage_slave_min[slave]:
                    self.voltage_slave_min[slave] = self.voltage[cell]
                if self.voltage_slave_max[slave] < self.voltage[cell]:
                    self.voltage_slave_max[slave] = self.voltage[cell]
                self.voltage_slave_nominal[slave] = self.voltage_slave_nominal[slave] and voltage_nominal(self.voltage[cell])
            except KeyError:
                pass

            try:
                self.voltage_segment_sum[segment] += self.voltage[cell]
                if self.voltage[cell] < self.voltage_segment_min[segment]:
                    self.voltage_segment_min[segment] = self.voltage[cell]
                if self.voltage_segment_max[segment] < self.voltage[cell]:
                    self.voltage_segment_max[segment] = self.voltage[cell]
                self.voltage_segment_nominal[segment] = self.voltage_segment_nominal[segment] and voltage_nominal(self.voltage[cell])
            except KeyError:
                pass

    def update_log(self):
        ttext = "\n".join(self.log)
        self.terminal.setText(ttext)
        self.terminal.verticalScrollBar().setValue(self.terminal.verticalScrollBar().maximum())

    def LOG(self, text):
        self.log += [text]



    def update_elements(self):
        for cell in self.voltage:
            for element in self.voltage_values[cell]:
                try:
                    
                    voltage = self.voltage[cell]
                    element.setText(f'{voltage:.3f}V')
                except KeyError:
                    pass

            for element in self.voltage_bars[cell]:
                try:
                    
                    level = voltage_clamp(self.voltage[cell])
                    element.setValue(level)
                except KeyError:
                    pass

        for slave in self.voltage_slave_sum:
            for element in self.voltage_slave_sum_bars[slave]:
                try:
                    
                    level = voltage_clamp(self.voltage_slave_sum[slave] / 12)
                    element.setValue(level)
                except KeyError:
                    pass

        for slave in self.voltage_slave_min:
            for element in self.voltage_slave_min_values[slave]:
                try:
                    
                    voltage = self.voltage_slave_min[slave]
                    element.setText(f'{voltage:.3f}V')
                except KeyError:
                    pass

        for slave in self.voltage_slave_max:
            for element in self.voltage_slave_max_values[slave]:
                try:
                    
                    voltage = self.voltage_slave_max[slave]
                    element.setText(f'{voltage:.3f}V')
                except KeyError:
                    pass

        for slave in self.voltage_slave_nominal:
            for element in self.voltage_slave_nominality[slave]:
                try:
                    
                    nominality = self.voltage_slave_nominal[slave]
                    if nominality:
                        replace_text(element, "NOMINAL")
                        element.setStyleSheet(nominal_stylesheet)
                    else:
                        replace_text(element, "CRITICAL")
                        self.LOG(f"Critical voltage in {slave}!")
                        element.setStyleSheet(critical_stylesheet)
                except KeyError:
                    pass

        for segment in self.voltage_segment_sum:
            for element in self.voltage_segment_sum_values[segment]:
                try:
                    
                    voltage = self.voltage_segment_sum[segment]
                    element.setText(f'{voltage:.3f}V')
                except KeyError:
                    pass

            for element in self.voltage_segment_sum_bars[segment]:
                try:
                    
                    level = voltage_clamp(self.voltage_segment_sum[segment] / 21)
                    element.setValue(level)
                except KeyError:
                    pass

        for segment in self.voltage_segment_min:
            for element in self.voltage_segment_min_values[segment]:
                try:
                    
                    voltage = self.voltage_segment_min[segment]
                    element.setText(f'{voltage:.3f}V')
                except KeyError:
                    pass

        for segment in self.voltage_segment_max:
            for element in self.voltage_segment_max_values[segment]:
                try:
                    
                    voltage = self.voltage_segment_max[segment]
                    element.setText(f'{voltage:.3f}V')
                except KeyError:
                    pass

        for segment in self.voltage_segment_nominal:
            for element in self.voltage_segment_nominality[segment]:
                try:
                    
                    nominality = self.voltage_segment_nominal[segment]
                    if nominality:
                        replace_text(element, "NOMINAL")
                        element.setStyleSheet(nominal_stylesheet)
                    else:
                        replace_text(element, "CRITICAL")
                        element.setStyleSheet(critical_stylesheet)
                except KeyError:
                    pass


        for cell in self.temperature:
            for element in self.temperature_values[cell]:
                try:
                    
                    temperature = self.temperature[cell]
                    element.setText(f'{temperature:.3f}C')
                except KeyError:
                    pass

            for element in self.temperature_bars[cell]:
                try:
                    
                    level = temperature_clamp(self.temperature[cell])
                    element.setValue(level)
                    R, G, B = temperature_walk(level)
                    element.setStyleSheet(color_bar_stylesheet(R, G, B))
                except KeyError:
                    pass

            for element in self.temperature_indicator[cell]:
                try:
                    
                    level = temperature_clamp(self.temperature[cell])
                    R, G, B = temperature_walk(level)
                    element.setStyleSheet(color_stylesheet(R, G, B))
                except KeyError:
                    pass


        for slave in self.temperature_slave_max:
            for element in self.temperature_slave_max_values[slave]:
                try:
                    
                    temperature = self.temperature_slave_max[slave]
                    element.setText(f'{temperature:.3f}C')
                except KeyError:
                    pass

            for element in self.temperature_slave_max_bars[slave]:
                try:
                    
                    level = temperature_clamp(self.temperature_slave_max[slave])
                    element.setValue(level)
                    R, G, B = temperature_walk(level)
                    element.setStyleSheet(color_bar_stylesheet(R, G, B))
                except KeyError:
                    pass

        for slave in self.temperature_slave_nominal:
            for element in self.temperature_slave_nominality[slave]:
                try:
                    
                    nominality = self.temperature_slave_nominal[slave]
                    if nominality:
                        replace_text(element, "NOMINAL")
                        element.setStyleSheet(nominal_stylesheet)
                    else:
                        replace_text(element, "CRITICAL")
                        self.LOG(f"Critical temperature in {slave}!")
                        element.setStyleSheet(critical_stylesheet)
                except KeyError:
                    pass

        for segment in self.temperature_segment_max:
            for element in self.temperature_segment_max_values[segment]:
                try:
                    
                    temperature = self.temperature_segment_max[segment]
                    element.setText(f'{temperature:.3f}C')
                except KeyError:
                    pass

            for element in self.temperature_segment_max_bars[segment]:
                try:
                    
                    level = temperature_clamp(self.temperature_segment_max[segment])
                    element.setValue(level)
                    R, G, B = temperature_walk(level)
                    element.setStyleSheet(color_bar_stylesheet(R, G, B))
                except KeyError:
                    pass

        for segment in self.temperature_segment_nominal:
            for element in self.temperature_segment_nominality[segment]:
                try:
                    
                    nominality = self.temperature_segment_nominal[segment]
                    if nominality:
                        replace_text(element, "NOMINAL")
                        element.setStyleSheet(nominal_stylesheet)
                    else:
                        replace_text(element, "CRITICAL")
                        element.setStyleSheet(critical_stylesheet)
                except KeyError:
                    pass

        try:
            text = self.data['air1_closed']
            self.common_stats_A_value.setText(str(text))
        except KeyError:
            pass
        try:
            text = self.data['air2_closed']
            self.common_stats_B_value.setText(str(text))
        except KeyError:
            pass
        try:
            text = self.data['sc_closed']
            self.common_stats_C_value.setText(str(text))
        except KeyError:
            pass
        try:
            text = self.data['ams_error']
            self.common_stats_D_value.setText(str(text))
        except KeyError:
            pass
        try:
            text = self.data['imd_error']
            self.common_stats_E_value.setText(str(text))
        except KeyError:
            pass
        try:
            text = self.data['pre_charge_status']
            self.common_stats_F_value.setText(str(text))
        except KeyError:
            pass
        


    def set_references(self):
        for index in range(126):
            s, c = scfi(index)

            self.voltage_bars[f'v{c}s{s}'] = []
            eval(f"self.voltage_bars['v{c}s{s}'].append(self.voltage_entry_bar{indexer(index+1)})")

            self.voltage_values[f'v{c}s{s}'] = []
            eval(f"self.voltage_values['v{c}s{s}'].append(self.voltage_entry_value{indexer(index+1)})")


        for index in range(12):
            s = index + 1

            self.voltage_slave_sum_bars[f's{s}'] = []
            eval(f"self.voltage_slave_sum_bars['s{s}'].append(self.segment_voltage_entry_stats_A_voltage{indexer(index+1)})")

            self.voltage_slave_min_values[f's{s}'] = []
            eval(f"self.voltage_slave_min_values['s{s}'].append(self.segment_voltage_entry_stats_B_min_value{indexer(index+1)})")

            self.voltage_slave_max_values[f's{s}'] = []
            eval(f"self.voltage_slave_max_values['s{s}'].append(self.segment_voltage_entry_stats_B_max_value{indexer(index+1)})")

            self.voltage_slave_nominality[f's{s}'] = []
            eval(f"self.voltage_slave_nominality['s{s}'].append(self.segment_voltage_entry_stats_A_nominality{indexer(index+1)})")


        for index in range(6):
            s = index + 1

            self.voltage_segment_sum_values[f'S{s}'] = []
            eval(f"self.voltage_segment_sum_values['S{s}'].append(self.segment_voltage_head_entry_stats_E_value{indexer(index+1)})")
            eval(f"self.voltage_segment_sum_values['S{s}'].append(self.segment_temperature_head_entry_stats_E_value{indexer(index+1)})")

            self.voltage_segment_sum_bars[f'S{s}'] = []
            eval(f"self.voltage_segment_sum_bars['S{s}'].append(self.segment_voltage_head_entry_stats_C_voltage{indexer(index+1)})")
            eval(f"self.voltage_segment_sum_bars['S{s}'].append(self.segment_temperature_head_entry_stats_C_voltage{indexer(index+1)})")

            self.voltage_segment_min_values[f'S{s}'] = []
            eval(f"self.voltage_segment_min_values['S{s}'].append(self.segment_voltage_head_entry_stats_D_min_value{indexer(index+1)})")
            eval(f"self.voltage_segment_min_values['S{s}'].append(self.segment_temperature_head_entry_stats_D_min_value{indexer(index+1)})")

            self.voltage_segment_max_values[f'S{s}'] = []
            eval(f"self.voltage_segment_max_values['S{s}'].append(self.segment_voltage_head_entry_stats_D_max_value{indexer(index+1)})")
            eval(f"self.voltage_segment_max_values['S{s}'].append(self.segment_temperature_head_entry_stats_D_max_value{indexer(index+1)})")

            self.voltage_segment_nominality[f'S{s}'] = []
            eval(f"self.voltage_segment_nominality['S{s}'].append(self.segment_voltage_head_entry_stats_C_nomality{indexer(index+1)})")
            eval(f"self.voltage_segment_nominality['S{s}'].append(self.segment_temperature_head_entry_stats_C_nomality{indexer(index+1)})")

        for index in range(60):
            s, t = stfi(index)

            self.temperature_bars[f't{t}s{s}'] = []
            eval(f"self.temperature_bars['t{t}s{s}'].append(self.temperature_entry_bar{indexer(index+1)})")

            self.temperature_values[f't{t}s{s}'] = []
            eval(f"self.temperature_values['t{t}s{s}'].append(self.temperature_entry_value{indexer(index+1)})")

        for index in range(60):
            ni = index % 10
            nj = 2*(index // 10)
            t = 1 + (LLLL[ni] - 1) % 5
            s = nj + 1 + (LLLL[ni] - 1) // 5

            self.temperature_indicator[f't{t}s{s}'] = []
            eval(f"self.temperature_indicator['t{t}s{s}'].append(self.segment_temp_node{indexer(index+1)})")

        for index in range(12):
            s = index + 1

            self.temperature_slave_max_bars[f's{s}'] = []
            eval(f"self.temperature_slave_max_bars['s{s}'].append(self.segment_temperature_entry_stats_A_temperature{indexer(index+1)})")

            self.temperature_slave_max_values[f's{s}'] = []
            eval(f"self.temperature_slave_max_values['s{s}'].append(self.segment_temperature_entry_stats_B_value{indexer(index+1)})")

            self.temperature_slave_nominality[f's{s}'] = []
            eval(f"self.temperature_slave_nominality['s{s}'].append(self.segment_temperature_entry_stats_A_nomality{indexer(index+1)})")


        for index in range(6):
            s = index + 1

            self.temperature_segment_max_bars[f'S{s}'] = []
            eval(f"self.temperature_segment_max_bars['S{s}'].append(self.segment_temperature_head_entry_A_temperature{indexer(index+1)})")
            eval(f"self.temperature_segment_max_bars['S{s}'].append(self.segment_voltage_head_entry_A_temperature{indexer(index+1)})")

            self.temperature_segment_max_values[f'S{s}'] = []
            eval(f"self.temperature_segment_max_values['S{s}'].append(self.segment_temperature_head_entry_stats_B_value{indexer(index+1)})")
            eval(f"self.temperature_segment_max_values['S{s}'].append(self.segment_voltage_head_entry_stats_B_value{indexer(index+1)})")

            self.temperature_segment_nominality[f'S{s}'] = []
            eval(f"self.temperature_segment_nominality['S{s}'].append(self.segment_temperature_head_entry_A_nomality{indexer(index+1)})")
            eval(f"self.temperature_segment_nominality['S{s}'].append(self.segment_voltage_head_entry_A_nomality{indexer(index+1)})")





if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
