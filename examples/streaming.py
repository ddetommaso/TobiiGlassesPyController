# streaming.py : A demo for live streaming eye-tracker data
#
# Copyright (C) 2018  Davide De Tommaso
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>

from tobiiglassesctrl import TobiiGlassesController

import sys
import time
import json


def main():

	tobiiglasses = TobiiGlassesController()

	tobiiglasses.start_streaming()

	raw_input("Press a key to start streaming (1000 samples will be shown)")
	
	for i in range(1000):
		
		print "Head unit: %s" % tobiiglasses.get_data()['mems']
		print "Left Eye: %s " % tobiiglasses.get_data()['left_eye']
		print "Right Eye: %s " % tobiiglasses.get_data()['right_eye']
		print "Gaze Position: %s " % tobiiglasses.get_data()['gp']
		print "Gaze Position 3D: %s " % tobiiglasses.get_data()['gp3']
		
		print "PTS: %s " % tobiiglasses.get_data()['pts']
	

	tobiiglasses.stop_streaming()



if __name__ == '__main__':
    main()
