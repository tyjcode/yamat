# https://docs.panda3d.org/1.10/python/introduction/tutorial/using-intervals-to-move-the-panda
from math import pi, sin, cos

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3

from direct.showbase.InputStateGlobal import inputState
from direct.showbase.ShowBaseGlobal import globalClock

from panda3d.core import CollisionNode, CollisionRay, CollisionTraverser, CollisionHandlerQueue, BitMask32
from panda3d.core import GeomNode, CollisionSphere, CollisionEntry

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
        #self.pandaPace.loop()

#######################
        self.disableMouse()
        self.camera.setPos(10,-40,20)
        self.camera.lookAt(0,0,0)
        inputState.watchWithModifiers(MOVE_FORWARD, "arrow_up")
        inputState.watchWithModifiers(TURN_LEFT, "arrow_left")
        inputState.watchWithModifiers(TURN_RIGHT, "arrow_right")
        self.taskMgr.add(self.update, "update")

        self.accept("escape", self.ending)

####################################
        self.pandaActor.setTag("pandaTag", "1")
        self.pandaActor.setCollideMask(BitMask32.bit(1))
 
        # self.panda_c_NP = self.pandaActor.attachNewNode(CollisionNode("col1"))
        # self.panda_c_NP.node().addSolid(CollisionSphere(0,0,300,600))
        # self.panda_c_NP.show()
        
        self.pickerNode = CollisionNode("mouseRay")
#        self.pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
        self.pickerNode.setFromCollideMask(BitMask32.bit(1))
        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        
        self.collisionTraverser = CollisionTraverser()
        self.pickerNP = self.camera.attachNewNode(self.pickerNode)
        self.handlerQueue = CollisionHandlerQueue()
        self.collisionTraverser.addCollider(self.pickerNP, self.handlerQueue)
        self.collisionTraverser.showCollisions(self.render) #衝突箇所を表示

#        self.collisionTraverser.addCollider(self.panda_c_NP, self.handlerQueue)

        self.accept("mouse1", self.ray_cast)

    def ray_cast(self):
        mouse_pos = self.mouseWatcherNode.getMouse()
        self.pickerRay.setFromLens(self.camNode, mouse_pos.getX(), mouse_pos.getY())
        self.collisionTraverser.traverse(self.render)
        # Assume for simplicity's sake that handlerQueue is a CollisionHandlerQueue.
        if self.handlerQueue.getNumEntries() > 0:
            # This is so we get the closest object.
            self.handlerQueue.sortEntries()
            pickedObj = self.handlerQueue.getEntry(0).getIntoNodePath()
            pickedObj = pickedObj.findNetTag("pandaTag")
            if not pickedObj.isEmpty():
                print(pickedObj.name)
                #pickedObj.setH(pickedObj, 90)
                pandaPos = self.pandaActor.getPos()
                i1 = self.pandaActor.posInterval(0.2,Point3(pandaPos.x, pandaPos.y, pandaPos.z + 3))
                i2 = self.pandaActor.posInterval(0.2,pandaPos)
                Sequence(i1,i2).start()


            else:
                print("Empty")
####################################

    def ending(self):
        exit()
    
    def update(self, task):
        dt = globalClock.getDt()
        key_pressed = False
        
        if inputState.isSet(MOVE_FORWARD):
            key_pressed = True
            self.pandaActor.setY(self.pandaActor, -300 * dt) #1秒でマイナス方向へ300
        
        if inputState.isSet(TURN_LEFT):
            key_pressed = True
            self.pandaActor.setH(self.pandaActor, 90 * dt) #1秒で90度

        if inputState.isSet(TURN_RIGHT):
            key_pressed = True
            self.pandaActor.setH(self.pandaActor, -90 * dt)

        if key_pressed and not self.pandaActor.getAnimControl("walk").isPlaying():
            self.pandaActor.loop("walk")
        if not key_pressed and self.pandaActor.getAnimControl("walk").isPlaying():
            self.pandaActor.stop()

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

