#!/usr/bin/env python

import os



class CTS2000:
    def __init__(self,port):
        self.setting = {}
        self.transferToSettingMode = "\x1d(E\x03\x00\x01IN"
        # settingModeReply = '7 \x00'
        self.endSettingMode = "\x1d(E\x04\x00\x02OUT"
        self.fd = os.open(port, os.O_RDWR)

    def getSettings(self):
        self.getMSW()
        self.getCustomValues()
        self.getSerialParameters()

    def getMSW(self):
        msw = ['']
        #fd = os.open("/dev/usb/lp0", os.O_RDWR)
        for i in range(1,6):
            os.write(self.fd, "\x1d(E\x02\x00\x04" + chr(i))
            sw = os.read(self.fd,11)
            # This is to grab byte 2-10 from the printer output, reverse it and prepend space
            #
            # The reason i do this is because the printer outputs the settings
            # in reverse order, and the documentation documents settings like
            # MSW[1-5,7-10]-[1-8] and i like addressing MSW1-1 as msw[1][1]
            # As far as i know, this command \x1d(E\x02\x00\x04 only allows viewing MSW[1-5].
            msw.append(' ' + sw[2:10][::-1])
        msw = [' ', ' 00000000', ' 11000000', ' 00000010', ' 00100001', ' 00100100']
        # I try to use the documented setting name here:
        self.setting['PowerOnInfo']   = msw[1][1] == '1'
        self.setting['BufferSize4k']  = msw[1][2] == '1'
        self.setting['BusyCondition'] = msw[1][3] == '1'
        self.setting['ReceiveError']  = msw[1][4] == '1'
        self.setting['CRmode']        = msw[1][5] == '1'
        #
        self.setting['DSRSignal']     = msw[1][7] == '1'
        self.setting['InitSignal']    = msw[1][8] == '1'

        #reserved
        self.setting['AutoCutter']    = msw[2][2] == '1'
        self.setting['SpoolPrint']    = msw[2][3] == '1'
        self.setting['FullColPrint']  = msw[2][4] == '1'
        self.setting['ResumeaftPE']   = msw[2][5] == '1'
        #reserved
        #reserved

        self.setting['ResumCttrErr']  = msw[3][1] == '1'
        #reserved
        self.setting['Parallel31Pin'] = msw[3][3] == '1'
        #
        #
        #No use
        self.setting['CBM1000Mode']   = msw[3][7] == '1'
        self.setting['ResumOpenErr']  = msw[3][8] == '1'

        self.setting['BMMeasure']     = msw[4][1] == '1'
        #
        self.setting['FeedCutatTOF']  = msw[4][3] == '1' # feed and cut paper when cover is closed
        #
        #
        #
        #
        self.setting['Partialonly']   = msw[4][8] == '1'

        self.setting['Buzzer']        = msw[5][1] == '1'
        self.setting['LinePitch']     = 401 if msw[5][2] == '1' else 360
        self.setting['USBMode']       = 'usblp' if msw[5][3] == '1' else 'usbtty'
        #
        #
        #
        #
        #

    def getCustomValues(self):
        for a in [ 1,2,3,5,6,116,201,202 ]:
            os.write(self.fd, "\x1d(E\x02\x00\x06"+chr(a))
            sends = os.read(self.fd,12)
            # Data is returned from printer like:
            # "7'"+ string of number + \x1f ("separation number"),
            # followed by an ascii string which is the config value, terminated with \x00
            if sends[0:3+len(str(a))] == "7'"+str(a) + "\x1f":
                # a = 1: When user NV memory capacity is specified
                if a == 1:
                    self.setting['userNVmemory'] = sends[4]
                    # 1 = 1K bytes
                    # 2 = 64K bytes
                    # 3 = 128K bytes
                    # 4 = 192K bytes
                if a == 2:
                    self.setting['graphicsNVmemory'] = sends[4]
                    # 1 = 0 bytes
                    # 2 = 64K bytes
                    # 3 = 128K bytes
                    # 4 = 192K bytes
                    # 5 = 256K bytes
                    # 6 = 320K bytes
                    # 7 = 384K bytes
                if a == 3:
                    #self.setting['paperWidth'] = sends[4]
                    if sends[4] == '1':
                        self.setting['printWidth'] = 360
                    if sends[4] == '2':
                        self.setting['printWidth'] = 384
                    if sends[4] == '3':
                        self.setting['printWidth'] = 432
                    if sends[4] == '4':
                        self.setting['printWidth'] = 432
                    if sends[4] == '5':
                        self.setting['printWidth'] = 436
                    if sends[4] == '6':
                        self.setting['printWidth'] = 512
                    if sends[4] == '7':
                        self.setting['printWidth'] = 576
                    if sends[4] == '8':
                        self.setting['printWidth'] = 640
                    # 1 = 58mm
                    # 2 = 58mm
                    # 3 = 58mm
                    # 4 = 58/60mm
                    # 5 = 60mm
                    # 6 = 80mm
                    # 7 = 80mm
                    # 8 = 82.5mm
                if a == 5:
                    if len(sends) == 10:
                        value = sends[4:9]
                    else:
                        value = sends[4]
                    if value == '65530':
                        self.setting['printDensity'] = .7
                    if value == '65531':
                        self.setting['printDensity'] = .75
                    if value == '65532':
                        self.setting['printDensity'] = .8
                    if value == '65533':
                        self.setting['printDensity'] = .85
                    if value == '65534':
                        self.setting['printDensity'] = .9
                    if value == '65535':
                        self.setting['printDensity'] = .95
                    if value == '0':
                        self.setting['printDensity'] = 1
                    if value == '1':
                        self.setting['printDensity'] = 1.05
                    if value == '2':
                        self.setting['printDensity'] = 1.1
                    if value == '3':
                        self.setting['printDensity'] = 1.15
                    if value == '4':
                        self.setting['printDensity'] = 1.2
                    if value == '5':
                        self.setting['printDensity'] = 1.25
                    if value == '6':
                        self.setting['printDensity'] = 1.3
                    if value == '7':
                        self.setting['printDensity'] = 1.35
                    if value == '8':
                        self.setting['printDensity'] = 1.4
                    # 65530 = 70%
                    # 65531 = 75%
                    # 65532 = 80%
                    # 65533 = 85%
                    # 65534 = 90%
                    # 65535 = 95%
                    #     0 = Basic density
                    #     1 = 105%
                    #     2 = 110%
                    #     3 = 115%
                    #     4 = 120%
                    #     5 = 125%
                    #     6 = 130%
                    #     7 = 135%
                    #     8 = 140%
                if a == 6:
                    self.setting['printingSpeed'] = sends[4]
                    # Speed level 1-9. No more info on that.
                if a == 116:
                    self.setting['paperColors'] = sends[6]
                    # 1 = Single-color paper
                    # 2 = 2-color paper
                if a == 201:
                    self.setting['ackPosition'] = sends[6]
                    # 1'] = ACK-in-Busy
                    # 2'] = ACK-while-Busy
                    # 3'] = ACK-after-Busy
                if a == 202:
                    self.setting['bufferFullBusy'] = sends[6]
                    # Busy behaviour in case of MSW1-2 ON (Buffer size is 45 bytes)
                    #  Busy Output/Cancel
                    # 1 = 16/26
                    # 2 = 16/36 
                    # 3 =  8/26
                    # 4 =  8/36
                    # Busy behaviour in case of MSW1-2 OFF (Buffer size is 4k bytes)
                    # 1 = 128/256
                    # 2 = 128/512 
                    # 3 =  72/256
                    # 4 =  72/512
    def getSerialParameters(self):
        # Reading serial port parameters
        for a in (1,2,3,4):
            # There is also parameters 119 and 120 which seems to be not working on my printer.
            # Probably works if you install a parallel port? Who knows.
            os.write(self.fd, "\x1d(E\x02\x00\x0c"+chr(a))
            sends = os.read(self.fd,12)
            if sends[0:3+len(str(a))] == "73"+str(a) + "\x1f":
                value = sends[4:-1]
                if a == 1:
                    self.setting['serial_baud'] = value
                if a == 2:
                    if value == '0':
                        self.setting['serial_parity'] = 'no'   
                    if value == '1':
                        self.setting['serial_parity'] = 'odd'
                    if (value == '2'):
                        self.setting['serial_parity'] = 'even'
                if a == 3:
                    # Flow control, hw is DSR/DTR, sw is XON/XOFF
                    # Even when flow control is hw, it might occasionally send XON/XOFF
                    if value == '0':
                        self.setting['serial_flow_control'] = 'hw'
                    if value == '1':
                        self.setting['serial_flow_control'] = 'sw'
                if a == 4:
                    if value == '0':
                        self.setting['serial_length'] = '7'
                    if value == '1':
                        self.setting['serial_length'] = '8'
    def resetSettings(self,settings):
        resetcommand = "\x1d(E\x02\x00\xff"
        if settings == 'memoryswitch':
            os.write(self.fd, resetcommand + chr(3))
        if settings == 'customvalue':
            os.write(self.fd, resetcommand + chr(5))
        if settings == 'charcode':
            os.write(self.fd, resetcommand + chr(7))
        if settings == 'serial':
            os.write(self.fd, resetcommand + chr(11))
        if settings == 'all':
            os.write(self.fd, resetcommand + chr(255))
        self.getSettings()




