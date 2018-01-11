# demo_connection.py : A demo code for connecting with the Tobii Pro Glasses 2
#
# Copyright (C) 2017  Davide De Tommaso
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

from tobiiglasses.tobiiglassescontroller import TobiiGlassesController

import sys


def main():

	tobiiglasses = TobiiGlassesController()
	#tobiiglasses = TobiiGlassesController(49152, "fe80::76fe:48ff:fe19:fbe3%18")

if __name__ == '__main__':
    main()
