from machine import Pin, I2C
from lib.oled import Write, GFX, SSD1306_I2C
from lib.oled.fonts import ubuntu_mono_15, ubuntu_mono_20
import utime

# Expected instrument behaviour:
# Run will be switched on, B cartridge output will be triggered during cleaning cycles
# When cleaning is done B will be switched off and A will start the first cycle
# After *init_cycles* cycles (default=4, ending on channel B) the channel will be switched to A and the perm process begins
# After the initial perm they then occur every *post_cycles* cycles (default=135), alternating channels
# This will be interrupted at some point by a calibration which will turn the RUN signal OFF
# Run will turn back on after and the process will repeat

# This program also has a calibration request function and a master switch to enable the script

# Pico Outputs (Tekran inputs)
# Event 1 - to signify in raw data output that a standard edition run was started
# Perm source on - to start std ed. Hold on for 120s
# Will turn on Pico LED when run is ON
pinEvent = Pin(26, Pin.OUT) # Output for instrument to use
pinPermOn = Pin(20, Pin.OUT) # Output for instrument to use
pinCalSend = Pin(18, Pin.OUT) # Output for instrument to use
pinBOn = Pin(16, Pin.OUT) # Output for human use, to see if B channel is ON
pinRunOn = Pin(25, Pin.OUT) # Output for human use, to see if RUN is ON
pinBOn.high(), pinEvent.high(), pinPermOn.high(), pinRunOn.low(), pinCalSend.high() # Set initial output vals to high

# Pico Inputs (Tekran outputs)
# Run pin - signifies if instrument is running a cycle (a or b)
# Cartridge B flag - signifies instrument running a B cycle
# Source ON - an output that verifies that the source is on
# Also has constant 5V power and ground
pinRun = Pin(3, Pin.IN, Pin.PULL_UP) # Run input from instrument
pinB = Pin(8, Pin.IN, Pin.PULL_UP) # B channel input from instrument
pinSrcFlag = Pin(12, Pin.IN, Pin.PULL_UP) # Perm source confirmation from instrument
pinMaster = Pin(15, Pin.IN, Pin.PULL_UP) # Master switch for enabling the entire loop
pinCalreq = Pin(6, Pin.IN, Pin.PULL_UP) # Calibration request switch

# OLED Display Initialisation.
# Note: ssd1306 library passed a default OLED address of 0x3C, needed to find real address with i2c.scan() and change to 0x3D
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)
sz15 = Write(oled, ubuntu_mono_15)
sz20 = Write(oled, ubuntu_mono_20)
oled.fill(0)
oled.show()

# VARIABLES
cycleCounter = 0
permCounter = 0
oddEven = 0
currentCycle = None
cleaningProcess = False
msgSent = False
finalCycle = False
initCycleDone = False
calRequested = False
runMsg = False


def tekran_params(settings_file):
    global init_cycles, perm_delay, perm_time, post_cycles
    path = settings_file
    settings = open(path)

    # Default settings
    init_cycles = 4
    perm_delay = 150
    perm_time = 120
    post_cycles = 135

    lines = settings.readlines()
    
    init_cycles = int(lines[1].split()[1])
    perm_delay = int(lines[2].split()[1])
    perm_time = int(lines[3].split()[1])
    post_cycles = int(lines[4].split()[1])
    
tekran_params('file.txt')

