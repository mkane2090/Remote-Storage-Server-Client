from PySide2.QtCore import QObject, Slot
from api import *
import os

class Manager(QObject):

	path = ['/']
	files = []
	username = ''
	viewLocal = True
	def __init__(self):
		super().__init__()

	@Slot(result=str)
	def hello(self):
		return "Hello World"

	@Slot(str,str,result=int)
	def login(self,username,password):
		self.username = username
		rslt = login(username=username,password=password)
		if bool(rslt) is True:
			return 1
		return 0

	@Slot()
	def load_local_files(self):
		self.viewLocal = True
	
	@Slot()
	def load_remote_files(self):
		self.viewLocal = False

	@Slot(result = int)
	def num_of_files(self):
		if self.viewLocal:
			path = ''
			for val in self.path: path += val
			self.files = os.listdir(path)
		else:
			self.files = list_stored_files(username = self.username)
		return len(self.files)

	@Slot(int,result = str)
	def get_file_path(self,i):
		print(i,len(self.files))
		path = ''
		for val in self.path: path += val
		return path + self.files[i]

	@Slot(result = str)
	def back_up_file_path(self):
		if len(self.path) == 1:
			return self.path[0]
		self.path = self.path[:-1]

	@Slot(int)
	def open_file_path(self,i):
		path = ''
		for val in self.path: path += val
		if os.path.isdir(path + self.files[i]):
			self.path.append(self.files[i] + '/')
			self.files = os.listdir(path + self.files[i] + '/')
		else:
			print('Not a directory')

	@Slot(int)
	def upload_file(self,i):
		path = ''
		for val in self.path: path += val
		rslt = upload_file(self.username,path,self.files[i])
		if bool(rslt) is True:
			return 1
		return 0
	
	@Slot(int)
	def download_file(self,i):
		rslt = download_file(self.username,self.files[i])
		if bool(rslt) is True:
			return 1
		return 0

	@Slot(int)
	def delete_file(self,i):
		rslt = remove_file(self.username,self.files[i])
		if bool(rslt) is True:
			return 1
		return 0
	
	def closing(self):
		logout(username = self.username)