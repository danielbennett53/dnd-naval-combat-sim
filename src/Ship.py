import datetime
import numpy as np
import random
import math

random.seed()

def rotate(vec, theta_d):
    theta = math.radians(theta_d)
    rot_mat = np.matrix([[math.cos(theta), math.sin(theta)],
                         [-math.sin(theta), math.cos(theta)]])
    return rot_mat * np.array(vec)


def getTransformString(scale, translate, rotate):
    return "translate({},{}) rotate({}) scale({},{})".format(
        translate[0], translate[1], rotate, scale[0], scale[1])

class Ship:
    step = 0.05

    def __init__(self, name, **kwargs):
        self.name = name
        self.position = np.array([[0], [1]])
        self.velocity = 0
        self.rotation = 0
        self.turn_rate = 0
        self.accel = 0
        self.start_time = None
        self.plan = []
        self.paths = []

        self.fill = "Grey"
        self.stroke = "Black"

        for key, value in kwargs.items():
            self.__dict__[key] = value

        # Define paths
        self.paths = {
            self.name + ".ship": {
                "d": "M -0.4,-0.5 C -0.45,-0.15 -0.5,0.0 -0.5,0.2 " + \
                     "S -0.25,0.4 0.0,0.5 C 0.25,0.4 0.5,0.4 0.5,0.2 " + \
                     "S 0.45,-0.15 0.4,-0.5 Z",
                "stroke": self.stroke,
                "fill": self.fill,
                "transform": getTransformString([self.width, self.length], self.position, self.rotation),
                "stroke-width": 2,
                },
            self.name + ".plan": {
                "d": "",
                "stroke": self.stroke,
                "fill": "transparent",
                "transform": getTransformString([1, 1], [0, 0], 0),
                "stroke-width": 3,
            }
        }

    def set_motion(self, thrust=None, turn_rate=None):
        if thrust is not None:
            self.accel = float(thrust) * self.max_accel / 6
        if turn_rate is not None:
            self.turn_rate = float(turn_rate) * self.max_turn_rate / 6

        self.plan = [(self.position, self.velocity, self.rotation)]
        self.paths[self.name + ".plan"]["d"] = "M {},{} ".format(self.position[0], self.position[1])
        for i in np.arange(Ship.step, 6, Ship.step):
            pos = np.array(self.plan[-1][0])
            vel = self.plan[-1][1]
            rot = self.plan[-1][2]

            direction = rotate([[0], [1]], rot)
            new_pos = pos + direction.transpose() * Ship.step * vel
            new_vel = vel + self.accel * Ship.step
            new_vel = np.clip(new_vel, 0, self.max_vel)
            new_rot = rot + self.turn_rate * Ship.step

            self.plan.append((new_pos.tolist()[0], new_vel, new_rot))

            if i % 0.25 == 0:
                self.paths[self.name + ".plan"]["d"] += "L {},{} ".format(self.plan[-1][0][0], self.plan[-1][0][1])
        self.paths[self.name + ".plan"]["d"] += "L {},{}".format(self.plan[-1][0][0], self.plan[-1][0][1])


    def start_movement(self, roll):
        roll = float(roll)
        self.start_time = datetime.datetime.now()
        # Add random noise if roll is less than DC
        if roll < self.nav_DC:
            err = (self.nav_DC - roll) * 0.75 / self.nav_DC
            tr_err = err * self.max_turn_rate / 6
            a_err = err * self.max_accel / 6
            tr_err_high = np.clip(self.turn_rate + tr_err, -self.max_turn_rate, self.max_turn_rate)
            tr_err_low = np.clip(self.turn_rate - tr_err, -self.max_turn_rate, self.max_turn_rate)
            self.turn_rate = random.uniform(tr_err_low, tr_err_high)
            a_err_high = np.clip(self.accel + a_err, -self.max_accel, self.max_accel)
            a_err_low = np.clip(self.accel - a_err, -self.max_accel, self.max_accel)
            self.accel = random.uniform(a_err_low, a_err_high)

        self.set_motion()


    def update(self):
        if self.plan and self.start_time is not None:

            dt = (datetime.datetime.now() - self.start_time).total_seconds()

            if dt >= 6:
                self.position = self.plan[-1][0]
                self.velocity = self.plan[-1][1]
                self.rotation = self.plan[-1][2]
                self.plan = []
                return

            idx = round(dt * (len(self.plan) - 1) / 6)
            self.position = self.plan[idx][0]
            self.velocity = self.plan[idx][1]
            self.rotation = self.plan[idx][2]

        self.paths[self.name + '.ship']['transform'] = getTransformString([self.width, self.length], self.position, -self.rotation)

    def finished(self):
        if self.start_time is None:
            return True
        dt = (datetime.datetime.now() - self.start_time).total_seconds()
        if dt > 6:
            return True
        else:
            return False

    def get_ac(self):
        ac = int(self.AC[0] + (self.AC[1] - self.AC[0]) * self.velocity / self.max_vel)
        return ac



class Sprinter(Ship):
    def __init__(self, name, **kwargs):
        self.max_vel = 60
        self.max_turn_rate = 120
        self.max_accel = 20
        self.firing_arc = [(-180, 180)]
        self.firing_range = 160
        self.width = 10
        self.length = 30
        self.nav_DC = 12
        self.AC = [10, 18]
        Ship.__init__(self, name, **kwargs)


class Galleon(Ship):
    def __init__(self, name, **kwargs):
        self.max_vel = 40
        self.max_turn_rate = 60
        self.max_accel = 10
        self.firing_arc = [(-140, -40), (40, 140)]
        self.firing_range = [300, 300]
        self.width = 20
        self.length = 70
        self.nav_DC = 15
        self.AC = [8, 14]
        Ship.__init__(self, name, **kwargs)