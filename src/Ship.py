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

    def __init__(self, pos, direction):
        self.position = np.array([[pos[0]], [pos[1]]])
        self.velocity = np.array([[0], [0]])
        self.direction = np.array([[direction[0]], [direction[1]]])
        self.turn_rate = 0
        self.accel = 0
        self.start_time = datetime.datetime.now()
        self.nav_DC = 0
        self.path = []

    def set_motion(self, thrust, turn_rate):
        if abs(turn_rate) > 1.0 or abs(thrust) > 1.0:
            return

        self.turn_rate = turn_rate * self.max_turn_rate / 6
        self.accel = thrust * self.max_accel / 6

        self.path = [(self.position, self.velocity, self.direction)]
        for _ in np.arange(Ship.step, 6, Ship.step):
            new_pos = self.path[-1][0] + self.path[-1][1] * Ship.step
            new_vel = self.path[-1][1] + self.path[-1][2] * self.accel * Ship.step
            new_vel = rotate(new_vel, self.turn_rate * Ship.step)
            if np.linalg.norm(new_vel) > self.max_vel:
                new_vel = new_vel * self.max_vel / np.linalg.norm(new_vel)
            if np.dot(new_vel.getA1(), self.direction) < 0:
                new_vel = np.array([[0], [0]])
            new_dir = rotate(self.path[-1][2], self.turn_rate * Ship.step)
            self.path.append((new_pos, new_vel, new_dir))


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

        self.path = [(self.position, self.velocity, self.direction)]
        for _ in np.arange(Ship.step, 6, Ship.step):
            new_pos = self.path[-1][0] + self.path[-1][1] * Ship.step
            new_vel = self.path[-1][1] + self.path[-1][2] * self.accel * Ship.step
            new_vel = rotate(new_vel, self.turn_rate * Ship.step)
            if np.linalg.norm(new_vel) > self.max_vel:
                new_vel = new_vel * self.max_vel / np.linalg.norm(new_vel)
            new_dir = rotate(self.path[-1][2], self.turn_rate * Ship.step)
            self.path.append((new_pos, new_vel, new_dir))


    def update(self):
        if not self.path:
            return

        dt = (datetime.datetime.now() - self.start_time).total_seconds()

        if dt >= 6:
            self.position = self.path[-1][0]
            self.velocity = self.path[-1][1]
            self.direction = self.path[-1][2]
            self.path = []
            return

        idx = round(dt * (len(self.path) - 1) / 6)
        self.position = self.path[idx][0]
        self.velocity = self.path[idx][1]
        self.direction = self.path[idx][2]

    def finished(self):
        dt = (datetime.datetime.now() - self.start_time).total_seconds()
        if dt > 6:
            return True
        else:
            return False

    def get_ship(self):
        pts = [
            [[-0.4], [-0.5]],
            [[-0.45], [-0.15]],
            [[-0.5], [0.0]],
            [[-0.5], [0.2]],
            [[-0.25], [0.4]],
            [[0.0], [0.5]],
            [[0.25], [0.4]],
            [[0.5], [0.4]],
            [[0.5], [0.2]],
            [[0.45], [-0.15]],
            [[0.4], [-0.5]],
            [[-0.4], [-0.5]]
        ]

        rot_deg = math.degrees(math.acos(self.direction[1] / np.linalg.norm(self.direction)))
        scale = np.array([[self.width], [self.length]])
        for i,_ in enumerate(pts):
            pts[i] = np.multiply(scale, np.array(pts[i]))
            pts[i] = (rotate(pts[i], rot_deg) + self.position).getA1()

        svg_str = "M {},{} ".format(pts[0][0], pts[0][1]) + \
                "C {},{} {},{} {},{} ".format(pts[1][0], pts[1][1], pts[2][0], pts[2][1], pts[3][0], pts[3][1]) + \
                "S {},{} {},{} ".format(pts[4][0], pts[4][1], pts[5][0], pts[5][1]) + \
                "C {},{} {},{} {},{} ".format(pts[6][0], pts[6][1], pts[7][0], pts[7][1], pts[8][0], pts[8][1]) + \
                "S {},{} {},{} ".format(pts[9][0], pts[9][1], pts[10][0], pts[10][1]) + \
                "Z {},{}".format(pts[11][0], pts[11][1])
        return svg_str

    def get_ship_data(self):
        pts = [
            [[-0.4], [-0.5]],
            [[-0.5], [0.0]],
            [[-0.5], [0.2]],
            [[-0.1], [0.5]],
            [[0.1], [0.5]],
            [[0.5], [0.2]],
            [[0.5], [0.0]],
            [[0.4], [-0.5]],
            [[-0.4], [-0.5]]
        ]

        rot_deg = math.degrees(math.acos(self.direction[1] / np.linalg.norm(self.direction)))
        scale = np.array([[self.width], [self.length]])
        for i,_ in enumerate(pts):
            pts[i] = np.multiply(scale, np.array(pts[i]))
            pts[i] = (rotate(pts[i], rot_deg) + self.position).getA1()
        return np.array(pts)

    def get_path_data(self):
        out = np.array([])
        if not self.path:
            return out

        for i in np.linspace(0, len(self.path), num=20):
            out.append(self.path[i][0])
        print(out)
        return out


    def get_path(self):
        if not self.path:
            return ""
        svg_str = "M {},{} ".format(self.path[0][0].item(0), self.path[0][0].item(1))

        for pt in self.path:
            svg_str += "L {},{} ".format(pt[0].item(0), pt[0].item(1))
        return svg_str


class Sprinter(Ship):
    def __init__(self, pos=[0,0], direction=[1,0]):
        self.max_vel = 80
        self.max_turn_rate = 60
        self.max_accel = 30
        self.firing_arc = [(-180, 180)]
        self.firing_range = 160
        self.width = 10
        self.length = 30
        self.nav_DC = 12
        Ship.__init__(self, pos, direction)


class Galleon(Ship):
    def __init__(self, pos=[0,0],  direction=[1,0]):
        self.max_vel = 50
        self.max_turn_rate = 30
        self.max_accel = 15
        self.firing_arc = [(-140, -40), (40, 140)]
        self.firing_range = [300, 300]
        self.width = 20
        self.length = 70
        self.nav_DC = 15
        Ship.__init__(self, pos, direction)