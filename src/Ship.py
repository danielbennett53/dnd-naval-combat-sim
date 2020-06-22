import datetime
import numpy as np
import random
import math

random.seed()

def rotate(vec, theta_d):
    theta = math.radians(theta_d)
    rot_mat = np.matrix([[math.cos(theta), math.sin(theta)],
                         [-math.sin(theta), math.cos(theta)]])
    return rot_mat * vec


class Ship:
    step = 0.05

    def __init__(self, name, **kwargs):
        self.name = name
        self.position = np.array([[0], [1]])
        self.velocity = 0
        self.rotation = 0
        self.turn_rate = 0
        self.accel = 0
        self.start_time = datetime.datetime.now()
        self.plan = []
        self.paths = []

        self.fill = "Grey"
        self.stroke = "Black"

        for key, value in kwargs.items():
            self.__dict__[key] = value

        # Define paths
        self.paths = {
            "ship": {
                "d": "M -0.4,-0.5 C -0.45,-0.15 -0.5,0.0 -0.5,0.2 " + \
                     "S -0.25,0.4 0.0,0.5 C 0.25,0.4 0.5,0.4 0.5,0.2 " + \
                     "S 0.45,-0.15 0.4,-0.5 Z",
                "stroke": self.stroke,
                "fill": self.fill,
                "transform": {"scale": [self.width, self.length],
                              "translate": self.position.tolist(),
                              "rotate": self.rotation
                    }
                },
            "plan": {
                "d": "",
                "stroke": self.stroke,
                "fill": self.fill,
                "transform": {"scale": [1, 1],
                            "translate": [0, 0],
                            "rotate": 0}
                },
            }

    def set_motion(self, thrust=None, turn_rate=None):
        if thrust is None:
            self.accel = thrust * self.max_accel / 6
        if turn_rate is None:
            self.turn_rate = turn_rate * self.max_turn_rate / 6        

        self.plan = [(self.position, self.velocity, self.rotation)]
        self.paths["plan"]["d"] = "M {},{} ".format(self.position[0], self.position[1])
        for i in np.arange(Ship.step, 6, Ship.step):
            direction = rotate([[0], [1]], self.rotation)
            new_pos = self.plan[-1][0] + direction * Ship.step * self.velocity
            new_vel = self.plan[-1][1] + self.accel * Ship.step
            np.clip(new_vel, 0, self.max_vel)
            new_rot = self.plan[-1][2] + self.turn_rate * Ship.step
            self.plan.append((new_pos, new_vel, new_rot))
            if i % 6 == 5:
                self.paths["plan"]["d"] += "L {},{} ".format(self.plan[-1][0][0], self.plan[-1][0][1])
            
        self.paths["plan"]["d"] += "L {},{}".format(self.plan[-1][0][0], self.plan[-1][0][1])


    def start_movement(self, roll):
        self.start_time = datetime.datetime.now()
        # Add random noise if roll is less than DC
        if roll < self.nav_DC:
            err = (self.nav_DC - roll) * 1.25 / self.nav_DC
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
        if not self.plan:
            return

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

    def finished(self):
        dt = (datetime.datetime.now() - self.start_time).total_seconds()
        if dt > 6:
            return True
        else:
            return False


class Sprinter(Ship):
    def __init__(self, name, **kwargs):
        self.max_vel = 80
        self.max_turn_rate = 60
        self.max_accel = 30
        self.firing_arc = [(-180, 180)]
        self.firing_range = 160
        self.width = 10
        self.length = 30
        self.nav_DC = 12
        Ship.__init__(self, name, **kwargs)


class Galleon(Ship):
    def __init__(self, name, **kwargs):
        self.max_vel = 50
        self.max_turn_rate = 30
        self.max_accel = 15
        self.firing_arc = [(-140, -40), (40, 140)]
        self.firing_range = [300, 300]
        self.width = 20
        self.length = 70
        self.nav_DC = 15
        Ship.__init__(self, name, **kwargs)