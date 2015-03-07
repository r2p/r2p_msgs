#!/usr/bin/env python
"""
Robocom teleoperator node
"""

import sys, os, time

import roslib
import rospy
from sensor_msgs.msg import Joy
from r2p.msg import Velocity

topic = rospy.get_param('topic', 'robot')
setpoint_scale = rospy.get_param('setpoint_scale', {'x': 1, 'y': 1, 'w': 1})
gear_ratio = rospy.get_param('gear_ratio', (
	{'x': 0.25, 'y': 0.25, 'w': 0.25},
	{'x': 0.5, 'y': 0.5, 'w': 0.5},
	{'x': 0.75, 'y': 0.75, 'w': 0.75},
	{'x': 1, 'y': 1, 'w': 1}
))

setpoint = {'x': 0.0,'y': 0.0,'w': 0.0}
gear = 0
restart = False

def joy_cb(msg):
	global gear
	global setpoint
	global restart

	if msg.buttons[6]:
		restart = True
	if msg.buttons[3]:
		gear = 3
	if msg.buttons[2]:
		gear = 2
	if msg.buttons[1]:
		gear = 1
	if msg.buttons[0]:
		gear = 0

	setpoint['x'] = msg.axes[1] * setpoint_scale['x'] * gear_ratio[gear]['x']
	setpoint['y'] = msg.axes[0] * setpoint_scale['y'] * gear_ratio[gear]['y']
	setpoint['w'] = msg.axes[3] * setpoint_scale['w'] * gear_ratio[gear]['w']
	
def main():
	global restart
	
	# Initialize ROS stuff
	rospy.init_node("teleop_joy")
	r = rospy.Rate(20) # 20hz
	
	pubVelocity = rospy.Publisher(topic, Velocity)
	pubVelocity.publish(Velocity(0.0, 0.0, 0.0))
	
	subJoy = rospy.Subscriber("/joy", Joy, joy_cb)
	
	while not rospy.is_shutdown():
		if restart == True: 
			pubVelocity.unregister()
			rospy.sleep(1)
		        pubVelocity = rospy.Publisher(topic, Velocity)
		        pubVelocity.publish(Velocity(0.0, 0.0, 0.0))
			restart = False
			
		print setpoint
		pubVelocity.publish(Velocity(setpoint['x'], setpoint['y'], setpoint['w']))
		r.sleep()

	# Stop the robot
	pubVelocity.publish(Velocity(0.0, 0.0, 0.0))


# Call the 'main' function when this script is executed
if __name__ == "__main__":
	try: main()
	except rospy.ROSInterruptException: pass

