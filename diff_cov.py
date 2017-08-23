#-*- coding: utf-8 -*-

import sys
from subprocess import Popen, PIPE
import re
import subprocess
import tempfile
import os

def git_diff_by_version(lgr,A_V,B_V):
	cmd=['cd  %s; git diff %s %s --stat'%(lgr,A_V,B_V)]
	print "cmd:",cmd[0]
	result=[]
        try:
                out_tmp=tempfile.SpooledTemporaryFile(bufsize=10*1000)
                fileno=out_tmp.fileno()
                obj=subprocess.Popen(cmd,stdout=fileno,stderr=fileno,shell=True)
                obj.wait()
                out_tmp.seek(0)
                lines =out_tmp.readlines()
                
		for value in lines:
                        pre=value.split('|')[0].strip()
			if "SXGCDA" in pre:
				pass
				#result.append(pre)	
			elif pre[-2:]==".h" or pre[-2:]=='.m':
				result.append(pre)
			else:
				pass
                        
                return result
        except Exception,e:
                print "failue by e:",e
        finally:
                if out_tmp:
                        out_tmp.close()


def git_diff_by_file(lgr,A_V,B_V,diff_module):
        diff={}
        for mp in diff_module:
                print "mp:",mp
                if "..." in mp:
                        classname=mp.split('/')[-1].strip()
                        print "classname:",classname
                        get_module_cmd=['cd  %s; find . -name "%s"'%(lgr,classname)]
                        result_cmd=subprocess.Popen(get_module_cmd,stdin =subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).stdout.read().split('\n')[0]
                        if result_cmd:
                                get_module_path=result_cmd
                else:
                        get_module_path=mp
                print "get_mode_path",get_module_path
                print "............................"
                cmd=['cd  %s; git diff %s %s %s'%(lgr,A_V,B_V,get_module_path)]
                try:
                        out_tmp=tempfile.SpooledTemporaryFile(bufsize=10*1000)
                        fileno=out_tmp.fileno()
                        obj=subprocess.Popen(cmd,stdout=fileno,stderr=fileno,shell=True)
                        obj.wait()
                        out_tmp.seek(0)
                        lines =out_tmp.readlines()
                        i=0
                        flag=0
                        time=0
                        begin_line=0
                        diff_line=0
                        class_diff=[]
                        for value in lines:
                                #print "value:",value
                                if "new file" in value:
                                        class_diff.append(0)
                                        break
                                elif "@@" in value:
                                        begin_line=0
                                        flag=0
                                        begin_line=value.split('@@')[1].split('+')[1].split(',')[0]
                                        i=i+1
                                        flag=i
                                elif value.startswith('+') and "+++" not in value:
                                        i=i+1
                                        diff_line=int(begin_line)+i-int(flag)-1
                                        diff_class_line=get_module_path+"%"+str(diff_line)
                                        class_diff.append(diff_line)

                                elif value.startswith('-') and  "---" not in value:
                                        pass
                                else:
                                        i=i+1
                except Exception,e:
                        print "fail by e:",e

                diff[get_module_path]=class_diff
#               print "diff:",diff
        return diff










def diff_module_cov(gcda_dir,objs_dir,diff_module):
	for dm in diff_module.keys():
		class_name=dm.split('/')[-1]
		class_gcda_name=class_name.split('.')[0] + '.gcda'
		print "class_gcda_name",class_gcda_name
		cp_diff_gcda_file_cmd=['cd %s; cp %s %s'%(gcda_dir,class_gcda_name,objs_dir)]
		subprocess.Popen(cp_diff_gcda_file_cmd,stdin =subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
	


if __name__ =="__main__":
	#local git repoisty dir
	local_git_repoisty_dir=sys.argv[1]
	#want to diff version A_V,B_V,local or origin
	A_V="origin/"+sys.argv[2]
	B_V="origin/"+sys.argv[3]
	objs_dir=sys.argv[5]
	gcda_dir=sys.argv[4]
	print local_git_repoisty_dir
	print A_V
	print B_V
	print objs_dir
	print gcda_dir
	a=git_diff_by_version(local_git_repoisty_dir,A_V,B_V)
	print "a:",a
	
	b=git_diff_by_file(local_git_repoisty_dir,A_V,B_V,a)
        print "b:",b

	diff_module_cov(gcda_dir,objs_dir,b)

	


	





