from enum import Enum
from Area import *


# different health states as enum

class Health(Enum):
    HEALTHY = 'healthy'  # susceptible
    INFECTED = 'infected'  # no symptoms but infectious
    SICK = 'sick'  # symptoms and infectious
    CRITICAL = 'critical'  # use as hospitalized or NCU etc
    RECOVERED = 'recovered'  # -> immune, not infectious
    DEAD = 'dead'  # -> immune :(, not infectious


"""
This class saves all the data we need to know about a person for our simulation
It counts person objects and gives a corresponding ID to each person

variables include a name, id, speed and current location, target location and several health stats

methods include "health setters", movement, a roll for dieing, getColor for a color corresponding to health status

"""


class Person:
    # static counter to easily keep track of person ID's
    id = 0

    def __init__(self, currentLocation: Location, speed=2):
        self.id = Person.id
        Person.id = Person.id + 1
        self.name = "Person number" + str(self.id)

        # movement related stuff
        self.speed = speed  # distance Person can move in one cycle
        self.currentLocation = Location(currentLocation.x, currentLocation.y, currentLocation.area)
        # initializing random target
        self.target = randomLocation(self.currentLocation.area)

        # health related stuff
        self.health = Health.HEALTHY
        self.isolating = False
        self.infectious = False
        self.immune = False
        self.daysUntilRecovered = -1  # initially not recovering since healthy

    # just a simple string representation for more beautiful logs
    def __str__(self):
        return "Person " + str(self.id)

    def fullPrint(self):
        return "Person " + str(self.id) + " at Position " + str(self.currentLocation) + " with health status: " + str(
            self.health.value)

    # calculates the next move
    def deltaXY(self, xLimit=0, yLimit=0):
        x, y = self.target.x, self.target.y # just for readability

        # just to catch errors, not really needed
        if (xLimit, yLimit) == (0, 0):
            xLimit, yLimit = self.currentLocation.area.xlimit, self.currentLocation.area.ylimit

        # calculates distance between current location and target
        distance = self.currentLocation.getDistance(x, y)
        #if isolating -> dont move
        if self.isolating:
            deltaX = 0
            deltaY = 0
        # if close to the close to the border get new target
        elif self.currentLocation.x > .9 * xLimit or self.currentLocation.y > .9 * yLimit:
            self.setTarget(randomLocation(self.currentLocation.area))
            deltaX = (x - self.currentLocation.x) / distance * self.speed
            deltaY = (y - self.currentLocation.y) / distance * self.speed

        # else just go "speed" distance towards current target
        else:
            deltaX = (x - self.currentLocation.x) / distance * self.speed
            deltaY = (y - self.currentLocation.y) / distance * self.speed

        return deltaX, deltaY

    # checks whether a target is in the current area
    def isMoveLegit(self, x, y):

        if self.currentLocation.area.xlimit > self.currentLocation.x + x > 0 \
                and 0 < self.currentLocation.y + y < self.currentLocation.area.ylimit:
            return True
        return False

    # moves if goal is in current area, else raises exception
    def move(self, deltaX, deltaY):
        if self.isMoveLegit(deltaX, deltaY):
            self.currentLocation.x += deltaX
            self.currentLocation.y += deltaY
        else:
            print("DelXY to big probs")
            raise Exception

    # update target location
    def setTarget(self, target: Location):
        self.target = target.getCopy()

    def updatePos(self):
        if not (self.health is Health.DEAD or self.health is Health.CRITICAL):
            if Location.getDistance(self=self.currentLocation, x=self.target.x, y=self.target.y) < 5:
                self.setTarget(randomLocation(self.currentLocation.area))
            self.move(self.deltaXY()[0], self.deltaXY()[1])

    def updateHealth(self):
        if self.daysUntilRecovered > 0:
            self.daysUntilRecovered -= 1
        if self.daysUntilRecovered == 0:
            self.setRecovered()
        if self.health is Health.INFECTED:
            if random.random() < 0.1:
                self.setSick()
        self.hospitalRoll()
        self.deathRoll()

    def deathRoll(self):
        if self.infectious:
            chance = random.random()

            if self.health is Health.INFECTED:
                if chance < .001:
                    self.setDead()
            elif self.health is Health.SICK:
                if chance < .005:
                    self.setDead()
            else:  # else person should be in critical condition
                if chance < .01:
                    self.setDead()

    # low chance to enter critical state. will increase recovery time by 10 days if entering critical state
    def hospitalRoll(self):
        chance = random.random()
        if self.health is Health.INFECTED:
            if chance < .03:
                self.setCritical()
                self.daysUntilRecovered += 10
        if self.health is Health.SICK:
            if chance < .06:
                self.setCritical()
                self.daysUntilRecovered += 10

    def update(self):
        self.updateHealth()
        self.updatePos()

    # returns a color based on health status for the animation
    def getColor(self):
        if self.health is Health.HEALTHY:
            return 'green'
        elif self.health is Health.INFECTED:
            return 'yellow'
        elif self.health is Health.SICK:
            return 'orange'
        elif self.health is Health.CRITICAL:
            return 'red'
        elif self.health is Health.RECOVERED:
            return 'blue'
        elif self.health is Health.DEAD:
            return 'gray'
        else:
            raise Exception("something went wrong with getColor in Person")

    # update health functions
    def setInfected(self, duration=10):
        self.health = Health.INFECTED
        self.infectious = True
        self.immune = True
        self.daysUntilRecovered = duration

    def setSick(self, duration=10):
        self.health = Health.SICK
        self.infectious = True
        self.immune = True
        self.daysUntilRecovered = duration

    def setCritical(self):
        self.health = Health.CRITICAL
        self.infectious = True
        self.immune = True
        self.isolating = True

    def setDead(self):
        self.health = Health.DEAD
        self.infectious = False
        self.immune = True
        self.daysUntilRecovered = -1  # for recovery checks

    def setRecovered(self):
        self.health = Health.RECOVERED
        self.infectious = False
        self.immune = True
        self.daysUntilRecovered = -1  # just in case
        self.isolating = False
