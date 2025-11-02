import numpy as np
import pymunk
from pymunk import Vec2d
import pymunk.pygame_util
from enum import IntEnum
from copy import deepcopy

import uuid

class OperatorGP(IntEnum):
    Default = -1
    Variable = 0
    Constant = 1
    RotateAcLeft = 2
    RotateBaLeft = 3
    RotateAcRight = 4
    RotateBaRight = 5
    AddDegree = 6
    SubstractDegree = 7
    RotateBfLeft = 8
    RotateBfRight = 9
    Condition = 10
    Loop = 11


class Node:
    @staticmethod
    def default(x:'Node',y:'Node') -> float:
        return x

    def __init__(self):
        self.operator = OperatorGP.Default
        self.func = self.default
        self._left = 0.0
        self._right = 0.0
        self.depth = 1
        self.size = 1

    def __str__(self):
        return f"{self.func.__name__}({self.left},{self.right})"

    def __float__(self) -> float:
        return self.func(self.left,self.right)

    def __del__(self):
        del self._left
        del self._right

    def __adjust_size(self, new_value, old_value):
        if isinstance(new_value, Node):
            self.size += new_value.size
        if isinstance(old_value, Node):
            self.size -= old_value.size

    def __check_depth(self):
        if isinstance(self._right, Node):
            self.depth = 1 + self._right.depth
        if isinstance(self._left, Node):
            self.depth = max(self.depth,1 + self._left.depth)

    @property
    def left(self):
        return self._left

    @left.setter
    def left(self, value):
        self.__adjust_size(value, self._left)
        self._left = value
        self.__check_depth()

    @property
    def right(self):
        return self._right

    @right.setter
    def right(self, value):
        self.__adjust_size(value, self._right)
        self._right = value
        self.__check_depth()

    def deepcopy(old_node):

        if not isinstance(old_node, Node):
            return deepcopy(old_node)

        new_node = Node()
        new_node.operator = old_node.operator
        new_node.left = Node.deepcopy(old_node.left)
        new_node.right = Node.deepcopy(old_node.right)

        return new_node

import pymunk
from pymunk.vec2d import Vec2d

