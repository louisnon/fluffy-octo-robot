# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 21:53:06 2022

@author: Simon

Description:
    We use this file to analyze and visualize the data.
    In general, we'll have two images : 
        figure 1:
            - The distance between the direction of the car and the wall;
            - The speed we give the car (unit: unknown);
        figure 2:
            - The direction farthest from the wall
            - Suggested direction of the car
    By the way, we can also obtain the detailed data by putting the mouse on images

Annotation for the global variables:
    time, time_map : the absolute running time for the car.
    distance : The distance between the direction of the car and the wall (average);
    speed : The speed we give the car
    direction_raw : The direction farthest from the wall
    direction_true : The direction farthest from the wall after some treatment
    direction_sugg : Suggested direction of the car according to direction_true
    lidarMap : Real lidar data detected directly by lidar

Usage:
    Put "output.txt" in the same place
    Run this file directly
            
"""

import matplotlib.pyplot as plt
import numpy as np



time = []
time_map = []
distance = []
speed = []
direction_raw = []
direction_true = []
direction_sugg = []
lidarMap = []

# some variable for mouse interaction
text = []
po_annotation = []



# file structure for ismap=false : separate by " "
# - time stamp
# - average distance in direction 0
# - speed commend for motor
# - raw direction data detected by lidar
# - calculated direction
# - direction suggest

# file structure for ismap=true : separate by " "
# - time stamp
# - array of distance for each direction

def readFile(filename, ismap=False):
    file = open(filename)
    if not ismap:
        line = file.readline() # we skip first line which is the name of parameters
        line = file.readline()
        while line:
            try:
                line2list = line.split(" ")
                time.append(float(line2list[0]))
                distance.append(float(line2list[1]))
                speed.append(float(line2list[2]))
                direction_raw.append(float(line2list[3]))
                direction_true.append(float(line2list[4]))
                direction_sugg.append(float(line2list[5]))
            except Exception:
                break;  
            line = file.readline()

    else:
        line = file.readline() # we skip first line which is the name of parameters
        line = file.readline()
        while line:
            line2list = line.split(" ")
            try:
                time_map.append(float(line2list[0]))
                lidar=[]
                lidar.append(float(line2list[1][1:-1]))
                for i in range(357):
                    lidar.append(float(line2list[i+2][:-1]))
                lidar.append(float(line2list[360][:-2]))
                lidarMap.append(lidar)
            except Exception:
                break
            line = file.readline()
    file.close();

def find_index(xdata, oderlist, start, end):
    if int(end-start) < 2:
        return int((end+start)/2)
    if (xdata > oderlist[int((end+start)/2)]):
        return find_index(xdata, oderlist, int((end+start)/2), end)
    else:
        return find_index(xdata, oderlist, start, int((end+start)/2))
    

def plot_speed(time, distance, speed):
    fig = plt.figure()
    length = min(len(time),len(speed),len(distance))
   
    
    ax1 = fig.add_subplot(211)
    ax1.plot(time[:length-1], distance[:length-1], color='tab:blue')
    # plt.tick_params('x', labelbottom=False)
    ax1.set_title("Average distance & speed")
    
    ax1.set_ylabel("distance")
    ax1.grid(True)
    
    text1 = plt.text(length-1, distance[-1], str(distance[-1]), fontsize = 10)
    line_y = ax1.axvline(x=time[-1], color='skyblue')
    
    ax2 = fig.add_subplot(212, sharex=ax1)
    ax2.plot(time[:length-1], speed[:length-1], color='tab:orange')
    ax2.set_ylabel("speed")
    ax2.set_xlabel("time/s")
    ax2.grid(True)
    
    text2 = plt.text(length-1, speed[-1], str(speed[-1]), fontsize = 10)
    line_y2 = ax2.axvline(x=time[-1], color='skyblue')
    
    def scroll(event):
        axtemp = event.inaxes
        x_min, x_max = axtemp.get_xlim()
        scale = (x_max - x_min) / 10
        if event.button == 'up':
            axtemp.set(xlim=(x_min, x_max-scale))
        elif event.button == 'down':
            axtemp.set(xlim=(x_min, x_max+scale))
        fig.canvas.draw_idle()
    def motion(event):
        try:
            index = find_index(event.xdata, time, 0, length-1)
            temp = distance[index]
            temp2 = speed[index]

            line_y.set_xdata(event.xdata)
            line_y2.set_xdata(event.xdata)
            
            text1.set_position((event.xdata, temp))
            text1.set_text(str(temp))
            
            text2.set_position((event.xdata, temp2))
            text2.set_text(str(temp2))
            
            fig.canvas.draw_idle()
        except:
            pass
    
    
    # fig.canvas.mpl_connect('scroll_event', scroll)
    fig.canvas.mpl_connect('motion_notify_event', motion)

    plt.xlim(left=0)
    plt.show()

def plot_direction(time, dir_raw, border1, border2, sugg_dir):
    fig = plt.figure()
    length = min(len(time),len(dir_raw), len(sugg_dir))
    
    x_major_locator=plt.MultipleLocator(1)

    
    # 2 borders
    ax1 = fig.add_subplot(211)
    ax1.plot(time[:length-1], [border1 for i in range(length-1)], color='tab:blue', linewidth=0.5, ls='-')
    ax1.plot(time[:length-1], [-border1 for i in range(length-1)], color='tab:blue', linewidth=0.5, ls='-')
    ax1.plot(time[:length-1], [border2 for i in range(length-1)], color='tab:orange', linewidth=0.5, ls='-')
    ax1.plot(time[:length-1], [-border2 for i in range(length-1)], color='tab:orange', linewidth=0.5, ls='-')
    ax1.set_title("Detected direction & suggest direction")
    ax1.scatter(time, dir_raw, color='tab:red', s=1, marker='.')
    ax1.grid(axis='x')
    
    text1 = plt.text(length-1, dir_raw[-1], str(dir_raw[-1]), fontsize = 10)
    line_y = ax1.axvline(x=time[-1], color='skyblue')
    
    ax2 = fig.add_subplot(212, sharex=ax1, sharey=ax1)
    ax2.plot(time[:length-1], np.asarray(sugg_dir[:length-1])-90, color='tab:red', linewidth=1)
    ax2.grid(True)
    ax2.set_xlabel("time/s")
    fig.text(0, 0.5, 'angle/degree', va='center', rotation='vertical')
    
    text2 = plt.text(length-1, sugg_dir[-1], str(sugg_dir[-1]), fontsize = 10)
    line_y2 = ax2.axvline(x=time[-1], color='skyblue')
    
    def scroll(event):
        axtemp = event.inaxes
        x_min, x_max = axtemp.get_xlim()
        scale = (x_max - x_min) / 10
        if event.button == 'up':
            axtemp.set(xlim=(x_min, x_max-scale))
        elif event.button == 'down':
            axtemp.set(xlim=(x_min, x_max+scale))
        fig.canvas.draw_idle()
    def motion(event):
        try:
            index = find_index(event.xdata, time, 0, length-1)
            temp = dir_raw[index]
            temp2 = sugg_dir[index] - 90

            line_y.set_xdata(event.xdata)
            line_y2.set_xdata(event.xdata)
            
            text1.set_position((event.xdata, temp))
            text1.set_text(str(temp))
            
            text2.set_position((event.xdata, temp2))
            text2.set_text(str(temp2))
            
            fig.canvas.draw_idle()
        except:
            pass
    
    
    # fig.canvas.mpl_connect('scroll_event', scroll)
    fig.canvas.mpl_connect('motion_notify_event', motion)
    
    plt.ylim(-90, 90)
    plt.xlim(left=0)
    

    ax1.xaxis.set_major_locator(x_major_locator)
    

    plt.show()
    
# TODO : draw the lidar data at one moment
def print_lidar(time, lidar_data):
    return 0
    
if __name__ == "__main__":
    readFile("output.txt")
    # the relative time
    time = np.asarray(time)-time[0]
    
    plot_speed(time, distance, speed)
    plot_direction(time, direction_true, 15, 50, direction_sugg)

    
    