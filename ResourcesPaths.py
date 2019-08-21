
import platform

if platform.system() == 'Linux':
	mediaPath: str = "/home/pi/Documents/2/"
	sitePath: str = "/home/pi/Documents/2/site/"
elif platform.system() == 'Windows':
	mediaPath: str = "D:\\SCEXIB\\"
	sitePath: str = "D:\\SCEXIB\\site\\"
