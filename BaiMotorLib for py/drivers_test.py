import BaiMotorLib as BML

if __name__ == '__main__':
    motor = BML.drivers.virtual.VirtualMotor
    sensor = BML.drivers.virtual.VirtualSensor()
    drv = BML.drivers.Driver(motor, sensor)
