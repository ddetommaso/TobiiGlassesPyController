# streaming.py : A demo for data streaming
#
# Copyright (C) 2019  Davide De Tommaso
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>

import time
import json
from tobiiglassesctrl import TobiiGlassesController


def main():

	tobiiglasses = TobiiGlassesController("192.168.71.50")
	print(tobiiglasses.get_battery_status())

	tobiiglasses.start_streaming()
	print("Please wait ...")
	time.sleep(3.0)

	for i in range(1000):
		print("Head unit: %s" % tobiiglasses.get_data()['mems'])
		print("Left Eye: %s " % tobiiglasses.get_data()['left_eye'])
		print("Right Eye: %s " % tobiiglasses.get_data()['right_eye'])
		print("Gaze Position: %s " % tobiiglasses.get_data()['gp'])
		print("Gaze Position 3D: %s " % tobiiglasses.get_data()['gp3'])

	tobiiglasses.stop_streaming()
	tobiiglasses.close()



if __name__ == '__main__':
    main()
