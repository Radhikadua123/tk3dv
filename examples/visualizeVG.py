import sys, os, argparse
from tk3dv.extern.binvox import binvox_rw
from tk3dv.common import drawing
import tk3dv.nocstools.datastructures as ds
from PyQt5.QtWidgets import QApplication
import PyQt5.QtCore as QtCore
from PyQt5.QtGui import QKeyEvent, QMouseEvent, QWheelEvent
import numpy as np

from tk3dv.pyEasel import *
from EaselModule import EaselModule
from Easel import Easel
import OpenGL.GL as gl

vertices = [
            [0, 0, 0],[1, 0, 0],[0, 1, 0], [1, 1, 0]
           ]
colors = [
            [0, 0, 0],[1, 0, 0],[0, 1, 0], [1, 1, 0]
           ]
indexes = [
           0,1,2,#2,3,1
          ]
# indexes = [
#            0,1,1,2,2,0
#           ]

from OpenGL.GL import *
import OpenGL.arrays.vbo as glvbo

vertexarray = np.array(vertices, dtype=np.float32)
colorarray = np.array(colors, dtype=np.float32)
indexarray = np.array(indexes, dtype=np.int32)

vertexvbo = glvbo.VBO(vertexarray)
colorvbo = glvbo.VBO(colorarray)
indexvbo = glvbo.VBO(indexarray, target=GL_ELEMENT_ARRAY_BUFFER)

class VGVizModule(EaselModule):
    def __init__(self):
        super().__init__()

    def init(self, argv=None):
        self.Parser = argparse.ArgumentParser(description='This module visualizes voxel grids.', fromfile_prefix_chars='@')
        ArgGroup = self.Parser.add_argument_group()
        ArgGroup.add_argument('-v', '--voxel-grid', help='Specify binvox file.', required=True)

        self.Args, _ = self.Parser.parse_known_args(argv)
        if len(sys.argv) <= 1:
            self.Parser.print_help()
            exit()

        print('[ INFO ]: Opening binvox file:', self.Args.voxel_grid)
        with open(self.Args.voxel_grid, 'rb') as f:
            self.VG = binvox_rw.read_as_3d_array(f)

        self.VGDS = ds.VoxelGrid(self.VG)

        self.PointSize = 3
        self.showObjIdx = 0 # 0, 1, 2

    def step(self):
        pass

    def drawVG(self, Alpha=0.8, ScaleX=1, ScaleY=1, ScaleZ=1):

        if self.showObjIdx == 0 or self.showObjIdx == 1:
            self.VGDS.drawVG(Alpha, ScaleX, ScaleY, ScaleZ)

        # if self.showObjIdx == 0 or self.showObjIdx == 2:
        #     gl.glMatrixMode(gl.GL_MODELVIEW)
        #     gl.glPushMatrix()
        #     gl.glScale(ScaleX, ScaleY, ScaleZ)
        #
        #     self.VGDS.draw(pointSize=self.PointSize)
        #
        #     gl.glPopMatrix()

    def draw(self):
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPushMatrix()

        Scale = 10
        gl.glScale(Scale, Scale, Scale)

        glLineWidth(10)
        glColor4f(0, 0, 0, 1)

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)

        glEnableClientState(GL_COLOR_ARRAY)
        colorvbo.bind()
        glColorPointer(3, GL_FLOAT, 0, None)

        glEnableClientState(GL_VERTEX_ARRAY)
        vertexvbo.bind()
        indexvbo.bind()
        glVertexPointer(3, GL_FLOAT, 0, None)

        glDrawElements(GL_TRIANGLES, len(indexarray), GL_UNSIGNED_INT, None)

        glDisableClientState(GL_VERTEX_ARRAY)
        # glDisableClientState(GL_COLOR_ARRAY)
        glDisable(GL_BLEND)

        gl.glPopMatrix()

        # gl.glMatrixMode(gl.GL_MODELVIEW)
        # gl.glPushMatrix()
        #
        # gl.glTranslate(-20, -20, -20)
        # self.drawVG(0.7, 40, 40, 40)
        #
        # gl.glPopMatrix()

    def keyPressEvent(self, a0: QKeyEvent):
        if a0.key() == QtCore.Qt.Key_Plus:  # Increase or decrease point size
            if self.PointSize < 20:
                self.PointSize = self.PointSize + 1

        if a0.key() == QtCore.Qt.Key_Minus:  # Increase or decrease point size
            if self.PointSize > 1:
                self.PointSize = self.PointSize - 1

        if a0.key() == QtCore.Qt.Key_T:  # Toggle objects
            self.showObjIdx = (self.showObjIdx + 1)%(3)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    mainWindow = Easel([VGVizModule()], sys.argv[1:])
    mainWindow.show()
    sys.exit(app.exec_())
