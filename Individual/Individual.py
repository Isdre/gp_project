import pymunk
from pymunk import Vec2d
import pymunk.pygame_util

class Individual:
    def __init__(self, space, ground_y):
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
        chassis_b = pymunk.Body(chassisMass, pymunk.moment_for_box(chassisMass, (chWd, chHt)))
        chassis_b.position = chassisXY
        chassis_shape = pymunk.Poly.create_box(chassis_b, (chWd, chHt))
        chassis_shape.color = 200, 200, 200, 100

        # ---first left leg a
        leftLeg_1a_body = pymunk.Body(legMass, pymunk.moment_for_box(legMass, (legWd_a, legHt_a)))
        leftLeg_1a_body.position = chassisXY - ((legWd_a / 2), -chHt / 2)
        leftLeg_1a_shape = pymunk.Poly.create_box(leftLeg_1a_body, (legWd_a, legHt_a))
        leftLeg_1a_shape.color = 255, 0, 0, 100

        # ---first left leg b
        leftLeg_1b_body = pymunk.Body(legMass, pymunk.moment_for_box(legMass, (legWd_b, legHt_b)))
        leftLeg_1b_body.position = leftLeg_1a_body.position - ((legWd_a / 2) + (legWd_b / 2), 0)
        leftLeg_1b_shape = pymunk.Poly.create_box(leftLeg_1b_body, (legWd_b, legHt_b))
        leftLeg_1b_shape.color = 0, 255, 0, 100

        # ---first right leg a
        rightLeg_1a_body = pymunk.Body(legMass, pymunk.moment_for_box(legMass, (legWd_a, legHt_a)))
        rightLeg_1a_body.position = chassisXY + ((legWd_a / 2), chHt / 2)
        rightLeg_1a_shape = pymunk.Poly.create_box(rightLeg_1a_body, (legWd_a, legHt_a))
        rightLeg_1a_shape.color = 255, 0, 0, 100

        # ---first right leg b
        rightLeg_1b_body = pymunk.Body(legMass, pymunk.moment_for_box(legMass, (legWd_b, legHt_b)))
        rightLeg_1b_body.position = rightLeg_1a_body.position + ((legWd_a / 2) + (legWd_b / 2), 0)
        rightLeg_1b_shape = pymunk.Poly.create_box(rightLeg_1b_body, (legWd_b, legHt_b))
        rightLeg_1b_shape.color = 0, 255, 0, 100

        # ---link left leg b with left leg a
        pj_ba1left = pymunk.PinJoint(leftLeg_1b_body, leftLeg_1a_body, (legWd_b / 2, 0),
                                     (-legWd_a / 2, 0))  # anchor point coordinates are wrt the body; not the space
        self.motor_ba1Left = pymunk.SimpleMotor(leftLeg_1b_body, leftLeg_1a_body, relativeAnguVel)
        # ---link left leg a with chassis
        pj_ac1left = pymunk.PinJoint(leftLeg_1a_body, chassis_b, (legWd_a / 2, 0), (0, chHt / 2))
        self.motor_ac1Left = pymunk.SimpleMotor(leftLeg_1a_body, chassis_b, relativeAnguVel)
        # ---link right leg b with right leg a
        pj_ba1Right = pymunk.PinJoint(rightLeg_1b_body, rightLeg_1a_body, (-legWd_b / 2, 0),
                                      (legWd_a / 2, 0))  # anchor point coordinates are wrt the body; not the space
        self.motor_ba1Right = pymunk.SimpleMotor(rightLeg_1b_body, rightLeg_1a_body, relativeAnguVel)
        # ---link right leg a with chassis
        pj_ac1Right = pymunk.PinJoint(rightLeg_1a_body, chassis_b, (-legWd_a / 2, 0), (0, chHt / 2))
        self.motor_ac1Right = pymunk.SimpleMotor(rightLeg_1a_body, chassis_b, relativeAnguVel)

        self.space.add(chassis_b, chassis_shape)
        self.space.add(leftLeg_1a_body, leftLeg_1a_shape, rightLeg_1a_body, rightLeg_1a_shape)
        self.space.add(leftLeg_1b_body, leftLeg_1b_shape, rightLeg_1b_body, rightLeg_1b_shape)
        self.space.add(pj_ba1left, self.motor_ba1Left, pj_ac1left, self.motor_ac1Left)
        self.space.add(pj_ba1Right, self.motor_ba1Right, pj_ac1Right, self.motor_ac1Right)

        # ---prevent collisions with ShapeFilter
        shape_filter = pymunk.ShapeFilter(group=1)
        chassis_shape.filter = shape_filter
        leftLeg_1a_shape.filter = shape_filter
        rightLeg_1a_shape.filter = shape_filter
        leftLeg_1b_shape.filter = shape_filter
        rightLeg_1b_shape.filter = shape_filter

        # self.motor_ba1Left.rate = 0
        # self.motor_ac1Left.rate = 0

