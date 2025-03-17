import pygame
import cv2
import numpy as np
import math
import random
import threading
import queue
import serial
import re
import time

class CircuitBoard3D():
		
	def __init__(self) :
				
			self.width = 800
			self.height = 600
			self.screen = pygame.display.set_mode((self.width, self.height))
			pygame.display.set_caption('3D Circuit Cleaner')
			self.board_size = 4
			self.board = [[False for _ in range(self.board_size)] for _ in range(self.board_size)]
			self.player_pos = [0, 0]
			self.score = 0
			self.DEFAULT_ROT_X = 30
			
			self.DEFAULT_ROT_Y = 45
			
			self.DEFAULT_ROT_Z = 0
			self.DEFAULT_SCALE = 50
		
			
			self.rotation_x = self.DEFAULT_ROT_X
			self.rotation_y = self.DEFAULT_ROT_Y
			self.rotation_z = self.DEFAULT_ROT_Z
			self.scale = self.DEFAULT_SCALE
			self.min_scale = 20
			self.max_scale = 100
			self.center_x = self.width // 2
			self.center_y = self.height // 2
			
			self.dragging = False
			self.last_mouse_pos = None
		
			
			self.CYAN = (255, 255, 0)
			self.DARK_CYAN = (139, 139, 0)
			self.RED = (0, 0, 255)
			self.DARK_RED = (0, 0, 180)
			self.GREEN = (0, 255, 0)
			self.BLUE = (255, 0, 0)
			self.WHITE = (255, 255, 255)
			self.BLACK = (0, 0, 0)
			self.GRID_COLOR = (100, 100, 100)
		
			self.command_queue = queue.Queue()
			
		
	def reset_view(self) :
				
			self.rotation_x = self.DEFAULT_ROT_X
			self.rotation_y = self.DEFAULT_ROT_Y
			self.rotation_z = self.DEFAULT_ROT_Z
			self.scale = self.DEFAULT_SCALE
			
		
	def rotate_point(self, point) :
				
			rx = math.radians(self.rotation_x)
			ry = math.radians(self.rotation_y)
			rz = math.radians(self.rotation_z)
			Rx = np.array([[1, 0, 0], [0, math.cos(rx), -math.sin(rx)], [0, math.sin(rx), math.cos(rx)]])
			
			Ry = np.array([[math.cos(ry), 0, math.sin(ry)], [0, 1, 0], [-math.sin(ry), 0, math.cos(ry)]])
			
			
			
			
			
			Rz = np.array([[math.cos(rz), -math.sin(rz), 0], [math.sin(rz), math.cos(rz), 0], [0, 0, 1]])
			
			
			
			
			
			point = np.dot(Rx, point)
			point = np.dot(Ry, point)
			point = np.dot(Rz, point)
			
			x = point[0] * self.scale + self.center_x
			y = point[1] * self.scale + self.center_y
			
			return (int(x), int(y))
			
		
	def draw_cylinder(self, img, base_center, height, color, border_color) :
				
			view_angle = math.radians(self.rotation_x)
			radius = max(5, int(12 * self.scale / 50))
			squash = abs(math.cos(view_angle))
			
			
			height_scale = height * self.scale / 50 * 1.5
			
			
			
			top_center = (base_center[0], base_center[1] - int(height_scale))
			
			
			points = np.array([[base_center[0] - radius, base_center[1]], [base_center[0] + radius, base_center[1]], [top_center[0] + radius, top_center[1]], [top_center[0] - radius, top_center[1]]], np.int32)
			
			
			
			
			
			cv2.fillPoly(img, [points], color)
			cv2.polylines(img, [points], True, border_color)
			
			
			cv2.ellipse(img, base_center, (radius, int(radius * squash)), 0, 0, 360, color, -1)
			
			cv2.ellipse(img, base_center, (radius, int(radius * squash)), 0, 0, 360, border_color, 1)
			
			
			
			cv2.ellipse(img, top_center, (radius, int(radius * squash)), 0, 0, 360, color, -1)
			
			cv2.ellipse(img, top_center, (radius, int(radius * squash)), 0, 0, 360, border_color, 1)
			
		
	def draw_coordinate_axes(self, img) :
				
			origin = np.array([-self.board_size, -self.board_size, 0])
			origin_2d = self.rotate_point(origin)
			axis_length = 1.0
			for (axis, color, label) in [(np.array([axis_length, 0, 0]), self.RED, 'X'), (np.array([0, axis_length, 0]), self.GREEN, 'Y'), (np.array([0, 0, axis_length]), self.BLUE, 'Z')]:
				
				
				
				
				end_point = self.rotate_point(origin + axis)
				cv2.arrowedLine(img, origin_2d, end_point, color, 2, tipLength=0.3)
				
				
				dx = end_point[0] - origin_2d[0]
				dy = end_point[1] - origin_2d[1]
				length = math.sqrt(dx * dx + dy * dy)
				if length > 0:
				
					label_x = int(end_point[0] + (dx / length) * 10)
					label_y = int(end_point[1] + (dy / length) * 10)
					cv2.putText(img, label, (label_x, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
					
							
			
		
	def draw_board(self) :
				
			img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
			for i in range(self.board_size + 1):
				for j in range(self.board_size + 1):
					x = (i - self.board_size / 2) * 2
					y = (j - self.board_size / 2) * 2
					point = np.array([x, y, 0])
					if i < self.board_size and j < self.board_size:
					
						center_x = x + 1
						center_y = y + 1
						center = self.rotate_point(np.array([center_x, center_y, 0]))
						if [i, j] == self.player_pos:
						
							self.draw_cylinder(img, center, 1.0, self.RED, self.DARK_RED)
						else:
							if not self.board[i][j]:
							
								node_radius = max(5, int(15 * self.scale / 50))
								cv2.circle(img, center, node_radius, self.CYAN, -1)
								cv2.circle(img, center, node_radius, self.BLACK, 1)
								
							
						
									
							
			points = []
			for i in range(self.board_size + 1):
				for j in range(self.board_size + 1):
					x = (i - self.board_size / 2) * 2
					y = (j - self.board_size / 2) * 2
					points.append(np.array([x, y, 0]))
									
							
			for i in range(self.board_size + 1):
				p1 = self.rotate_point(points[i * (self.board_size + 1)])
				p2 = self.rotate_point(points[i * (self.board_size + 1) + self.board_size])
				cv2.line(img, p1, p2, self.GRID_COLOR, 1)
				p1 = self.rotate_point(points[i])
				p2 = self.rotate_point(points[i + (self.board_size + 1) * self.board_size])
				cv2.line(img, p1, p2, self.GRID_COLOR, 1)
							
			self.draw_coordinate_axes(img)
			font = cv2.FONT_HERSHEY_SIMPLEX
			cv2.putText(img, f'Score: {self.score}', (20, 30), font, 1, self.WHITE, 2)
			cv2.putText(img, 'Arrow Keys: Move | Mouse: Rotate | Scroll: Zoom | Space: Reset View | ESC: Quit', (20, self.height - 20), font, 0.5, self.WHITE, 1)
			
			img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
			surface = pygame.surfarray.make_surface(img.swapaxes(0, 1))
			return surface
			
		
	def handle_mouse(self, event) :
				
			if event.type == pygame.MOUSEBUTTONDOWN:
			
				if event.button == 1:
				
					self.dragging = True
					self.last_mouse_pos = pygame.mouse.get_pos()
				else:
					if event.button == 4:
					
						self.scale = min(self.max_scale, self.scale * 1.1)
					else:
						if event.button == 5:
						
							self.scale = max(self.min_scale, self.scale / 1.1)
							
						
					
			else:
				if event.type == pygame.MOUSEBUTTONUP:
				
					if event.button == 1:
					
						self.dragging = False
						
				else:
					if event.type == pygame.MOUSEMOTION and self.dragging:
					
						if self.last_mouse_pos:
						
							current_pos = pygame.mouse.get_pos()
							dx = current_pos[0] - self.last_mouse_pos[0]
							dy = current_pos[1] - self.last_mouse_pos[1]
							self.rotation_y += dx * 0.5
							self.rotation_x += dy * 0.5
							self.rotation_x = max(-89, min(89, self.rotation_x))
							self.last_mouse_pos = current_pos
							
						
					
				
			
		
	def move_player(self, dx, dy) :
				
			new_x = self.player_pos[0] + dx
			new_y = self.player_pos[1] + dy
			if 0 <= new_x < self.board_size and 0 <= new_y < self.board_size:
			
				self.player_pos = [new_x, new_y]
				if not self.board[new_x][new_y]:
				
					self.board[new_x][new_y] = True
					self.score += 10
					if random.random() < 0.2:
					
						corrupt_x = random.randint(0, self.board_size - 1)
						corrupt_y = random.randint(0, self.board_size - 1)
						if self.board[corrupt_x][corrupt_y]:
						
							self.board[corrupt_x][corrupt_y] = False
							
						
					
				
			
		
	def run(self):
		clock = pygame.time.Clock()
		running = True
		while running:
			
			try:
			
				while not self.command_queue.empty():
					command = self.command_queue.get_nowait()
					self.process_serial_command(command)
									
			except queue.Empty:
				pass
				
			
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
				
					running = False
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
					
						running = False
					elif event.key == pygame.K_SPACE:
						self.reset_view()
					elif event.key == pygame.K_UP:
						self.move_player(0, -1)
					elif event.key == pygame.K_DOWN:
						self.move_player(0, 1)
					elif event.key == pygame.K_LEFT:
						self.move_player(-1, 0)
					elif event.key == pygame.K_RIGHT:
						self.move_player(1, 0)
						
				else:
					self.handle_mouse(event)
					
							
			surface = self.draw_board()
			self.screen.blit(surface, (0, 0))
			pygame.display.flip()
			clock.tick(60)
					
		pygame.quit()
		
	def move_to_location(self, x, y):
		if 0 <= x < self.board_size and 0 <= y < self.board_size:
		
			self.player_pos = [x, y]
			if not self.board[x][y]:
			
				self.board[x][y] = True
				self.score += 10
				
				if random.random() < 0.2:
				
					corrupt_x = random.randint(0, self.board_size-1)
					corrupt_y = random.randint(0, self.board_size-1)
					if self.board[corrupt_x][corrupt_y]:
					
						self.board[corrupt_x][corrupt_y] = False
						
					
				
			return True
			
		return False
	def process_serial_command(self, command):
		
		try:
		
			
			if command.startswith(b'UP'):
			
				self.move_player(0, -1)
			elif command.startswith(b'DOWN'):
				self.move_player(0, 1)
			elif command.startswith(b'LEFT'):
				self.move_player(-1, 0)
			elif command.startswith(b'RIGHT'):
				self.move_player(1, 0)
				
		except Exception as e:
			print(f"Error processing command: {e}")
			
		
		
	
def serial_monitor(game):
	COM = 'COM8'
	BAUD = 9600
	while True:
		try:
		
			ser = serial.Serial(COM, BAUD)
			ser.flushInput()
			while True:
				try:
				
					ser_bytes = str( ser.readline() )
					if ser_bytes:
					
						position_code  = ser_bytes.replace('\\', '').replace('r', '').replace( 'b', '').replace( 'n', '' ).replace( ',', '' ).replace( '\'', '' )
						try:
						
							p = int( position_code )
							x = p % 4;
							y = int( p  / 4);
							print(f"Position code: {position_code} x,y:  {x} , {y} "  )
							game.move_to_location(x, y)
						except ValueError:
							print(f"Received: {ser_bytes } " )
							pass
							
						
						
				except serial.SerialException:
					print("Serial connection lost, retrying...")
					break
					
							
		except serial.SerialException as e:
			ser.close();
			print(f"Failed to open serial port: {e}")
			time.sleep(1)
		except Exception as e:
			ser.close();
			print(f"Unexpected error: {e}")
			time.sleep(1)
			
			
	
game = CircuitBoard3D()
def main():
	
	serial_thread = threading.Thread(target=serial_monitor, args=(game,), daemon=True)
	serial_thread.start()
	game.run()
	
if __name__ == '__main__':

	main();
	
#  Export  Date: 04:20:25 PM - 26:Oct:2024.

