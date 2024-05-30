import json
from bezier import Curve
from numpy import linalg
import numpy as np
import skfuzzy as fz
import copy


# Утилитарные функции
def angle(v):
    return np.arctan2(v[1], v[0])


def unitVector(v):
    return v / linalg.norm(v)


def orthogonalVector(v):
    return np.array([-v[1], v[0]])


def rotate(v, angle):
    cos = np.cos(angle)
    sin = np.sin(angle)
    rotationMatrix = np.array([[cos, -sin], [sin, cos]])
    return np.matmul(rotationMatrix, v)


def requestPointToNPPoint(p):
    return np.array([[p["x"]], [p["y"]]], np.float64)


def npPointToResponsePoint(p):
    return {"x": p[0, 0], "y": p[1, 0]}


def npPointsToCurves(curvesBasisPoints, maxPerCurvePointsCount):
    if curvesBasisPoints.size == 0:
        return []

    result = [Curve.from_nodes(curvesBasisPoints[:, :maxPerCurvePointsCount])]
    result.extend(
        npPointsToCurves(
            curvesBasisPoints[:, maxPerCurvePointsCount - 1 :], maxPerCurvePointsCount
        )
    )
    return result


_defaultAngleLimit = np.pi / 36


# Классы контроллеров
class Proportional:
    def __init__(self, coeff, angleLimit=_defaultAngleLimit):
        self._coeff = coeff
        self._angleLimit = angleLimit

    def rotationAngle(self, missile):
        return np.clip(
            self._coeff * missile._approachVelocity * missile._sightAngleDelta,
            -self._angleLimit,
            self._angleLimit,
        )


class Fuzzy:
    def __init__(self, inferenceMethod, defuzzMethod, angleLimit=_defaultAngleLimit):
        self._angleLimit = angleLimit
        self._defineUniversalSets()
        self._defineMemberFunctions()
        # Дополнительная логика инициализации

    def _defineUniversalSets(self):
        # Логика определения универсальных множеств
        pass

    def _defineMemberFunctions(self):
        # Логика определения функций принадлежности
        pass


# Класс ракеты
class Missile:
    def __init__(self):
        self.stepsCount = 0
        self.launchPoint = None
        self.startVelocity = None
        self.controller = None
        self.hasHit = False

    def copy(self):
        return copy.deepcopy(self)

    def trajectory(self, aircraftTrajectory):
        # Логика расчета траектории ракеты
        trajectory = np.zeros((2, self.stepsCount))
        for i in range(self.stepsCount):
            # Пример расчета траектории (здесь должна быть реальная логика)
            trajectory[:, i] = (
                self.launchPoint.flatten() + i * self.startVelocity.flatten()
            )
        return trajectory


# Основной класс генератора траекторий
class TrajectoryGenerator:
    def __init__(self, requestFileName, responseFileName):
        self._request = json.load(open(requestFileName))
        self._response = {}

        self._stepsCount = self._request["StepsCount"]
        self._aircraftTrajectory = None

        self._genAircraft()
        self._genMissiles()

        json.dump(self._response, open(responseFileName, "w"))

    def _genAircraft(self):
        curvesBasisPoints = np.hstack(
            tuple(map(requestPointToNPPoint, self._request["AircraftPoints"]))
        )

        at = calculateAircraftTrajectory(curvesBasisPoints, self._stepsCount)
        self._response = {
            "AircraftTrajectory": list(
                map(npPointToResponsePoint, np.hsplit(at, np.shape(at)[1]))
            )
        }
        self._aircraftTrajectory = at

    def _genMissiles(self):
        settings = self._request["Missiles"]

        usual = Missile()
        usual.stepsCount = self._stepsCount
        usual.launchPoint = requestPointToNPPoint(settings["LaunchPoint"])
        direction = requestPointToNPPoint(settings["Direction"]) - usual.launchPoint
        usual.startVelocity = unitVector(direction) * settings["VelocityModule"]
        usual.controller = Proportional(settings["PropCoeff"])

        fuzzy = usual.copy()
        fuzzy.controller = Fuzzy(settings["Inference"], settings["Defuzzification"])

        ut = usual.trajectory(self._aircraftTrajectory)
        ut = list(map(npPointToResponsePoint, np.hsplit(ut, np.shape(ut)[1])))
        self._response["UsualMissile"] = {"Trajectory": ut, "IsHit": usual.hasHit}

        ft = fuzzy.trajectory(self._aircraftTrajectory)
        ft = list(map(npPointToResponsePoint, np.hsplit(ft, np.shape(ft)[1])))
        self._response["FuzzyMissile"] = {"Trajectory": ft, "IsHit": fuzzy.hasHit}


# Функция расчета траектории самолета
def calculateAircraftTrajectory(curvesBasisPoints, stepsCount):
    curves = npPointsToCurves(
        curvesBasisPoints, 3
    )  # тут можно поменять на 2 и линии будут кривыми

    evaluate = lambda curve: curve.evaluate_multi(
        np.linspace(0.0, 1.0, stepsCount // len(curves))
    )

    t = np.hstack(tuple(map(evaluate, curves)))
    return t


if __name__ == '__main__':
    TrajectoryGenerator("ImitationRequest.json", "ImitationResponse.json")
    print("Успешно сгенерировано!")
