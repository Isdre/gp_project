import pymunk
from pymunk import Vec2d
import pymunk.pygame_util

class Node:
    @staticmethod
    def __default(x:float,y:float):
        return x
    
    def __init__(self):
        self.func = Node.__default
        self.left = 0
        self.right = 0

    def __str__(self):
        return f"{self.func.__name__}({self.left},{self.right})"

    def __float__(self) -> float:
        return self.func(self.left,self.right)

class Individual:
    shape_filter = pymunk.ShapeFilter(group=1)

    def __init__(self, space, ground_y):
        self.brain = None
        self.fitness = 0
        self.crossed_legs = False
        self.previous_distance = 100
        #-------

        self.space = space
        self.ground_y = ground_y
        # Create the spider
        chassisXY = Vec2d(100, self.ground_y - 100)
        chWd = 30
        chHt = 60
        chassisMass = 10

        legWd_a = 50
        legHt_a = 5
        legWd_b = 100
        legHt_b = 5
        legMass = 1
        relativeAnguVel = 0

        # ---chassis
        self.chassis_b = pymunk.Body(chassisMass, pymunk.moment_for_box(chassisMass, (chWd, chHt)))
        self.chassis_b.position = chassisXY
        chassis_shape = pymunk.Poly.create_box(self.chassis_b, (chWd, chHt))
        chassis_shape.color = 200, 200, 200, 100

        # ---first left leg a
        self.leftLeg_1b_body = pymunk.Body(legMass, pymunk.moment_for_box(legMass, (legWd_a, legHt_a)))
        self.leftLeg_1b_body.position = chassisXY - ((legWd_a / 2), -chHt / 2)
        leftLeg_1a_shape = pymunk.Poly.create_box(self.leftLeg_1b_body, (legWd_a, legHt_a))
        leftLeg_1a_shape.color = 255, 0, 0, 100

        # ---first left leg b
        leftLeg_1b_body = pymunk.Body(legMass, pymunk.moment_for_box(legMass, (legWd_b, legHt_b)))
        leftLeg_1b_body.position = self.leftLeg_1b_body.position - ((legWd_a / 2) + (legWd_b / 2), 0)
        leftLeg_1b_shape = pymunk.Poly.create_box(leftLeg_1b_body, (legWd_b, legHt_b))
        leftLeg_1b_shape.color = 0, 255, 0, 100

        # ---first right leg a
        self.rightLeg_1b_body = pymunk.Body(legMass, pymunk.moment_for_box(legMass, (legWd_a, legHt_a)))
        self.rightLeg_1b_body.position = chassisXY + ((legWd_a / 2), chHt / 2)
        rightLeg_1a_shape = pymunk.Poly.create_box(self.rightLeg_1b_body, (legWd_a, legHt_a))
        rightLeg_1a_shape.color = 255, 0, 0, 100

        # ---first right leg b
        rightLeg_1b_body = pymunk.Body(legMass, pymunk.moment_for_box(legMass, (legWd_b, legHt_b)))
        rightLeg_1b_body.position = self.rightLeg_1b_body.position + ((legWd_a / 2) + (legWd_b / 2), 0)
        rightLeg_1b_shape = pymunk.Poly.create_box(rightLeg_1b_body, (legWd_b, legHt_b))
        rightLeg_1b_shape.color = 0, 255, 0, 100

        # ---link left leg b with left leg a
        pj_ba1left = pymunk.PinJoint(leftLeg_1b_body, self.leftLeg_1b_body, (legWd_b / 2, 0),
                                     (-legWd_a / 2, 0))  # anchor point coordinates are wrt the body; not the space
        self.motor_ba1Left = pymunk.SimpleMotor(leftLeg_1b_body, self.leftLeg_1b_body, relativeAnguVel)
        # ---link left leg a with chassis
        pj_ac1left = pymunk.PinJoint(self.leftLeg_1b_body, self.chassis_b, (legWd_a / 2, 0), (0, chHt / 2))
        self.motor_ac1Left = pymunk.SimpleMotor(self.leftLeg_1b_body, self.chassis_b, relativeAnguVel)
        # ---link right leg b with right leg a
        pj_ba1Right = pymunk.PinJoint(rightLeg_1b_body, self.rightLeg_1b_body, (-legWd_b / 2, 0),
                                      (legWd_a / 2, 0))  # anchor point coordinates are wrt the body; not the space
        self.motor_ba1Right = pymunk.SimpleMotor(rightLeg_1b_body, self.rightLeg_1b_body, relativeAnguVel)
        # ---link right leg a with chassis
        pj_ac1Right = pymunk.PinJoint(self.rightLeg_1b_body, self.chassis_b, (-legWd_a / 2, 0), (0, chHt / 2))
        self.motor_ac1Right = pymunk.SimpleMotor(self.rightLeg_1b_body, self.chassis_b, relativeAnguVel)

        self.space.add(self.chassis_b, chassis_shape)
        self.space.add(self.leftLeg_1b_body, leftLeg_1a_shape, self.rightLeg_1b_body, rightLeg_1a_shape)
        self.space.add(leftLeg_1b_body, leftLeg_1b_shape, rightLeg_1b_body, rightLeg_1b_shape)
        self.space.add(pj_ba1left, self.motor_ba1Left, pj_ac1left, self.motor_ac1Left)
        self.space.add(pj_ba1Right, self.motor_ba1Right, pj_ac1Right, self.motor_ac1Right)

        # ---prevent collisions with ShapeFilter
        chassis_shape.filter = Individual.shape_filter
        leftLeg_1a_shape.filter = Individual.shape_filter
        rightLeg_1a_shape.filter = Individual.shape_filter
        leftLeg_1b_shape.filter = Individual.shape_filter
        rightLeg_1b_shape.filter = Individual.shape_filter

        # self.motor_ba1Left.rate = 0
        # self.motor_ac1Left.rate = 0

    def __to_one_number(self,x:float, y:float) -> float:
        return (float(x) + float(y)) / 2 #do zmiany

    def getDistance(self) -> float:
        return self.chassis_b.position.x

    def getHeight(self,x:float,y:float) -> float:
        return self.chassis_b.position.y

    def getSpread(self,x:float,y:float) -> float:
        return self.leftLeg_1b_body.position.x - self.rightLeg_1b_body.position.x

    def rotateAcLeft(self,x:float, y:float) -> float:
        m = self.__to_one_number(x,y)
        self.motor_ac1Left.rate = m
        return m

    def rotateBaLeft(self,x:float, y:float) -> float:
        m = self.__to_one_number(x, y)
        self.motor_ba1Left.rate = m
        return m

    def rotateAcRight(self,x:float, y:float) -> float:
        m = self.__to_one_number(x, y)
        self.motor_ac1Right.rate = m
        return m

    def rotateBaRight(self,x:float, y:float) -> float:
        m = self.__to_one_number(x, y)
        self.motor_ba1Right.rate = m
        return m

    def addDegree(self,x:float, y:float) -> float:
        return float(x) + float(y)

    def substractDegree(self,x:float, y:float) -> float:
        return float(x) - float(y)