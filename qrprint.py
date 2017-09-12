import pyqrcode
import pypng

text = pyqrcode.create('example')
print(text.text())
print('\n')
print(text.terminal())
##print(text.terminal(module_color='red', background='yellow'))
##print(text.terminal(module_color=5, background=123, quiet_zone=1))
