import time
from math import atan2, degrees, cos
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
import numpy as np
import skfuzzy as fuzz
import matplotlib.pyplot as plt
#import matplotlib.pyplot as plt
#ensure gpios are clean

#create objects for each sesnor, f/b = front/back l/m/r = left/middle/right

# importing time module
import time



fl = 0
fm = 0
fr = 0
br = 0
bm = 0
bl = 0



def destroy():
    #RPi.GPIO.cleanup()
    print("\nCleaned up GPIO resources.")


def vector_2_degrees(x, y):
    angle = degrees(atan2(y, x))
    if angle < 0:
        angle += 360
    return angle


def get_heading(_sensor):
    magnet_x, magnet_y, _ = _sensor.magnetic
    return vector_2_degrees(magnet_x, magnet_y)


def setup():
    roomdeg = 100
    roomdeg = -1*roomdeg
    print("set up")
    return roomdeg


def headchange(goalhead, change):
    goalhead = goalhead + change
    if 360 <= goalhead:
        goalhead = goalhead - 360
    if goalhead < 0:
        goalhead = goalhead + 360
    return goalhead


def motors(leftcycle, rightcycle):
    print(leftcycle, rightcycle)


def loop():
    # Get the current processor time in seconds
    start_time = time.time()
    print("Current processor time (in seconds):", start_time)
    global fl,fm, fr, br, bm, bl
    fail = "bigfail"
    print("fuzzy setup")
    # Generate universe variables
    #   * Quality and leftice on subjective ranges [0, 10]
    #   * Tip has a range of [0, 25] in units of percentage points
    frontobstical = np.arange(0, 200, 1)  # 0,11,1
    leftobstical = np.arange(0, 200, 1)
    rightobstical = np.arange(0, 200, 1)
    leftmotorspeed = np.arange(0, 1, 0.1)
    rightmotorspeed = np.arange(0, 1, 0.1)

    front_lo = fuzz.trapmf(frontobstical , [0, 0,20, 100])
    front_md = fuzz.trimf(frontobstical , [50, 100, 150])
    front_hi = fuzz.trimf(frontobstical , [100, 200, 200])
    left_lo = fuzz.trapmf(leftobstical , [0, 0, 20, 100])
    left_md = fuzz.trimf(leftobstical , [50, 100, 150])
    left_hi = fuzz.trimf(leftobstical , [100, 200, 200])
    right_lo = fuzz.trapmf(rightobstical , [0, 0, 20, 100])
    right_md = fuzz.trimf(rightobstical , [50, 100, 150])
    right_hi = fuzz.trimf(rightobstical , [100, 200, 200])

    """left_slow = fuzz.trimf(leftmotorspeed, [0, 0, 50000])
    left_fast = fuzz.trimf(leftmotorspeed, [15000, 65536, 65536])
    right_slow = fuzz.trimf(rightmotorspeed, [0, 0, 50000])
    right_fast = fuzz.trimf(rightmotorspeed, [15000, 65536, 65536])"""
    left_slow = fuzz.trimf(leftmotorspeed, [0, 0, 0.3])
    left_trundle = fuzz.trimf(leftmotorspeed, [0.2, .5, 0.8])
    left_fast = fuzz.trimf(leftmotorspeed, [0.7, 1, 1])
    right_slow = fuzz.trimf(rightmotorspeed, [0, 0, 0.3])
    right_trundle = fuzz.trimf(leftmotorspeed, [0.2, .5, 0.8])
    right_fast = fuzz.trimf(rightmotorspeed, [0.7, 1, 1])

    fig, (ax0, ax1, ax2) = plt.subplots(nrows=3, figsize=(8, 9))
    plt.ylabel('Truth Value')
    plt.xlabel('Distance (cm)')
    ax0.plot(leftobstical, left_lo, 'b', linewidth=1.5, label='close')
    ax0.plot(leftobstical, left_md, 'g', linewidth=1.5, label='mid')
    ax0.plot(leftobstical, left_hi, 'r', linewidth=1.5, label='far')
    ax0.set_title('Left Obstacle Distance')

    ax0.legend()
    plt.ylabel('Truth Value')
    ax1.plot(rightobstical, right_lo, 'b', linewidth=1.5, label='close')
    ax1.plot(rightobstical, right_md, 'g', linewidth=1.5, label='mid')
    ax1.plot(rightobstical, right_hi, 'r', linewidth=1.5, label='far')
    ax1.set_title('Right Obstacle Distance (cm)')
    #ax1.ylabel('Truth Value')
    ax1.legend()
    plt.ylabel('Truth Value')
    ax2.plot(frontobstical, front_lo, 'b', linewidth=1.5, label='close')
    ax2.plot(frontobstical, front_md, 'g', linewidth=1.5, label='mid')
    ax2.plot(frontobstical, front_hi, 'r', linewidth=1.5, label='far')
    ax2.set_title('Front Obstacle Distance (cm)')
    #ax2.ylabel('Truth Value')
    ax2.legend()

    # Turn off top/right axes
    for ax in (ax0, ax1, ax2):
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()

    plt.tight_layout()
    #plt.show()  # show plots
    oldtime=0
    while True:

        pro_time = ( - oldtime)
        #oldtimtime.time()
        print("Current processor time (in seconds):", pro_time)
        print("fl, then fr")
        fl = input()
        #fm = input()
        fr = input()
        print("fl: ", fl, "fm: ", fm, "fr: ", fr, "bl: ", bl, "bm:", bm, "br:", br)
        #print("membership, load sensor readings into membership function")
        leftobsticalclose = fuzz.interp_membership(leftobstical  , left_lo, fl)
        leftobsticalmid = fuzz.interp_membership(leftobstical  , left_md, fl)
        leftobsticalfar = fuzz.interp_membership(leftobstical  , left_hi, fl)

        rightobsticalclose = fuzz.interp_membership(rightobstical  , right_lo, fr)
        rightobsticalmid = fuzz.interp_membership(rightobstical  , right_md, fr)
        rightobsticalfar = fuzz.interp_membership(rightobstical  , right_hi, fr)

        frontobsticalclose = fuzz.interp_membership(frontobstical, front_lo, fm)
        frontobsticalmid = fuzz.interp_membership(frontobstical, front_md, fm)
        frontobsticalfar = fuzz.interp_membership(frontobstical, front_hi, fm)
        #print("rules")
        # The OR operator means we take the maximum of these two.
        #active_rule1 = np.fmax(leftobsticalclose, frontobsticalclose)
        # Now we apply this by clipping the top off the corresponding output
        # membership function with `np.fmin`
        #map left obsticals to right speeds
        right_activation_close = np.fmin(leftobsticalclose, right_slow) # if left or middle obstcial close, righ motor slow

        #active_rule2 = np.fmax(leftobsticalmid, frontobsticalmid)# if left obstical or front obstical close
        right_activation_md = np.fmin(leftobsticalmid, right_trundle)# right motor slow

        #active_rule3 = np.fmin(leftobsticalfar, frontobsticalfar)# if left and front obstical far, right motor fast
        right_activation_far = np.fmin(leftobsticalfar, right_fast)

        #map right obsticals to left speeds
        left_activation_close = np.fmin(rightobsticalclose, left_slow)
        left_activation_md = np.fmin(rightobsticalmid, left_trundle)
        left_activation_far = np.fmin(rightobsticalfar, left_fast)

        right0 = np.zeros_like(rightmotorspeed)
        left0 = np.zeros_like(leftmotorspeed)

        #print("defuzzy")
        #defuzzy
        aggregatedleft =np.fmax(left_activation_close, np.fmax(left_activation_md, left_activation_far))
        leftcrispspeed = fuzz.defuzz(leftmotorspeed, aggregatedleft, 'centroid')
        left_activation = fuzz.interp_membership(leftmotorspeed, aggregatedleft, leftcrispspeed)  # for plot

        aggregatedright =np.fmax(right_activation_close, np.fmax(right_activation_md, right_activation_far))
        rightcrispspeed = fuzz.defuzz(rightmotorspeed, aggregatedright, 'centroid')
        right_activation = fuzz.interp_membership(rightmotorspeed, aggregatedright, rightcrispspeed)  # for plot

        motors(rightcrispspeed, leftcrispspeed)

        #plot defuzzy

        fig, ax0 = plt.subplots(figsize=(8, 3))

        ax0.plot(leftmotorspeed, left_slow, 'b', linewidth=0.5, linestyle='--', )
        ax0.plot(leftmotorspeed, left_trundle, 'b', linewidth=0.5, linestyle='--', )
        ax0.plot(leftmotorspeed, left_fast, 'g', linewidth=0.5, linestyle='--')

        ax0.fill_between(leftmotorspeed, left0, aggregatedleft, facecolor='Orange', alpha=0.7)
        ax0.plot([leftcrispspeed, leftcrispspeed], [0, left_activation], 'k', linewidth=1.5, alpha=0.9)
        ax0.set_title('Aggregated membership and result (line) for Left Motor Speed')

        # Turn off top/right axes
        for ax in (ax1,):
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.get_xaxis().tick_bottom()
            ax.get_yaxis().tick_left()
        #right defuzzy
        fig, ax1 = plt.subplots(figsize=(8, 3))

        ax1.plot(rightmotorspeed, right_slow, 'b', linewidth=0.5, linestyle='--', )
        ax1.plot(rightmotorspeed, right_trundle, 'b', linewidth=0.5, linestyle='--', )
        ax1.plot(rightmotorspeed, right_fast, 'g', linewidth=0.5, linestyle='--')

        ax1.fill_between(rightmotorspeed, right0, aggregatedright, facecolor='Orange', alpha=0.7)
        ax1.plot([rightcrispspeed, rightcrispspeed], [0, right_activation], 'k', linewidth=1.5, alpha=.5)#aplpha = 0.9
        ax1.set_title('Aggregated membership and result (line) for Right Motor Speed')

        # Turn off top/right axes
        for ax in (ax1,):
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.get_xaxis().tick_bottom()
            ax.get_yaxis().tick_left()
        plt.tight_layout()
        oldtime = pro_time
        plt.show()  # show plots



if __name__ == '__main__':
    #print("go!")
    #setup()
    #print("setup")
    try:
        #print("try loop!")
        loop()
        #print("exit loop?")
    except KeyboardInterrupt:
       # print("destroy")
        destroy()
        print("destroyed!")

