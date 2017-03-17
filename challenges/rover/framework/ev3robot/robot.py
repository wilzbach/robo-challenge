# -*- coding: utf-8 -*-
import logging
import ev3dev.ev3 as ev3
import common
import operator


class Robot:
    """
    The ev3dev robot (Lego Mindstorms).
    """

    DEFAULT_SPEED = 100
    MIN_ROTATION_SPEED = 5
    ROTATION_EXPONENTIAL_SLOWDOWN_ANGLE_PERCENTAGE = 2 / 3
    ROTATION_EXPONENTIAL_SLOWDOWN_RIGHT_SPEED_PERCENTAGE = 0.5
    ROTATION_EXPONENTIAL_SLOWDOWN_LEFT_SPEED_PERCENTAGE = 0.5

    MAX_DIST = 5000
    MIN_DIST = 0
    MAX_ANGLE = 360
    MIN_ANGLE = 0

    def __init__(self):
        """
        Initialize the ev3dev robot
        """

        right_motor = ev3.LargeMotor('outA')
        logging.info("motor right connected: %s" % str(right_motor.connected))

        left_motor = ev3.LargeMotor('outB')
        logging.info("motor left connected: %s" % str(right_motor.connected))

        right_motor.reset()
        left_motor.reset()

        gyro_sensor = ev3.GyroSensor()
        logging.info("gyro sensor connected: %s" % str(gyro_sensor.connected))
        gyro_sensor.mode = 'GYRO-ANG'

        gyro_sensor.mode = 'GYRO-G&A'

        self.gyro_sensor = gyro_sensor

        self.motors = [left_motor, right_motor]
        self.right_motor = right_motor
        self.left_motor = left_motor
        self.speed = self.DEFAULT_SPEED

    def reset(self):
        """
        Resets the robot to the default state (right / left motor and gyro sesor)
        :return:
        """
        self.right_motor.reset()
        self.left_motor.reset()
        self.gyro_sensor.mode = 'GYRO-ANG'
        self.gyro_sensor.mode = 'GYRO-G&A'
        self.speed = self.DEFAULT_SPEED

    @common.check_int
    @common.max(MAX_DIST)
    @common.min(MIN_DIST)
    def forward(self, distance):
        """
        Move the robot forward by a given distance.
        :param distance: the distance the robot should move forward.
        :return: None
        """
        self.stop()
        for m in self.motors:
            m.run_to_rel_pos(position_sp=distance, speed_sp=self.DEFAULT_SPEED)

    @common.check_int
    @common.max(MAX_DIST)
    @common.min(MIN_DIST)
    def backward(self, distance):
        """
        Move the robot backward by a given distance.
        :param distance: the distance the robot should move backward.
        :return: None
        """
        self.stop()
        for m in self.motors:
            m.run_to_rel_pos(position_sp=-distance, speed_sp=self.DEFAULT_SPEED)

    @common.check_int
    @common.max(MAX_ANGLE)
    @common.min(MIN_ANGLE)
    def right(self, angle):
        """
        Turn the robot right by a given angle (degrees).
        :param angle: the angle in degrees.
        :return: None
        """
        self.right_motor.speed_sp = -round(self.speed / 2)
        self.left_motor.speed_sp = round(self.speed / 2)

        self._exponential_slowdown_rotation(angle, operator.lt, operator.plus)

    @common.check_int
    @common.max(MAX_ANGLE)
    @common.min(MIN_ANGLE)
    def left(self, angle):
        """
        Turn the robot left by a given angle (degrees).
        :param angle: the angle in degrees.
        :return: None
        """
        self.right_motor.speed_sp = round(self.speed / 2)
        self.left_motor.speed_sp = -round(self.speed / 2)

        self._rotation_with_exponential_slowdown(angle, operator.gt, operator.sub)

    def _rotation_with_exponential_slowdown(self, angle, comperator, arithmetic_op):
        """
        Performs an exponential slow-down during a rotation of the robot.
        :param target_angle: the angle in degrees
        :param comparator: custom comparator to check the target_angle vs. the current angle (i.e. the direction of the rotation)
        :param arithmetic_op: custom arithmetic operator between the current_angle and the target_angle based on the direction of the rotation
        :return: None
        """
        self.right_motor.run_forever()
        self.left_motor.run_forever()
        target_angle = arithmetic_op(self.gyro_sensor.value(), angle)
        while comperator(self.gyro_sensor.value(), target_angle):
            if min(abs(self.right_motor.speed_sp), abs(self.left_motor.speed_sp)) > self.MIN_ROTATION_SPEED:
                # use negative values to invert the arithmetic_op
                # ((-a) + (-b) = - (a + b)
                partial_target = -(arithmetic_op(-self.gyro_sensor.value(), -target_angle)) * self.ROTATION_EXPONENTIAL_SLOWDOWN_ANGLE_PERCENTAGE
                while comperator(self.gyro_sensor.value(), partial_target):
                    pass
                # TODO: it might be necessary to stop the motor here (?)
                self.right_motor.speed_sp *= self.ROTATION_EXPONENTIAL_SLOWDOWN_RIGHT_SPEED_PERCENTAGE
                self.left_motor.speed_sp *= self.ROTATION_EXPONENTIAL_SLOWDOWN_LEFT_SPEED_PERCENTAGE
        self.stop()

    def stop(self):
        """
        Stops the robot
        :return: None
        """
        for m in self.motors:
            m.stop()

    def state(self):
        """
        Returns the state of the robot (distance right / left motor and angle)
        :return: map {'right_motor', 'lef_motor', 'angle'} with the current values distance
        left motor, distance right motor and current angle in degrees of the robot
        """
        out = {
            'right_motor': self.right_motor.position,
            'left_motor': self.left_motor.position,
            'angle': self.gyro_sensor.value()
        }

        return out

