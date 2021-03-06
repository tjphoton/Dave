#!/usr/bin/python

import sys
import time
import threading
import math

import logger
from kinematics import Arm
from vision import Eye

if len(sys.argv) > 1 and sys.argv[1] == "debug":
    logger.log_level = logger.Level.DEBUG
else:
    logger.log_level = logger.Level.NORMAL

class Thready (threading.Thread):
    def __init__(self, id, function = None):
        threading.Thread.__init__(self)
        self.threadID = id
        self.running = True
        self.function = function

    def set_function(self, function):
        self.function = function

    def run(self):
        while self.running:
            self.function()

    def stop(self):
        self.running = False

arm = Arm()
eye = Eye()
running = True
task = "none"

def start():
    logger.log("Starting up...")
    logger.log("Stretching arm...")
    arm.reset_servos()
    time.sleep(1)
    arm.open_claw(arm.close_claw())
    logger.log("Putting on glasses...")
    eye.start()
    logger.log("Starting to listen...")
    input_thread = threading.Thread(name='input_thread', target=get_input)
    start_task("hi")
    input_thread.start()
    update()

def shutdown():
    global running
    logger.log("Shutting down...")
    running = False

def start_task(tsk):
    global task
    logger.log("Starting task: " + tsk, logger.Level.DEBUG)
    if tsk == "hi":
        logger.log("Hello!")
    elif tsk == "target":
        arm.move_to(140, 25)
    else:
        logger.error("Task '%s' does not exist" % (tsk))
        return
    task = tsk

def update():
    global task
    while running:
        if task == "hi":
            arm.open_claw()
            time.sleep(0.75)
            arm.close_claw()
            task = "none"
        elif task == "target":
            eye.look()
            target = eye.find_card()
            if target is not None:
                dist = 10
                if target[1] > dist * 10:
                    arm.move_to(arm.last_move[0], arm.last_move[1] - dist)
                elif target[1] < -dist * 10:
                    arm.move_to(arm.last_move[0], arm.last_move[1] + dist)
    logger.log("Resting arm...")
    arm.reset_servos()
    time.sleep(0.75)
    arm.rest_servos()
    time.sleep(1)
    logger.log("Goodbye!")
    logger.log("Update loop stopped", logger.Level.DEBUG)

def get_input():
    logger.log("I am ready to go!")
    while running:
        input = logger.prompt("Command?")
        command = input.split(" ")
        if len(command) == 2:
            if command[0] == "r" or command[0] == "rot" or command[0] == "rotation":
                arm.rot_servo.set_angle(float(command[1]))
            elif command[0] == "b":
                arm.b_servo.set_angle(float(command[1]))
            elif command[0] == "a":
                arm.a_servo.set_angle(float(command[1]))
            elif command[0] == "c" or command[0] == "claw":
                arm.claw_servo.set_angle(float(command[1]))
            elif command[0] == "start":
                start_task(command[1])
        elif len(command) == 3:
            if command[0] == "go" or command[0] == "move":
                arm.move_to(float(command[1]), float(command[2]))
        else:
            if command[0] == "q" or command[0] == "quit":
                shutdown()
            elif command[0] == "r" or command[0] == "reset":
                arm.reset_servos()
                logger.log("Servos reset")
            elif command[0] == "rest" or command[0] == "d" or command[0] == "disable":
                arm.rest_servos()
                logger.log("Servos set to rest")
            elif command[0] == "open":
                arm.open_claw()
                logger.log("Opening claw")
            elif command[0] == "close":
                arm.close_claw()
                logger.log("Closing claw")
            elif command[0] == "up":
                arm.b_servo.set_angle(80, arm.b_servo.rest)
            elif command[0] == "down":
                arm.b_servo.set_angle(0, arm.b_servo.rest)
            elif command[0] == "left":
                arm.rot_servo.set_angle(-80, arm.b_servo.rest)
            elif command[0] == "right":
                arm.rot_servo.set_angle(80, arm.b_servo.rest)
            elif command[0] == "back":
                arm.a_servo.set_angle(-70, arm.b_servo.rest)
            elif command[0] == "forward":
                arm.a_servo.set_angle(0, arm.b_servo.rest)
            elif command[0] == "hi" or command[0] == "hello" or command[0] == "greet":
                start_task("hi")
            else:
                logger.log("Command '%s' not recognized" % (input), logger.Level.ERROR)
    logger.log("Input thread stopped", logger.Level.DEBUG)

start()