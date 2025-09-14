# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 12:31:50 2024

@author: Kenneth Shepherd Kr
Interfaces with the TPG261 Single gauge pressure controller
"""

import serial 

CR = bytearray(b'\x0d')
LF = bytearray(b'\x0a')
ETX = bytearray(b'\x03')
ENQ = bytearray(b'\x05')
ACK = bytearray(b'\x06')
NAK = bytearray(b'\x15')

class PfeifferException(Exception):
    pass

class pfieffer_single_gauge_TPG261:
    '''Class to interface with the TPG261 pfieffer single gauge vacuum controller'''

    def __init__(self, port, baudrate=9600):
        self.ser = serial.Serial(
            port=port,  # <-- Pass port here
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1  # Add timeout to prevent hangs
        )
        self.set_filter()
        self.set_calibration_factor(1, 1)
        self.set_calibration_factor(2, 1)
        self.set_display_resolution()
        
    def get_pressure(self, gauge):
        '''Sets the pressure for Gauge 1 and returns the pressure for gauge 1'''
        messages = {
            0: 'Passed',
            1: 'Underrange',
            2: 'Overrange', 
            3: 'Sensor Error',
            4: 'Sensor off',
            5: 'No Sensor',
            6: 'ID Error'
        }
        
        # writes the pressure to gauge 1
        self.ser.write(bytearray('PR%i' %gauge, 'ascii') + CR + LF)
        line = self.ser.readline().strip()
        
        # see if the controller acknowledges
        if line != ACK:
            raise PfeifferException('Error Sending "PR%i"' %gauge)
            
        # requests the information 
        self.ser.write(ENQ)
        line = self.ser.readline().strip().decode('utf-8')
        status, value = line.split(",")
        
        status = int(status)
        if status != 0:
            print(messages[status])
               
        return messages[status], float(value)
    
    def get_gauge_type(self):
        '''Returns the gauge type for sensor 1 and sensor 2'''
        
        self.ser.write(bytearray('TID', 'ascii') + CR + LF)
        line = self.ser.readline().strip()
        
        if line != ACK:
            raise PfeifferException('Error sending "TID"')
            
        self.ser.write(ENQ)
        line = self.ser.readline().strip().decode('utf-8')
        gauge_1, gauge_2 = line.split(',')
        
        return gauge_1, gauge_2
    
    def get_calibration_factor(self):
        '''Gets the Calibration Factor'''
        self.ser.write(bytearray('CAl', 'ascii') + CR + LF)
        line = self.ser.readline()
              
        self.ser.write(ENQ)
        line = self.ser.readline().strip().decode('utf-8')
        G1_cal, G2_cal = line.split(',')
        
        return G1_cal, G2_cal
    
    def set_calibration_factor(self, gauge, cal):
        '''Changes the calibration factor for gauge 1 and guage 2'''
        if gauge == 1:
            self.ser.write(bytearray('CAL,%.3f,%.3f' %(cal, 1), 'ascii') + CR + LF)
            line = self.ser.readline().strip()
        
            if line != ACK:
                raise PfeifferException('Error sending Calibration factor')
        
            self.ser.write(ENQ)
            line = self.ser.readline().strip().decode('utf-8')
            G1_cal, G2_cal = line.split(',')
            return G1_cal
        
        if gauge == 2:
            self.ser.write(bytearray('CAL,%.3f,%.3f' %(1, cal), 'ascii') + CR + LF)
            line = self.ser.readline().strip()
        
            if line != ACK:
                raise PfeifferException('Error sending Calibration factor')
        
            self.ser.write(ENQ)
            line = self.ser.readline().strip().decode('utf-8')
            G1_cal, G2_cal = line.split(',')
            return G2_cal
    
    def set_units(self, unit=1):
        '''Changes the default units of the gauge to Torr
        units = {
            0: 'mbar/bar',
            1: 'Torr',
            2: 'Pascal'
        }
        '''
        units = {
            0: 'mbar/bar',
            1: 'Torr',
            2: 'Pascal'
        }
        
        self.ser.write(bytearray('UNI,%i' %unit, 'ascii') + CR + LF)
        line = self.ser.readline().strip()
        
        if line != ACK:
            raise PfeifferException('Error changing units')
            
        self.ser.write(ENQ)
        line = self.ser.readline().strip().decode('utf-8')
        
        return print(f'The TPG261 default units are set to {units[int(line)]}')
    
    def set_filter(self, G1=1, G2=1):
        '''Sets the filter speed of each gauge. defaulting to medium'''
        
        Filter = {
            0: 'fast',
            1: 'medium (default)',
            2: 'slow'
        }
        
        self.ser.write(bytearray('FIL,%i,%i' %(G1, G2), 'ascii') + CR + LF)
        line = self.ser.readline().strip()
        
        if line != ACK:
            raise PfeifferException('Error changing the filter speed to fast')
            
        self.ser.write(ENQ)
        line = self.ser.readline().strip().decode('utf-8')
        gauge1, gauge2 = line.split(',')
        
        return print(f'The TPG261 Filter speed for Gauge 1 is {Filter[int(gauge1)]} and for Gauge 2 is {Filter[int(gauge2)]}')
    
    def set_display_resolution(self):
        '''Sets the default display resolution according to the values below. 
            resolution = {
                2: '2 digits',
                3: '3 digits'
                }
            '''
        Resolution = {
                2: '2 digits',
                3: '3 digits'
                }
            
        resolution = 3
            
        self.ser.write(bytearray('DCD,%i' %resolution, 'ascii') + CR + LF)
        line = self.ser.readline().strip()
        
        if line !=ACK:
            raise PfeifferException('Error in changing the display resolution')
        
        self.ser.write(ENQ)
        res = self.ser.readline().strip().decode('utf-8')
        
        return print(f'The display resolution has been set to {Resolution[int(res)]} digits.')
        
            
    def close(self):
        self.ser.close()