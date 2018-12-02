# connect.py : A demo code for connecting with the Tobii Pro Glasses 2
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

import sys
sys.path.append('..')

from tobiiglassesctrl import TobiiGlassesController

def main():

	TobiiGlassesController()

	"""
	other ways to connect with the tobii glasses

	TobiiGlassesController("fe80::76fe:48ff:ff00:hell%eth0") #if you know the ipv6 addr of the tobii glasses and the net interface of your host system
	TobiiGlassesController("192.168.71.50") #if you know the ipv4 addr of the tobii glasses (in case of wifi connection)
	"""


if __name__ == '__main__':
    main()
