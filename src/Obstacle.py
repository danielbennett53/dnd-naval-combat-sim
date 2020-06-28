import random
import math

random.seed()

radius_lims = [20, 70]
vertex_lims = [5, 10]
angle_err = 0.9

def getTransformString(scale, translate, rotate):
    return "translate({},{}) rotate({}) scale({},{})".format(
        translate[0], translate[1], rotate, scale[0], scale[1])

class Obstacle:

    def __init__(self, **kwargs):
        self.position = [0, 0]
        self.__dict__ = {**kwargs}

        if 'rx' not in kwargs.keys():
            self.rx = radius_lims[0] + random.random() * (radius_lims[1] - radius_lims[0])

        if 'ry' not in kwargs.keys():
            self.ry = radius_lims[0] + random.random() * (radius_lims[1] - radius_lims[0])

        if 'rotation' not in kwargs.keys():
            self.rotation = random.randint(-180, 180)

        if 'num_vertices' not in kwargs.keys():
            self.num_vertices = random.randint(vertex_lims[0], vertex_lims[1])

        angle_step = 360 / self.num_vertices
        self.vertices = []
        for i in range(self.num_vertices):
            ang = (random.random() - 0.5) * angle_step * angle_err + i * angle_step
            x = math.cos(math.radians(ang))
            y = math.sin(math.radians(ang))
            self.vertices.append((x, y))

        d = "M {},{} ".format(self.vertices[0][0], self.vertices[0][1])
        for i in range(self.num_vertices - 1):
            d += "L {},{} ".format(self.vertices[i+1][0], self.vertices[i+1][1])
        d += "Z"

        self.path = {
            "d": d,
            "stroke": "Black",
            "fill": "Gray",
            "transform": getTransformString([self.rx, self.ry], self.position, self.rotation),
            "str0ke-width": 3,
        }

