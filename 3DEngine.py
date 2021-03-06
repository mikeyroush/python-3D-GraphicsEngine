from scene import *
from math import tan, sin, cos, pi
import numpy as np

def matrixMult(pos,matProj):
	posProj = [0 for _ in pos]
	for j in range(len(matProj[0])):
		for k in range(len(pos)):
			posProj[j] += pos[k] * matProj[k][j]
	if not posProj[3] == 0:
		posProj = tuple(map(lambda i:i/posProj[3],posProj))
	return tuple(posProj)
	

class vec3d:
	def __init__(self,pos):
		self.pos = pos + (1,)
		(self.x,self.y,self.z) = self.pos[:3]
	
class triangle:
	def __init__(self,pos1,pos2,pos3):
		self.vertices = (pos1,pos2,pos3)
		
	@classmethod
	def fromList(cls,list):
		#initialize triangle from list of positions
		return cls(list[0],list[1],list[2])
	
class mesh:
	def __init__(self,triangles):
		self.triangles = triangles
	
class cuboid(ShapeNode):
	def __init__(self,*args,**kwargs):
		ShapeNode.__init__(self,*args,**kwargs)
		#self.path = ui.Path.rect(0,0,0,0)
		triangles = []
		#south
		triangles.append(triangle(vec3d((0,0,0)),vec3d((0,1,0)),vec3d((1,1,0))))
		triangles.append(triangle(vec3d((0,0,0)),vec3d((1,1,0)),vec3d((1,0,0))))
		#east
		triangles.append(triangle(vec3d((1,0,0)),vec3d((1,1,0)),vec3d((1,1,1))))
		triangles.append(triangle(vec3d((1,0,0)),vec3d((1,1,1)),vec3d((1,0,1))))
		#north
		triangles.append(triangle(vec3d((1,0,1)),vec3d((1,1,1)),vec3d((0,1,1))))
		triangles.append(triangle(vec3d((1,0,1)),vec3d((0,1,1)),vec3d((0,0,1))))
		#west
		triangles.append(triangle(vec3d((0,0,1)),vec3d((0,1,1)),vec3d((0,1,0))))
		triangles.append(triangle(vec3d((0,0,1)),vec3d((0,1,0)),vec3d((0,0,0))))
		#top
		triangles.append(triangle(vec3d((0,1,0)),vec3d((0,1,1)),vec3d((1,1,1))))
		triangles.append(triangle(vec3d((0,1,0)),vec3d((1,1,1)),vec3d((1,1,0))))
		#bottom
		triangles.append(triangle(vec3d((0,0,0)),vec3d((0,0,1)),vec3d((1,0,1))))
		triangles.append(triangle(vec3d((0,0,0)),vec3d((1,0,1)),vec3d((1,0,0))))
		
		#add triangles to mesh
		self.mesh = mesh(triangles)
		
		#calculate values for projection matrix
		near = .1
		far = 1000
		theta = 90
		ratio = self.parent.size.h / self.parent.size.w
		fovRad = 1 / (tan(theta/2/180*pi))
		
		#projection matrix
		self.matProj = [[0 for _ in range(4)] for _ in range(4)]
		self.matProj[0][0] = float(ratio * fovRad)
		self.matProj[1][1] = fovRad
		self.matProj[2][2] = far / (far - near)
		self.matProj[3][2] = (-far * near) / (far - near)
		self.matProj[2][3] = 1
		self.matRotX = None
		self.matRotZ = None
		self.draw()
		
	def drawTriangles(self,triangles):
		path = ui.Path()
		#ensure object doesn't move
		path.move_to(0,0)
		path.line_to(self.parent.size.w,0)
		path.line_to(self.parent.size.w,self.parent.size.h)
		
		#draw triangles
		for tri in triangles:
			verts = tri.vertices
			path.line_width = 2
			path.move_to(verts[0].x,verts[0].y)
			path.line_to(verts[1].x,verts[1].y)
			path.line_to(verts[2].x,verts[2].y)
		path.close()
		self.path = path
		self.fill_color = 'clear'
	
	def draw(self):
		triangles = []
		for i, tri in enumerate(self.mesh.triangles):
			positions = []
			for vert in tri.vertices:
				posProj = vert.pos
				if self.matRotZ:
					posProj = matrixMult(posProj,self.matRotZ)
				if self.matRotX:
					posProj = matrixMult(posProj,self.matRotX)
				posProj = (posProj[0],posProj[1],posProj[2]+3,posProj[3])
				posProj = matrixMult(posProj,self.matProj)
				vecProj = vec3d(posProj)
				vecProj.x += 1
				vecProj.y += 1
				vecProj.x *= self.parent.size.w / 2
				vecProj.y *= self.parent.size.y / 2
				positions.append(vecProj)
			triangles.append(triangle.fromList(positions))
		self.drawTriangles(triangles)

class engineGUI(Scene):
	def setup(self):
		self.background_color = '#9cce76'
		self.cube = cuboid(stroke_color='white',parent=self,position=(self.size.w/2,self.size.h/2))
		self.counter = 0
		self.theta = 1
		
		#rotation matrices
		self.matRotX = [[0 for _ in range(4)] for _ in range(4)]
		self.matRotZ = [[0 for _ in range(4)] for _ in range(4)]
		
	def update(self):
		self.counter += 1
		
		if self.counter % 1 == 0:
			self.theta += .03
			
			self.matRotX[0][0] = 1
			self.matRotX[1][1] = cos(self.theta/2)
			self.matRotX[1][2] = sin(self.theta/2)
			self.matRotX[2][1] = -sin(self.theta/2)
			self.matRotX[2][2] = cos(self.theta/2)
			self.matRotX[3][3] = 1
			self.cube.matRotX = self.matRotX
			
			self.matRotZ[0][0] = cos(self.theta)
			self.matRotZ[0][1] = sin(self.theta)
			self.matRotZ[1][0] = -sin(self.theta)
			self.matRotZ[1][1] = cos(self.theta)
			self.matRotZ[2][2] = 1
			self.matRotZ[3][3] = 1
			self.cube.matRotZ = self.matRotZ
			
			self.cube.draw()
	
#Main
run(engineGUI())
