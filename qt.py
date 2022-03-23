from PyQt5 import QtCore, QtGui, QtWidgets
import monitor


def makeHtml(text):
    return """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n<html><head><meta name="qrichtext" content="1" /><style type="text/css">\np, li { white-space: pre-wrap; }\n</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;">\n<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">""" + text + """</p></body></html>"""

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
            eval(f"replace_text_label(self.segment_temp_node{indexer(index+1)}, 'S1T11', 'S{s}T{t}')")


        # as follows are mock values
        self.voltages = dict()
        for index in range(126):
            s, c = scfi(index)
            self.voltages[f's{s}v{c}'] = 3.802

        self.temperatures = dict()
        for index in range(60):
            s, t = stfi(index)
            self.temperatures[f's{s}t{t}'] = 28.97



        # how to append elements
        self.voltage_bars = dict()
        self.voltage_values = dict()

        for index in range(126):
            s, c = scfi(index)

            self.voltage_bars[f's{s}v{c}'] = []
            eval(f"self.voltage_bars['s{s}v{c}'].append(self.voltage_entry_bar{indexer(index+1)})")

            self.voltage_values[f's{s}v{c}'] = []
            eval(f"self.voltage_values['s{s}v{c}'].append(self.voltage_entry_value{indexer(index+1)})")

        self.voltage_slave_sum_bars = dict()
        self.voltage_slave_min_values = dict()
        self.voltage_slave_max_values = dict()
        self.voltage_slave_nominality = dict()

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

        self.voltage_segment_sum_values = dict()
        self.voltage_segment_sum_bars = dict()
        self.voltage_segment_min_values = dict()
        self.voltage_segment_max_values = dict()
        self.voltage_segment_nominality = dict()

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


        self.temperature_bars = dict()
        self.temperature_values = dict()

        for index in range(60):
            s, t = stfi(index)

            self.temperature_bars[f's{s}t{t}'] = []
            eval(f"self.temperature_bars['s{s}t{t}'].append(self.temperature_entry_bar{indexer(index+1)})")

            self.temperature_values[f's{s}t{t}'] = []
            eval(f"self.temperature_values['s{s}t{t}'].append(self.temperature_entry_value{indexer(index+1)})")

        self.temperature_slave_max_values = dict()
        self.temperature_slave_max_bars = dict()
        self.temperature_slave_nominality = dict()

        for index in range(12):
            s = index + 1

            self.temperature_slave_max_bars[f's{s}'] = []
            eval(f"self.temperature_slave_max_bars['s{s}'].append(self.segment_temperature_entry_stats_A_temperature{indexer(index+1)})")

            self.temperature_slave_max_values[f's{s}'] = []
            eval(f"self.temperature_slave_max_values['s{s}'].append(self.segment_temperature_entry_stats_B_value{indexer(index+1)})")

            self.temperature_slave_nominality[f's{s}'] = []
            eval(f"self.temperature_slave_nominality['s{s}'].append(self.segment_temperature_entry_stats_A_nomality{indexer(index+1)})")

        self.temperature_segment_max_values = dict()
        self.temperature_segment_max_bars = dict()
        self.temperature_segment_nominality = dict()

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

        # how to update elements
        for cell_pair in self.voltage_values:
            for element in self.voltage_values[cell_pair]:
                voltage = self.voltages[cell_pair]
                element.setText(f'{voltage:.3f}V')




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
