from screeninfo import get_monitors
for m in get_monitors():
    print(str(m))

import wmi
obj = wmi.WMI().Win32_PnPEntity(ConfigManagerErrorCode=0)

displays = [x for x in obj if 'DISPLAY' in str(x)]

for item in displays:
   print(item)