class Individual:
    used_ids = set()

    rotation_rate_up_limit = 15
    rotation_rate_down_limit = -15
    shape_filter = pymunk.ShapeFilter(group=1)

    def __init__(self, space, ground_y):
        self.unique_id = uuid.uuid4()
        while self.unique_id in Individual.used_ids:
            self.unique_id = uuid.uuid4()
        Individual.used_ids.add(self.unique_id)

        # Simulation attributes
        self.brain = None
        self.live = True
        self.fitness = 1

        # Space and position initialization
        self.space = space
        self.ground_y = ground_y
        self.start_positions = []
        chassis_start_xy = Vec2d(100, self.ground_y - 150)
        self.start_positions.append(chassis_start_xy)

        # Dimensions and properties
        chassis_width, chassis_height = 30, 60
        chassis_mass = 40
        leg_a_width, leg_a_height = 50, 5
        leg_b_width, leg_b_height = 100, 5
        foot_f_width, foot_f_height = 40, 5

        leg_mass = 10
        default_angular_velocity = 0

        # --- Create chassis
        self.chassis_body = pymunk.Body(chassis_mass, pymunk.moment_for_box(chassis_mass, (chassis_width, chassis_height)))
        self.chassis_body.position = chassis_start_xy
        self.chassis_shape = pymunk.Poly.create_box(self.chassis_body, (chassis_width, chassis_height))
        self.chassis_shape.color = (200, 200, 200, 100)
        self.chassis_shape.filter = Individual.shape_filter
        self.chassis_shape.friction = 1

        # Add chassis to space
        self.space.add(self.chassis_body, self.chassis_shape)

        # --- Create legs (left and right)
        self.legs = []
        for side in ["left", "right"]:
            offset = 1 if side == "right" else -1

            # Create leg `a`
            leg_a_body = pymunk.Body(leg_mass, pymunk.moment_for_box(leg_mass, (leg_a_width, leg_a_height)))
            leg_a_body.position = chassis_start_xy + (offset * (leg_a_width - 10), chassis_height/2)
            leg_a_shape = pymunk.Poly.create_box(leg_a_body, (leg_a_width, leg_a_height))
            leg_a_shape.color = (255, 0, 0, 100)
            leg_a_shape.filter = Individual.shape_filter
            leg_a_shape.friction = 1

            # Create leg `b`
            leg_b_body = pymunk.Body(leg_mass, pymunk.moment_for_box(leg_mass, (leg_b_width, leg_b_height)))
            leg_b_body.position = leg_a_body.position + (offset * (leg_a_width + leg_b_width) / 2, 0)
            leg_b_shape = pymunk.Poly.create_box(leg_b_body, (leg_b_width, leg_b_height))
            leg_b_shape.color = (0, 255, 0, 100)
            leg_b_shape.filter = Individual.shape_filter
            leg_b_shape.friction = 1

            # Create foot `f`
            foot_f_body = pymunk.Body(leg_mass, pymunk.moment_for_box(leg_mass, (foot_f_width, foot_f_height)))
            foot_f_body.position = leg_b_body.position + (offset * (leg_b_width + foot_f_width) / 2, 0)
            foot_f_shape = pymunk.Poly.create_box(foot_f_body, (foot_f_width, foot_f_height))
            foot_f_shape.color = (0, 0, 255, 100)
            foot_f_shape.filter = Individual.shape_filter
            foot_f_shape.friction = 1

            # Add leg parts to space
            self.space.add(leg_a_body, leg_a_shape)
            self.space.add(leg_b_body, leg_b_shape)
            self.space.add(foot_f_body, foot_f_shape)
            # --- Connect leg parts and chassis
            # Connect foot f to leg `b`
            joint_bf = pymunk.PivotJoint(leg_b_body, foot_f_body, (offset * leg_b_width / 2, 0), (-offset * foot_f_width / 2, 0))
            joint_bf.collide_bodies = False
            motor_bf = pymunk.SimpleMotor(leg_b_body, foot_f_body, default_angular_velocity)
            motor_bf.collide_bodies = False
            # Connect leg `b` to leg `a`
            joint_ba = pymunk.PivotJoint(leg_a_body, leg_b_body, (offset * leg_a_width / 2, 0), (-offset * leg_b_width / 2, 0))
            joint_ba.collide_bodies = False
            motor_ba = pymunk.SimpleMotor(leg_a_body, leg_b_body, default_angular_velocity)
            motor_ba.collide_bodies = False
            # Connect leg `a` to the chassis
            joint_ac = pymunk.PivotJoint(leg_a_body, self.chassis_body, (-offset * leg_a_width / 2, 0), (offset * chassis_width/2, chassis_height / 2))
            joint_ac.collide_bodies = False
            motor_ac = pymunk.SimpleMotor(leg_a_body, self.chassis_body, default_angular_velocity)
            motor_ac.collide_bodies = False
            # Add joints and motors to space
            self.space.add(joint_ba, motor_ba, joint_ac, motor_ac, joint_bf, motor_bf)

            # Track components for removal later
            self.legs.append((leg_a_body, leg_a_shape, leg_b_body, leg_b_shape, foot_f_body, foot_f_shape, motor_ba, motor_ac, motor_bf, joint_ac, joint_ba, joint_bf))

            # Assign motors to individual properties
            if side == "left":
                self.leg_a_body_left = leg_a_body
                self.leg_b_body_left = leg_b_body
                self.motor_ac_left = motor_ac
                self.motor_ba_left = motor_ba
                self.motor_bf_left = motor_bf
            elif side == "right":
                self.leg_a_body_right = leg_a_body
                self.leg_b_body_right = leg_b_body
                self.motor_ac_right = motor_ac
                self.motor_ba_right = motor_ba
                self.motor_bf_right = motor_bf

            self.start_positions.append((leg_a_body.position,leg_b_body.position,foot_f_body.position))
        # print(self.start_positions)
        self.max_speed = 0

    def reset_individual(self):
        self.fitness = 1
        self.live = True
        self.max_speed = 0
        # Reset chassis position and velocity
        self.chassis_body.position = self.start_positions[0]
        self.chassis_body.force = 0, 0
        self.chassis_body.torque = 0
        self.chassis_body.velocity = 0, 0
        self.chassis_body.angular_velocity = 0
        self.chassis_body.angle = 0


        i = 0
        # Reset each leg
        for leg_a_body, _, leg_b_body, _, foot_f_body, _, _, _, _, _, _, _ in self.legs:
            # Reset leg part `a`
            leg_a_body.position = self.start_positions[i+1][0]
            leg_a_body.force = 0, 0
            leg_a_body.torque = 0
            leg_a_body.velocity = 0, 0
            leg_a_body.angular_velocity = 0
            leg_a_body.angle = 0

            # Reset leg part `b`
            leg_b_body.position = self.start_positions[i+1][1]
            leg_b_body.force = 0, 0
            leg_b_body.torque = 0
            leg_b_body.velocity = 0, 0
            leg_b_body.angular_velocity = 0
            leg_b_body.angle = 0

            foot_f_body.position = self.start_positions[i+1][2]
            foot_f_body.force = 0, 0
            foot_f_body.torque = 0
            foot_f_body.velocity = 0, 0
            foot_f_body.angular_velocity = 0
            foot_f_body.angle = 0
            i += 1

        # Reset motor rates (ensure no unintended movement)
        self.motor_ba_left.rate = 0
        self.motor_ba_right.rate = 0
        self.motor_ac_left.rate = 0
        self.motor_ac_right.rate = 0
        self.motor_bf_left.rate = 0
        self.motor_bf_right.rate = 0

    def die(self):
        self.chassis_shape.color = (255,0,0,100)
        try:
            assert all(isinstance(item, tuple) and len(item) == 12 for item in self.legs), "Leg components missing in self.legs"

            for leg in self.legs:
                self.space.remove(*leg)

            self.space.remove(self.chassis_body, self.chassis_shape)

            self.live = False
            Individual.used_ids.remove(self.unique_id)
        except Exception as e:
            print(e.args)
            print(f"Error during removal: {e}")

    def check_speed(self):
        self.max_speed = max(np.sqrt(pow(self.chassis_body.velocity.x,2) + pow(self.chassis_body.velocity.y,2)),self.max_speed)
        # print(self.max_speed)

    def __str__(self):
        return f"Individual: {self.unique_id}"

    def __eq__(self, other):
        return isinstance(other, Individual) and self.unique_id == other.unique_id

    def __hash__(self):
        return hash(self.unique_id)

    def __del__(self):
        del self.brain

    def __limit_rotation(self, x:float) -> float:
        if x < Individual.rotation_rate_down_limit: x = Individual.rotation_rate_down_limit
        elif x > Individual.rotation_rate_up_limit: x = Individual.rotation_rate_up_limit
        return x

    def __to_one_number(self, x:Node, y:Node) -> float:
        return (self.__float(x) + self.__float(y)) / 2

    def getDistance(self) -> float:
        return float(self.chassis_body.position.x - 100)

    def getHeight(self,x:Node,y:Node) -> float:
        return self.chassis_body.position.y

    def getSpread(self,x:Node,y:Node) -> float:
        return self.leg_b_body_left.position.x - self.leg_b_body_right.position.x

    def rotateAcLeft(self,x:Node, y:Node) -> float:
        m = self.__to_one_number(x,y)
        self.motor_ac_left.rate = self.__limit_rotation(m)
        return m

    def rotateBaLeft(self,x:Node, y:Node) -> float:
        m = self.__to_one_number(x, y)
        self.motor_ba_left.rate = self.__limit_rotation(m)
        return m

    def rotateAcRight(self,x:Node, y:Node) -> float:
        m = self.__to_one_number(x, y)
        self.motor_ac_right.rate = self.__limit_rotation(m)
        return m

    def rotateBaRight(self,x:Node, y:Node) -> float:
        m = self.__to_one_number(x, y)
        self.motor_ba_right.rate = self.__limit_rotation(m)
        return m

    def addDegree(self,x:Node, y:Node) -> float:
        return self.__float(x) + self.__float(y)

    def substractDegree(self,x:Node, y:Node) -> float:
        return self.__float(x) - self.__float(y)

    def condition(self,x:Node, y:Node) -> float:
        c = self.__float(x)
        if c > 0:
            return c
        else:
            return self.__float(y)

    def loop(self,x:Node, y:Node) -> float:
        a = abs(int(float(x)))
        b = 0
        for _ in range(a):
            b = float(y)
        return float(a * b)

    def rotateBfLeft(self,x:Node, y:Node) -> float:
        m = self.__to_one_number(x, y)
        self.motor_bf_left.rate = self.__limit_rotation(m)
        return m

    def rotateBfRight(self,x:Node, y:Node) -> float:
        m = self.__to_one_number(x, y)
        self.motor_bf_right.rate = self.__limit_rotation(m)
        return m

    def __float(self,x):
        try:
            return float(x)
        except Exception as e:
            print(e)
            print(x)
            self.live = False
            return 0.0