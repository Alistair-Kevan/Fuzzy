

def trimf(x, points):
    pointA = points[0]
    pointB = points[1]
    pointC = points[2]
    slopeAB = getSlope(pointA, 0, pointB, 1)
    slopeBC = getSlope(pointB, 1, pointC, 0)
    result = 0
    if x >= pointA and x <= pointB:
        result = slopeAB * x + getYIntercept(pointA, 0, pointB, 1)
    elif x >= pointB and x <= pointC:
        result = slopeBC * x + getYIntercept(pointB, 1, pointC, 0)
    return result


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


def getSlope(x1, y1, x2, y2):
    # Avoid zero division error of vertical line for shouldered trapmf
    try:
        slope = (y2 - y1) / (x2 - x1)
    except ZeroDivisionError:
        slope = 0
    return slope


def getYIntercept(x1, y1, x2, y2):
    m = getSlope(x1, y1, x2, y2)
    if y1 < y2:
        y = y2
        x = x2
    else:
        y = y1
        x = x1
    return y - m * x


def getTrimfPlots(start, end, points):
    plots = [0] * (abs(start) + abs(end))
    pointA = points[0]
    pointB = points[1]
    pointC = points[2]
    slopeAB = getSlope(pointA, 0, pointB, 1)
    slopeBC = getSlope(pointB, 1, pointC, 0)
    yInterceptAB = getYIntercept(pointA, 0, pointB, 1)
    yInterceptBC = getYIntercept(pointB, 1, pointC
                                 , 0)
    for i in range(pointA, pointB):
        plots[i] = slopeAB * i + yInterceptAB
    for i in range(pointB, pointC):
        plots[i] = slopeBC * i + yInterceptBC

    return plots


def getTrapmfPlots(start, end, points, shoulder=None):
    plots = [0] * (abs(start) + abs(end))
    pointA = points[0]
    pointB = points[1]
    pointC = points[2]
    pointD = points[3]
    left = 0
    right = 0
    slopeAB = getSlope(pointA, 0, pointB, 1)
    slopeCD = getSlope(pointC, 1, pointD, 0)
    yInterceptAB = getYIntercept(pointA, 0, pointB, 1)
    yInterceptCD = getYIntercept(pointC, 1, pointD, 0)
    if shoulder == "left":
        for i in range(start, pointA):
            plots[i] = 1
    elif shoulder == "right":
        for i in range(pointD, end):
            plots[i] = 1
    for i in range(pointA, pointB):
        plots[i] = slopeAB * i + yInterceptAB
    for i in range(pointB, pointC):
        plots[i] = 1
    for i in range(pointC, pointD):
        plots[i] = slopeCD * i + yInterceptCD
    return plots


def getCentroid(aggregatedPlots):
    n = len(aggregatedPlots)
    xAxis = list(range(n))
    centroidNum = 0
    centroidDenum = 0
    for i in range(n):
        centroidNum += xAxis[i] * aggregatedPlots[i]
        centroidDenum += aggregatedPlots[i]
    return centroidNum / centroidDenum

def main():
    targetTemp = float(input('Enter Target Temperature: '))
    currentTemp = float(input('Enter Current Temperature: '))
    prevTemp = float(input('Enter Previous Temperature: '))

    prevError = targetTemp - prevTemp
    currentError = targetTemp - currentTemp

    error = currentError
    errorDerivative = prevError - currentError

    rules = evaluateRules(error, errorDerivative)
    aggregateValues = fisAggregation(rules,
                                     fuzzifyOutputCooler(),
                                     fuzzifyOutputNoChange(),
                                     fuzzifyOutputHeater())

    centroid = getCentroid(aggregateValues)

    print(error)
    print(errorDerivative)
    print(centroid)


def evaluateRules(error, errorDerivative):
    rules = [[0] * 3 for i in range(3)]

    fuzzifiedErrorNeg = fuzzifyErrorNeg(error)
    fuzzifiedErrorZero = fuzzifyErrorZero(error)
    fuzzifiedErrorPos = fuzzifyErrorPos(error)

    fuzzifiedErrorDotNeg = fuzzifyErrorDotNeg(errorDerivative)
    fuzzifiedErrorDotZero = fuzzifyErrorDotZero(errorDerivative)
    fuzzifiedErrorDotPos = fuzzifyErrorDotPos(errorDerivative)
    # RULE 1
    rules[0][0] = min(fuzzifiedErrorNeg, fuzzifiedErrorDotNeg)
    # RULE 2
    rules[0][1] = min(fuzzifiedErrorZero, fuzzifiedErrorDotNeg)
    # RULE 3
    rules[0][2] = min(fuzzifiedErrorPos, fuzzifiedErrorDotNeg)
    # RULE 4
    rules[1][0] = min(fuzzifiedErrorNeg, fuzzifiedErrorDotZero)
    # RULE 5
    rules[1][1] = min(fuzzifiedErrorZero, fuzzifiedErrorDotZero)
    # RULE 6
    rules[1][2] = min(fuzzifiedErrorPos, fuzzifiedErrorDotZero)
    # RULE 7
    rules[2][0] = min(fuzzifiedErrorNeg, fuzzifiedErrorDotPos)
    # RULE 8
    rules[2][1] = min(fuzzifiedErrorZero, fuzzifiedErrorDotPos)
    # RULE 9
    rules[2][2] = min(fuzzifiedErrorPos, fuzzifiedErrorDotPos)
    return rules


def fuzzifyErrorPos(error):
    return trimf(error, [0, 5, 5])


def fuzzifyErrorZero(error):
    return trimf(error, [-5, 0, 5])


def fuzzifyErrorNeg(error):
    return trimf(error, [-5, -5, 0])


def fuzzifyErrorDotPos(errorDot):
    return trapmf(errorDot, [1, 1.5, 5, 5])


def fuzzifyErrorDotZero(errorDot):
    return trimf(errorDot, [-2, 0, 2])


def fuzzifyErrorDotNeg(errorDot):
    return trapmf(errorDot, [-5, -5, -1.5, -1])


def fuzzifyOutputCooler():
    return getTrapmfPlots(0, 200, [0, 0, 30, 95], "left")


def fuzzifyOutputNoChange():
    return getTrimfPlots(0, 200, [90, 100, 110])


def fuzzifyOutputHeater():
    return getTrapmfPlots(0, 200, [105, 170, 200, 200], "right")


def fisAggregation(rules, pcc, pcnc, pch):
    result = [0] * 200
    for rule in range(len(rules)):
        for i in range(200):
            if rules[rule][0] > 0 and i < 95:
                result[i] = min(rules[rule][0], pcc[i])
            if rules[rule][1] > 0 and i > 90 and i < 110:
                result[i] = min(rules[rule][1], pcnc[i])
            if rules[rule][2] > 0 and i > 105 and i < 200:
                result[i] = min(rules[rule][2], pch[i])
    return result


if __name__ == "__main__":
    main()