from ublox_gps import UbloxGps
from datetime import datetime
import serial
import traceback
import glob

def find_port():
    ports = glob.glob('/dev/ttyACM[0-9]*')
    res = list()
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            res.append(port)
        except:
            print(traceback.format_exc())
    return res[0]

def gps_object():
    port = serial.Serial(
        find_port(),
        baudrate = 38400,
        timeout = 1
    )
    return UbloxGps(port), port

def main():
    gps, port = gps_object()
    try:
        f = open('GPS_data_{}.csv'.format(datetime.now().strftime(
            '%Y-%m-%d_%H-%M-%S'
        )), 'w')
        f.write('Longitude,Latitude,HeadMotion,Timestamp\n')
        while True:
            geo = gps.geo_coords()
            f.write('{},{},{},{}\n'.format(
                geo.lon,
                geo.lat,
                geo.headMot,
                datetime.now()
            ))
    except:
        print(traceback.format_exc())
    finally:
        port.close()
        f.close()

if __name__ == '__main__':
    main()
