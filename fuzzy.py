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


def trimf(x, points):
    pointA = points[0]
    pointB = points[1]
    pointC = points[2]
    slopeAB = getSlope(pointA, 0, pointB, 1)
    slopeBC = getSlope(pointB, 1, pointC, 0)
    result = 0
    if pointA <= x <= pointB:
        result = slopeAB * x + getYIntercept(pointA, 0, pointB, 1)
    elif pointB <= x <= pointC:
        result = slopeBC * x + getYIntercept(pointB, 1, pointC, 0)
    return result


def fuzzifyErrorNeg(error):
    return trimf(error, [-5, -5, 0])

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


if __name__ == "__main__":
    main()

