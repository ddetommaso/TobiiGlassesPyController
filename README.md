# A Python controller for Tobii Pro Glasses 2

A Python controller for accessing eye-tracker data and managing recordings,
participants and calibrations using the wearable Tobii Pro Glasses 2.
The code is based on the Tobii Pro Glasses 2 APIs available at:

https://www.tobiipro.com/product-listing/tobii-pro-glasses-2-sdk/

This project is available on Github at:

https://github.com/ddetommaso/tobiiglasses-controller.git


## 1. Install/Uninstall the package

### 1.1 Install the controller using sources
```
git clone --recursive https://github.com/ddetommaso/tobiiglasses-controller.git
cd tobiiglasses-controller
```

```
python setup.py install (for Python 2.7)
```
or

```
python3 setup.py install (for Python 3.5)
```

### 1.2 Install the controller using pip

```
python -m pip install --upgrade tobiiglassesctrl (for Python 2.7)
```

or

```
python3 -m pip install --upgrade tobiiglassesctrl (for Python 3.5)
```

### 2. Uninstall the controller using pip

```
python -m pip uninstall tobiiglassesctrl (for Python 2.7)
```

or

```
python3 -m pip uninstall tobiiglassesctrl (for Python 3.5)
```

## 3. Update the pip package to pypi.org

```
python setup.py sdist
twine upload dist/*
```

## 4. Tobii Pro Glasses 2 Connection

Connect the glasses through Wifi or Ethernet connection. You have 3 methods to
connect with the device.

### 4.1 Network discovery

```
tobiiglasses = TobiiGlassesController()
```

If you do not pass any parameter to the constructor, a set of discovery packets
will be sent through all the network interfaces of your system waiting for an
answer from the glasses.


### 4.2 Wifi connection

```
tobiiglasses = TobiiGlassesController("192.168.71.50")
```

Once a wireless connection with the glasses is established you can run the
controller providing the IPv4 address to the constructor.


### 4.3 Ethernet connection

You can use both IPv4 or IPv6. In case you are using IPv4, ensure to have
a DHCP server running in your machine. In case of IPv6, ensure that the network
is configured as link-local.

```
tobiiglasses = TobiiGlassesController("fe80::76fe:48ff:ff00:hell")
```

In case you have multiple network interfaces in your system, please specify
the network interface-name when you create a TobiiGlassesController object:

For Linux systems you should specify the name of the net interface ...

```
tobiiglasses = TobiiGlassesController("fe80::76fe:48ff:ff00:ff00%eth0")
```

For Windows systems you should specify the net interface index

```
tobiiglasses = TobiiGlassesController("fe80::76fe:48ff:ff00:ff00%7")
```


## 5. Python Examples

Python examples are available in the examples folder of the tobiiglasses-controller

```
git clone --recursive https://github.com/ddetommaso/tobiiglasses-controller.git
cd tobiiglasses-controller/examples
```
