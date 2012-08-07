import os
import sys
lib_path = os.path.abspath('../')
sys.path.append(lib_path)

import makerbot_driver
import optparse
import serial

parser = optparse.OptionParser()
parser.add_option("-i", "--inputline", dest="input_line",
                  help="gcode line to read in", default=False)
parser.add_option("-o", "--outputfile", dest="output_file",
                  help="s3g file to write out", default=False)
parser.add_option("-p", "--serialport", dest="serialportname",
                  help="serial port (ex: /dev/ttyUSB0)", default="/dev/ttyACM0")
parser.add_option("-b", "--baud", dest="serialbaud",
                  help="serial port baud rate", default="115200")
parser.add_option("-m", "--machine", dest="machine",
                  help="the type of machine we print to", default="ReplicatorDual")
(options, args) = parser.parse_args()


s = makerbot_driver.s3g()
port = serial.Serial(options.serialportname, options.serialbaud, timeout=.2)
s.writer = makerbot_driver.Writer.StreamWriter(port)

parser = makerbot_driver.Gcode.GcodeParser()
parser.state.profile = makerbot_driver.Profile(options.machine)
parser.s3g = s

parser.execute_line(options.input_line)