# Master loop to enable main script
while True:
    if pinMaster.value() == 0:
        # The main script loop
        while True:
            
            # OLED displays for when MASTER is on, RUN does not have to be on
            if cleaningProcess == True:
                oled.fill(0)
                sz20.text(f'Run is ON', 0, 0)
                sz20.text(f'Cleaning...', 0, 20)
                oled.show()
            else:
                if pinRun.value() == 0:
                    oled.fill(0)
                    sz20.text(f'Cycle #: {cycleCounter}', 0, 0)
                    sz20.text(f'Channel: {currentCycle}', 0, 20)
                    sz20.text(f'Std runs: {permCounter}', 0, 40)
                    oled.show()
                else:
                    oled.fill(0)
                    sz20.text('RUN OFF', 0, 30)
                    oled.show()
            
            # Searching and cleaning part of loop
            if pinRun.value() == 0 and cycleCounter == 0:
                pinRunOn.high()
                utime.sleep(3) # Give the instrument 3 seconds for B signal to be ON signifying cleaning process
                if pinB.value() == 0:
                    pinBOn.low()
                    if cleaningProcess == False:
                        print('Run signal on, waiting for cleaning to finish')
                    cleaningProcess = True
                if pinB.value() == 1:
                    pinBOn.high()
                    if cleaningProcess == True:
                        cleaningProcess = False
                        cycleCounter = 1
                        print('Run signal on, cleaning has finished')
                        
            # Counting part of loop 
            if pinRun.value() == 0 and cycleCounter > 0:
                
                # Change from A to B
                if cycleCounter % 2 != oddEven and pinB.value() == 0:
                    utime.sleep(0.2)
                    cycleCounter += 1
                    pinBOn.low()
                    msgSent = False
                    if cycleCounter < init_cycles+1:
                        print('Cycle changing from A to B')
                    elif initCycleDone == True and cycleCounter < post_cycles:
                        print('Cycle changing from A to B')
                # Change from B to A
                if cycleCounter % 2 == oddEven and pinB.value() == 1:
                    utime.sleep(0.2)
                    cycleCounter += 1
                    pinBOn.high()
                    msgSent = False
                    if cycleCounter < init_cycles+1:
                        print('Cycle changing from B to A')
                    elif initCycleDone == True and cycleCounter < post_cycles:
                        print('Cycle changing from B to A')
                # Send cycle counter 
                if msgSent == False and cycleCounter < init_cycles+1 or msgSent == False and initCycleDone == True and cycleCounter < post_cycles:
                        if pinB.value() == 0:
                            currentCycle = 'B'
                        elif pinB.value() == 1:
                            currentCycle = 'A'
                        print('Currently in cycle {}'.format(currentCycle))
                        print('Cycle number {}'.format(cycleCounter))
                        msgSent = True
            
            # Add another if statement incase cal req right before scheulded perm, check for run
            if pinRun.value() == 0:
                runMsg = False
                # Channel A Perm - This will be for initial perm and subsequent odd perms
                if cycleCounter == init_cycles+1 and initCycleDone == False or cycleCounter == post_cycles and initCycleDone == True and permCounter % 2 == 0:
                    if permCounter == 0:
                        initCycleDone = True
                    permCounter += 1
                    oled.fill(0)
                    oled.show()
                    sz15.text(f'Std Ed {permCounter} (Ch A)', 0, 0)
                    print('Time delay...')
                    sz20.text('Time delay...', 0, 20)
                    oled.show()
                    utime.sleep(perm_delay) 
                    oled.fill(0)
                    oled.show()
                    sz15.text(f'Std Ed {permCounter} (Ch A)', 0, 0)
                    print('Sending event signal, perm source started in channel A')
                    sz20.text('Perm src on', 0, 20)
                    oled.show()
                    pinEvent.low()
                    pinPermOn.low()
                    utime.sleep(1) # Send signal for 1s to register event
                    pinEvent.high()
                    utime.sleep(perm_time)
                    oled.fill(0)
                    oled.show()
                    print('Perm source off, resetting count')
                    pinPermOn.high()
                    cycleCounter = 1
                    oddEven = 1
                    utime.sleep(3) # Time to switch after perm is done
                    if pinB.value() == 1: 
                        pinBOn.high()
                        oled.fill(0)
                        oled.text('Ch A still active', 0, 0)
                        oled.text('Waiting for switch...', 0, 30)
                        oled.show()
                        print('Channel A still active after A perm, waiting until it switches')
                        while pinB.value() == 1:
                            utime.sleep(3)
                            # Break out of loop should RUN be turned OFF during searching of channel change
                            if pinRun.value() == 1:
                                break
                    else:
                        pinBOn.low()
                        print('Channel has been switched to B after A perm')
                
                # Channel B Perm - This will be for even number perms
                if cycleCounter == post_cycles and initCycleDone == True and permCounter % 2 == 1:
                    permCounter += 1
                    oled.fill(0)
                    oled.show()
                    sz15.text(f'Std Ed {permCounter} (Ch B)', 0, 0)
                    print('Time delay...')
                    sz20.text('Time delay...', 0, 20)
                    oled.show()
                    utime.sleep(perm_delay)
                    oled.fill(0)
                    oled.show()
                    sz15.text(f'Std Ed {permCounter} (Ch B)', 0, 0)
                    print('Sending event signal, perm source started in channel B')
                    sz20.text('Perm src on', 0, 20)
                    oled.show()
                    pinEvent.low()
                    pinPermOn.low()
                    utime.sleep(1) # Send signal for 1s to register event
                    pinEvent.high()
                    utime.sleep(perm_time-1)
                    oled.fill(0)
                    oled.show()
                    print('Perm source off, resetting count')
                    pinPermOn.high()
                    cycleCounter = 1
                    oddEven = 0
                    utime.sleep(3) # Time to switch after perm is done
                    if pinB.value() == 0: 
                        pinBOn.low()
                        oled.fill(0)
                        oled.text('Ch B still active', 0, 0)
                        oled.text('Waiting for switch...', 0, 30)
                        oled.show()
                        print('Channel B still active after B perm, waiting until it switches')
                        while pinB.value() == 0:
                            utime.sleep(3)
                            # Break out of loop should RUN be turned OFF during searching of channel change
                            if pinRun.value() == 1:
                                break
                    else:
                        pinBOn.high()
                        print('Channel has been switched to A after B perm')
                
            # Run OFF part of loop
            elif pinRun.value() == 1:
                if runMsg == False:
                    print('Run is off')
                    runMsg = True
                pinRunOn.high()
                cycleCounter, permCounter, oddEven = 0, 0, 0
                cleaningProcess, msgSent, finalCycle, initCycleDone, calRequested = False, False, False, False, False
                if pinB.value() == 0:
                    pinBOn.low()
                    currentCycle = 'B'
                elif pinB.value() == 1:
                    pinBOn.high()
                    currentCycle = 'A'
            
            # Cal request part of loop
            if pinCalreq.value() == 0 and pinRun.value() == 0 and calRequested == False:
                oled.fill(0)
                oled.text('Cal pressed', 0, 0)
                oled.text('Confirm: Press again', 0, 20)
                oled.text('Cancel: wait 10secs', 0, 40)
                oled.show()
                print('Cal btn pressed, press again within 10s to confirm or do nothing to cancel')
                utime.sleep(3) # To stop button holding unwanted affects
                start = utime.ticks_ms()
                # This will give the user 10s to reconfirm they want to cal, if so run will turn off
                while True:
                    if pinCalreq.value() == 0:
                        pinCalSend.low()
                        oled.fill(0)
                        sz20.text('Calibration', 0, 0)
                        sz20.text('Confirmed', 0, 20)
                        print('Cal confirmed')
                        oled.show()
                        utime.sleep(1)
                        pinCalSend.high()
                        utime.sleep(2)
                        calRequested = True
                        break
                    elif utime.ticks_diff(utime.ticks_ms(), start) > 10000:
                        oled.fill(0)
                        sz20.text('Calibration', 0, 0)
                        sz20.text('Cancelled', 0, 20)
                        print('Cal cancelled')
                        oled.show()
                        utime.sleep(2)
                        break
            
            # If master switch is turned off the program will exit after it has finished what it is doing
            if pinMaster.value() == 1:
                break
        
    # Re-initialising vars when master switch is off
    cycleCounter, permCounter, oddEven = 0, 0, 0
    cleaningProcess, msgSent, finalCycle, initCycleDone, calRequested, runMsg, currentCycle = False, False, False, False, False, False, None
    oled.fill(0)
    sz20.text('Master OFF', 0, 20)
    oled.show()
    pinBOn.high(), pinEvent.high(), pinPermOn.high(), pinRunOn.low(), pinCalSend.high()

