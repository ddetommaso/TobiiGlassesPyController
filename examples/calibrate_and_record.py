# calibrate_and_record.py : A demo code for connecting with the Tobii Pro Glasses 2
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


def main():

	tobiiglasses = TobiiGlassesController()
	print tobiiglasses.get_battery_info()

	if tobiiglasses.is_recording():
		rec_id = tobiiglasses.get_current_recording_id()
		tobiiglasses.stop_recording(rec_id)

	project_name = raw_input("Please insert the project's name: ")
	project_id = tobiiglasses.create_project(project_name)

	participant_name = raw_input("Please insert the participant's name: ")
	participant_id = tobiiglasses.create_participant(project_id, participant_name)

	calibration_id = tobiiglasses.create_calibration(project_id, participant_id)
	raw_input("Put the calibration marker in front of the user, then press enter to calibrate")
	tobiiglasses.start_calibration(calibration_id)

	res = tobiiglasses.wait_until_calibration_is_done(calibration_id)

	if res is False:
		print("Calibration failed!")
		exit(1)

	recording_id = tobiiglasses.create_recording(participant_id)
	raw_input("Press enter to start recording")
	tobiiglasses.start_recording(recording_id)
	tobiiglasses.send_event("start_recording", "Start of the recording ")
	raw_input("Press enter to stop recording")
	tobiiglasses.send_event("stop_recording", "Stop of the recording " + str(recording_id))
	tobiiglasses.stop_recording(recording_id)


	if res is False:
		print("Recording failed!")
		exit(1)

if __name__ == '__main__':
    main()
