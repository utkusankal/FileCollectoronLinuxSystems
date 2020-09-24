#!/usr/bin/python
#import json
#import subprocess
import socket
from os import walk
from os import listdir
from os.path import isfile, join
#import subprocess
import os
import re #split with multiple parameters
#import hashlib
import conf
import copy
import datetime
class LogCollector:
        
    def check_pattern(self, f, openlist):
	if f in openlist:
		return False
	if not os.path.isfile(f):
		return False
	
	for p in conf.pattern :

		if p in f or p.upper()  in f or p.lower() in f:


		
			
	        
			return True

	
	return False

    def UnOpened (self):
        openlist=[]
        path_dir_list=conf.path_dir
        for path in path_dir_list:
            var="sudo lsof" + " " + "+D" + " " + path
            stream = os.popen(var)
            lines = stream.readlines()
            
            for line in lines:
		open_file=str(line).split()[8]
		if open_file not in openlist:
        
        		openlist.append(open_file)
	filelist=[]
        for path in path_dir_list:
            filelist.extend([path+"/"+f for f in os.listdir(path) if self.check_pattern(path+"/"+f,openlist)])
        #compute difference of the lists
        return filelist

    def Checkmd5(self):
        
	unopened_final=self.UnOpened()
        path_Dir_list=conf.path_dir
	content2={}
        
        try:
       		 f= open("md5vsfilename.txt","r")
        	 content2=eval(f.read())
		 f.close()
	except:
		print("Unable to read file")

        path_dir_list=conf.path_dir
 
        file_name_with_path=[]
       
	new_md5sum=content2
	files_to_transfer_with_path=[]
	for k in unopened_final:
		if k not in new_md5sum.keys():
			files_to_transfer_with_path.append(k)
			new_md5sum[k]=self.getMD5SUM(k)
		else:
			md5_calculated=self.getMD5SUM(k)
			if new_md5sum[k]!=md5_calculated:
				new_md5sum[k]=md5_calculated
				files_to_transfer_with_path.append(k)

        return new_md5sum, files_to_transfer_with_path

    def getMD5SUM(self,filename):
	var="md5sum" +" " + filename
	
	stream = os.popen(var)
	output = stream.read()
	
	output=output.split()
	md5_calculated=output[0]
	return md5_calculated
    	
    def ConnectandTransfer(self,files_to_transfer_with_path,loglevel=2):
	# level 0: no log
	# level 1: succeed or not on host
	# level 2: all transfered files

	log=[]
        local_dir=conf.path_dir[0]
	remote_path=conf.remote_path
        remote_host_list=conf.remote_IPs
        
	exception=[True for i in remote_host_list]
	if len(files_to_transfer_with_path)==0:
		return exception,[["True","No file to transfer","[]"]]
	host_id=0
	for remote_host in remote_host_list:
			    
	    file_id=0
	    while file_id<len(files_to_transfer_with_path) :
		 file=files_to_transfer_with_path[file_id]
		 	
           	 var="scp " + " "+  file + " " + "smart@"+remote_host+":"+remote_path + " " + ">/dev/null 2>&1"
		 
		 ret_code=os.system(var)
		 	
		 if ret_code == 0:
			file_id+=1
			if loglevel==2:
				log.append(["True",remote_host,file])
		 else:
		        log.append(["False",remote_host,file])
			exception[host_id]=False
		     	break
	    host_id+=1
	return exception,log


LogCollector=LogCollector()
new_md5sum, files_to_transfer=LogCollector.Checkmd5()#unopened_final)
exception,log=LogCollector.ConnectandTransfer(files_to_transfer,conf.loglevel)
overall_status=False
for i in exception:
	if i:
		overall_status=True
if overall_status:
	f= open("md5vsfilename.txt","w+")
	f.write(str(new_md5sum))
	f.close()

execution_time=datetime.datetime.now()

f=open(conf.logfile,"a")
if overall_status:
	f.write(str(execution_time)+" INFO: status ok\n")
else:
	f.write(str(execution_time)+" INFO: Failed\n")
for l in log:
	f.write(str(execution_time)+" DEBUG: "+" ".join(l)+"\n")
f.close()


	
        
