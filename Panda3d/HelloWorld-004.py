# https://docs.panda3d.org/1.10/python/introduction/tutorial/using-intervals-to-move-the-panda
from math import pi, sin, cos

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3

from direct.showbase.InputStateGlobal import inputState
from direct.showbase.ShowBaseGlobal import globalClock

from panda3d.core import CollisionNode,CollisionSphere
from panda3d.core import CollisionTraverser, CollisionHandlerPusher
from panda3d.physics import PhysicsCollisionHandler

MOVE_FORWARD = "MoveForward"
TURN_LEFT = "TurnLelt"
TURN_RIGHT = "TurnRight"

class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        # Load the environment model.
        self.scene = self.loader.loadModel("models/environment")
        # Reparent the model to render.
        self.scene.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        self.scene.setScale(0.25, 0.25, 0.25)
        self.scene.setPos(-8, 42, 0)
        # Add the spinCameraTask procedure to the task manager.
        self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")
        # Load and transform the panda actor.
        self.pandaActor = Actor("models/panda-model",
                                {"walk": "models/panda-walk4"})
        self.pandaActor.setScale(0.005, 0.005, 0.005)
        self.pandaActor.reparentTo(self.render)
        # Loop its animation.
        self.pandaActor.loop("walk")
        
        # Create the four lerp intervals needed for the panda to
        # walk back and forth.
        posInterval1 = self.pandaActor.posInterval(13,
                                                   Point3(0, -10, 0),
                                                   startPos=Point3(0, 10, 0))
        posInterval2 = self.pandaActor.posInterval(13,
                                                   Point3(0, 10, 0),
                                               startPos=Point3(0, -10, 0))
        hprInterval1 = self.pandaActor.hprInterval(3,
                                                   Point3(180, 0, 0),
                                                   startHpr=Point3(0, 0, 0))
        hprInterval2 = self.pandaActor.hprInterval(3,
                                                   Point3(0, 0, 0),
                                                   startHpr=Point3(180, 0, 0))

        # Create and play the sequence that coordinates the intervals.
        self.pandaPace = Sequence(posInterval1, hprInterval1,
                                  posInterval2, hprInterval2,
                                  name="pandaPace")
        self.pandaPace.loop()


        self.disableMouse()
        self.camera.setPos(10,-40,20)
        self.camera.lookAt(0,0,0)
        inputState.watchWithModifiers(MOVE_FORWARD, "arrow_up")
        inputState.watchWithModifiers(TURN_LEFT, "arrow_left")
        inputState.watchWithModifiers(TURN_RIGHT, "arrow_right")
        self.taskMgr.add(self.update, "update")

        self.accept("escape", self.ending)

#################################################################
        self.pandaActor2 = Actor("models/panda-model",
                                {"walk": "models/panda-walk4"})
        self.pandaActor2.setScale(0.005, 0.005, 0.005)
        self.pandaActor2.setPos(1,0,0)
        self.pandaActor2.reparentTo(self.render)
        self.pandaActor2.loop("walk")

        cNode = CollisionNode('pandaActor')
        cNode.addSolid(CollisionSphere(0, -80, 200, 400))
        pandaC = self.pandaActor.attachNewNode(cNode)
        #pandaC.show()
        
        cNode2 = CollisionNode('pandaActor2')
        cNode2.addSolid(CollisionSphere(0, -80, 200, 400))
        pandaC2 = self.pandaActor2.attachNewNode(cNode2)
        #pandaC2.show()
        
        self.handlerPusher = CollisionHandlerPusher()
        self.handlerPusher.addCollider(pandaC, self.pandaActor)

        traverser = CollisionTraverser() 
        self.cTrav = traverser # cTrav は、特別なオブジェクト。このトラバーサーは、 フレームごとに自動的に実行される
        self.cTrav.addCollider(pandaC, self.handlerPusher)
#################################################################

    def ending(self):
        exit()
    
    def update(self, task):
        dt = globalClock.getDt()
        key_pressed = False
        
        if inputState.isSet(MOVE_FORWARD):
            key_pressed = True
            self.pandaActor2.setY(self.pandaActor2, -300 * dt) #1秒でマイナス方向へ300
        
        if inputState.isSet(TURN_LEFT):
            key_pressed = True
            self.pandaActor2.setH(self.pandaActor2, 90 * dt) #1秒で90度

        if inputState.isSet(TURN_RIGHT):
            key_pressed = True
            self.pandaActor2.setH(self.pandaActor2, -90 * dt)

        if key_pressed and not self.pandaActor2.getAnimControl("walk").isPlaying():
            self.pandaActor2.loop("walk")
        if not key_pressed and self.pandaActor2.getAnimControl("walk").isPlaying():
            self.pandaActor2.stop()

        return task.cont    
    
    # Define a procedure to move the camera.
    def spinCameraTask(self, task):
        # angleDegrees = task.time * 6.0
        # angleRadians = angleDegrees * (pi / 180.0)
        # self.camera.setPos(20 * sin(angleRadians), -20 * cos(angleRadians), 3)
        # self.camera.setHpr(angleDegrees, 0, 0)
        return Task.cont
    
app = MyApp()
app.run()


