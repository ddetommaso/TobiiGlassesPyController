# calibrate_and_record.py : A demo code for calibrating and recording
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
from tobiiglassesctrl.controller import TobiiGlassesController

if hasattr(__builtins__, 'raw_input'):
      input=raw_input


def main():

	tobiiglasses = TobiiGlassesController()
	print(tobiiglasses.get_battery_info())
	print(tobiiglasses.get_storage_info())

	if tobiiglasses.is_recording():
		rec_id = tobiiglasses.get_current_recording_id()
		tobiiglasses.stop_recording(rec_id)

	project_name = input("Please insert the project's name: ")
	project_id = tobiiglasses.create_project(project_name)

	participant_name = input("Please insert the participant's name: ")
	participant_id = tobiiglasses.create_participant(project_id, participant_name)

	calibration_id = tobiiglasses.create_calibration(project_id, participant_id)
	input("Put the calibration marker in front of the user, then press enter to calibrate")
	tobiiglasses.start_calibration(calibration_id)

	res = tobiiglasses.wait_until_calibration_is_done(calibration_id)

	if res is False:
		print("Calibration failed!")
		exit(1)

	recording_id = tobiiglasses.create_recording(participant_id)
	print("Important! The recording will be stored in the SD folder projects/%s/recordings/%s" % (project_id, recording_id))
	input("Press enter to start recording")
	tobiiglasses.start_recording(recording_id)
	tobiiglasses.send_custom_event("start_recording", "Start of the recording ")
	input("Press enter to stop recording")
	tobiiglasses.send_custom_event("stop_recording", "Stop of the recording " + str(recording_id))
	tobiiglasses.stop_recording(recording_id)


	if res is False:
		print("Recording failed!")
		exit(1)

if __name__ == '__main__':
    main()
