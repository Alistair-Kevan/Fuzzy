def x_far(x): #  T\ left edge shape
    fallstart = 200
    fallend = 250
    if x <= fallstart:
        return 1
    elif x >= fallend:
        return 0
    elif fallstart < x < fallend:
        return (fallend - x) / (fallend - fallstart)#falling edge


def x_mid(x): # /T\ shape in middel
    leftend =500
    fullleft = 650
    fullright = 750
    rightend = 900
    if x <= leftend:
        return 0
    elif x >= rightend:
        return 0
    elif leftend < x < fullleft:
        return (x - leftend) / (fullleft - leftend)#rising edge
    elif fullleft >= x >= fullright:
        return 1
    elif fullright < x < rightend:
        return (rightend - x) / (rightend - fullright)# falling edge


def x_close(x): # /T shape right end
    fallstart = 750
    fallend = 250
    if x >= fallstart:
        return 1
    elif x <= fallend:
        return 0
    elif fallend < x < fallstart:
        return (fallend - x) / (fallend - fallstart)#falling edge

def trapmf(x, points):
    pointA = points[0]
    pointB = points[1]
    pointC = points[2]
    pointD = points[3]
    slopeAB = getSlope(pointA, 0, pointB, 1)
    slopeCD = getSlope(pointC, 1, pointD, 0)
    yInterceptAB = getYIntercept(pointA, 0, pointB, 1)
    yInterceptCD = getYIntercept(pointC, 1, pointD, 0)
    result = 0
    if x > pointA and x < pointB:
        result = slopeAB * x + yInterceptAB
    elif x >= pointB and x <= pointC:
        result = 1
    elif x > pointC and x < pointD:
        result = slopeCD * x + yInterceptCD
    return result