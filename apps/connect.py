# connect.py : A demo code for connecting with the Tobii Pro Glasses 2
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

from tobiiglassesctrl import TobiiGlassesController

def main():

	"""
	How to connect with the tobii glasses

	0. Automatic discovery of the device

	TobiiGlassesController()

	1. If you know the IPv6 addr of the tobii glasses

	TobiiGlassesController("fe80::76fe:48ff:ff00:hell")

	2. If you know the IPv6 addr of the tobii glasses and the net interface
	   of your host system (in case of multiple interfaces)

	TobiiGlassesController("fe80::76fe:48ff:ff00:ff00%eth0")

	3. If you know the IPv4 addr of the tobii glasses (WLAN or LAN connections)

	TobiiGlassesController("192.168.71.50")
	"""

	TobiiGlassesController()


if __name__ == '__main__':
    main()
