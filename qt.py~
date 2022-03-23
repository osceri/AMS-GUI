from PyQt5 import QtCore, QtGui, QtWidgets
import monitor



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
    if temperature_lower_boundary < temperature:
        return False
    return True

def temperature_clamp(temperature):
    value = round(100 * (temperature - temperature_lower_boundary) / (temperature_upper_boundary - temperature_lower_boundary))
    if value < 0:
        return 0
    if 100 < value:
        return 100

    return value

R_0 = 160
G_0 = 120
B_0 = 120
R_1 = 240
G_1 = 160
B_1 = 190

def temperature_walk(DC):
    R = round(R_0 + (R_1-R_0)*DC/100)
    G = round(G_0 + (G_1-G_0)*DC/100)
    B = round(B_0 + (B_1-B_0)*DC/100)
    return f"rgb(R, G, B)"


LLLL = [ 3, 6, 9, 1, 4, 7, 10, 2, 5, 8 ]
RRRR = [ 1, 2, 2, 1, 1, 2, 2, 1, 1, 2 ]


def scfi(index):
    return (2*(index // 21) + ((index % 21) // 11) + 1, ((index % 21) % 11) + 1)

def stfi(index):
    return ((index // 5) + 1, (index % 5) + 1)


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
            eval(f"self.voltage_entry_value{indexer(index+1)}.setHtml('{3.802:.3f}V')")
        for index in range(60):
            s, t = stfi(index)
            eval(f"replace_text(self.temperature_entry_name{indexer(index+1)}, 'S{s}T{t}')")

            ni = index % 10
            nj = index // 10
            ns = RRRR[ni] + nj
            nt = LLLL[ni]
            eval(f"replace_text_label(self.segment_temp_node{indexer(index+1)}, 'S1T11', 'S{ns}T{nt}')")


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


        self.set_references()
        self.random_values()
        self.update_data()
        self.update_elements()

        #self.update_elements_callback = QTimer(self)




    def random_values(self):
        from random import randint

        for index in range(126):
            s, c = scfi(index)
            S = s // 2

            self.voltage[f's{s}v{c}'] = 3.802 + (randint(0, 100) - 50)/1000

        for index in range(60):
            s, t = stfi(index)
            S = s // 2

            self.temperature[f's{s}t{t}'] = 28.97 + (randint(0, 100) - 50)/10



    def update_data(self):
        for k in range(6):
            S = k+1
            segment = f'S{S}'
            self.voltage_segment_sum[segment] = self.voltage[f's{S}v1']
            self.voltage_segment_min[segment] = self.voltage[f's{S}v1']
            self.voltage_segment_max[segment] = self.voltage[f's{S}v1']
            self.voltage_segment_nominal[segment] = voltage_nominal(self.voltage[f's{S}v1'])
            self.temperature_segment_max[segment] = self.temperature[f's{S}t1']
            self.temperature_segment_nominal[segment] = temperature_nominal(self.temperature[f's{S}t1'])


        for k in range(12):
            s = k+1
            slave = f's{s}'
            self.voltage_slave_sum[slave] = self.voltage[f's{s}v1']
            self.voltage_slave_min[slave] = self.voltage[f's{s}v1']
            self.voltage_slave_max[slave] = self.voltage[f's{s}v1']
            self.voltage_slave_nominal[slave] = voltage_nominal(self.voltage[f's{S}v1'])
            self.temperature_slave_max[slave] = self.temperature[f's{s}t1']
            self.temperature_slave_nominal[slave] = temperature_nominal(self.temperature[f's{S}t1'])

        for index in range(60):
            s, t = stfi(index)
            S = 1 + ((s-1) // 2)

            cell = f's{s}t{t}'
            slave = f's{s}'
            segment = f'S{S}'

            if self.temperature_slave_max[slave] < self.temperature[cell]:
                self.temperature_slave_max[slave] = self.temperature[cell]
            if self.temperature_segment_max[segment] < self.temperature[cell]:
                self.temperature_segment_max[segment] = self.temperature[cell]

            self.temperature_slave_nominal[slave] = self.temperature_slave_nominal[slave] and temperature_nominal(self.temperature[cell])
            self.temperature_segment_nominal[segment] = self.temperature_segment_nominal[segment] and temperature_nominal(self.temperature[cell])


        for index in range(126):
            s, c = scfi(index)
            S = 1 + ((s-1) // 2)

            cell = f's{s}v{c}'
            slave = f's{s}'
            segment = f'S{S}'

            self.voltage_slave_sum[slave] += self.voltage[cell]
            self.voltage_segment_sum[segment] += self.voltage[cell]

            if self.voltage[cell] < self.voltage_slave_min[slave]:
                self.voltage_slave_min[slave] = self.voltage[cell]
            if self.voltage[cell] < self.voltage_segment_min[segment]:
                self.voltage_segment_min[segment] = self.voltage[cell]

            if self.voltage_slave_max[slave] < self.voltage[cell]:
                self.voltage_slave_max[slave] = self.voltage[cell]
            if self.voltage_segment_max[segment] < self.voltage[cell]:
                self.voltage_segment_max[segment] = self.voltage[cell]

            self.voltage_slave_nominal[slave] = self.voltage_slave_nominal[slave] and voltage_nominal(self.voltage[cell])
            self.voltage_segment_nominal[segment] = self.voltage_segment_nominal[segment] and voltage_nominal(self.voltage[cell])

        #self.voltage_bars = dict()
        #self.voltage_values = dict()
        #self.voltage_slave_sum_bars = dict()
        #self.voltage_slave_min_values = dict()
        #self.voltage_slave_max_values = dict()
        #self.voltage_slave_nominality = dict()
        #self.voltage_segment_sum_values = dict()
        #self.voltage_segment_sum_bars = dict()
        #self.voltage_segment_min_values = dict()
        #self.voltage_segment_max_values = dict()
        #self.voltage_segment_nominality = dict()
        #self.temperature_bars = dict()
        #self.temperature_values = dict()
        #self.temperature_indicator = dict()
        #self.temperature_slave_max_values = dict()
        #self.temperature_slave_max_bars = dict()
        #self.temperature_slave_nominality = dict()
        #self.temperature_segment_max_values = dict()
        #self.temperature_segment_max_bars = dict()
        #self.temperature_segment_nominality = dict()

        #self.voltage = dict()
        #self.voltage_slave_sum = dict()
        #self.voltage_slave_min = dict()
        #self.voltage_slave_max = dict()
        #self.voltage_slave_nominal = dict()
        #self.voltage_segment_sum = dict()
        #self.voltage_segment_min = dict()
        #self.voltage_segment_max = dict()
        #self.voltage_segment_nominal = dict()
        #self.temperature = dict()
        #self.temperature_slave_max = dict()
        #self.temperature_slave_nominal = dict()
        #self.temperature_segment_max = dict()
        #self.temperature_segment_nominal = dict()

    def update_elements(self):
        for cell in self.voltage:
            for element in self.voltage_values[cell]:
                voltage = self.voltage[cell]
                element.setText(f'{voltage:.3f}V')

            for element in self.voltage_bars[cell]:
                level = voltage_clamp(self.voltage[cell])
                element.setValue(level)

        for slave in self.voltage_slave_sum:
            for element in self.voltage_slave_sum_bars[slave]:
                level = voltage_clamp(self.voltage_slave_sum[slave] / 12)
                element.setValue(level)

        for slave in self.voltage_slave_min:
            for element in self.voltage_slave_min_values[slave]:
                voltage = self.voltage_slave_min[slave]
                element.setText(f'{voltage:.3f}V')

        for slave in self.voltage_slave_max:
            for element in self.voltage_slave_max_values[slave]:
                voltage = self.voltage_slave_max[slave]
                element.setText(f'{voltage:.3f}V')

        #for slave in self.voltage_slave_nominal:
        #   for element in self.voltage_slave_nominality[slave]:
        #       nominality = self.voltage_slave_nominal[slave]
        #       ???

        for segment in self.voltage_segment_sum:
            for element in self.voltage_segment_sum_bars[segment]:
                level = voltage_clamp(self.voltage_segment_sum[segment] / 21)
                element.setValue(level)

        for segment in self.voltage_segment_min:
            for element in self.voltage_segment_min_values[segment]:
                voltage = self.voltage_segment_min[segment]
                element.setText(f'{voltage:.3f}V')

        for segment in self.voltage_segment_max:
            for element in self.voltage_segment_max_values[segment]:
                voltage = self.voltage_segment_max[segment]
                element.setText(f'{voltage:.3f}V')

        #for segment in self.voltage_segment_nominal:
        #   for element in self.voltage_segment_nominality[segment]:
        #       nominality = self.voltage_segment_nominal[segment]
        #       ???

        for cell in self.temperature:
            for element in self.temperature_values[cell]:
                temperature = self.temperature[cell]
                element.setText(f'{temperature:.3f}C')

            for element in self.temperature_bars[cell]:
                level = temperature_clamp(self.temperature[cell])
                element.setValue(level)

            for element in self.temperature_indicator[cell]:
                level = temperature_clamp(self.temperature[cell])
                element.setValue(level)

        for slave in self.temperature_slave_max:
            for element in self.temperature_slave_max_values[slave]:
                temperature = self.temperature_slave_max[slave]
                element.setText(f'{temperature:.3f}C')

        #for slave in self.temperature_slave_nominal:
        #   for element in self.temperature_slave_nominality[slave]:
        #       nominality = self.temperature_slave_nominal[slave]
        #       ???

        for segment in self.temperature_segment_max:
            for element in self.temperature_segment_max_values[segment]:
                temperature = self.temperature_segment_max[segment]
                element.setText(f'{temperature:.3f}C')

        #for segment in self.temperature_segment_nominal:
        #   for element in self.temperature_segment_nominality[segment]:
        #       nominality = self.temperature_segment_nominal[segment]
        #       ???
        


    def set_references(self):
        for index in range(126):
            s, c = scfi(index)

            self.voltage_bars[f's{s}v{c}'] = []
            eval(f"self.voltage_bars['s{s}v{c}'].append(self.voltage_entry_bar{indexer(index+1)})")

            self.voltage_values[f's{s}v{c}'] = []
            eval(f"self.voltage_values['s{s}v{c}'].append(self.voltage_entry_value{indexer(index+1)})")


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

            self.temperature_bars[f's{s}t{t}'] = []
            eval(f"self.temperature_bars['s{s}t{t}'].append(self.temperature_entry_bar{indexer(index+1)})")

            self.temperature_values[f's{s}t{t}'] = []
            eval(f"self.temperature_values['s{s}t{t}'].append(self.temperature_entry_value{indexer(index+1)})")

        for index in range(60):
            ni = index % 10
            nj = index // 10
            s = RRRR[ni] + nj
            t = LLLL[ni]
            self.temperature_indicator[f's{s}t{t}'] = []
            eval(f"self.temperature_indicator['s{s}t{t}'].append(self.segment_temp_node{indexer(index+1)})")

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
