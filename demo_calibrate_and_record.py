#	demo_connection.py : A demo code for connecting with the Tobii Pro Glasses 2
#
#	Copyright (C) 2017  Davide De Tommaso
#
#	This program is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; either version 2 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program. If not, see <http://www.gnu.org/licenses/>

from tobiiglasses.tobiiglassescontroller import TobiiGlassesController

import sys
import time


def main():

	tobiiglasses = TobiiGlassesController(49152)

	tobiiglasses.connect()
	time.sleep(1)


	if not tobiiglasses.is_connected():
		print("The Tobii Pro Glasses is not correctly connected!")
		exit(1)

	project_name = raw_input("Please insert the project's name: ")
	project_id = tobiiglasses.create_project(project_name)
	participant_name = raw_input("Please insert the participant's name: ")
	participant_id = tobiiglasses.create_participant(project_id, participant_name)
	calibration_id = tobiiglasses.create_calibration(project_id, participant_id)

	print "Project: " + project_id, ", Participant: ", participant_id, ", Calibration: ", calibration_id, " "


	raw_input("Put the calibration marker in front of the user, then press enter to calibrate")

	tobiiglasses.start_calibration(calibration_id)

	time.sleep(3)
	tobiiglasses.is_calibrated(calibration_id)

	recording_id = tobiiglasses.create_recording(participant_id)

	raw_input("Press enter to start recording")

	tobiiglasses.start_recording(recording_id)

	raw_input("Press enter to stop recording")

	tobiiglasses.stop_recording(recording_id)


if __name__ == '__main__':
    main()
