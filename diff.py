#-*- coding: utf-8 -*-
from __future__ import division
import sys
from subprocess import Popen, PIPE
import re
import subprocess
import tempfile
import os
from bs4 import BeautifulSoup


def git_diff_by_version(lgr,A_V,B_V):
	cmd=['cd  %s; git diff %s %s --stat'%(lgr,A_V,B_V)]
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
		classname=mp.split('/')[-1].strip()
		get_module_cmd=['cd  %s; find . -name "%s"'%(lgr,classname)]
        	get_module_path=subprocess.Popen(get_module_cmd,stdin =subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).stdout.read()
	#	print "get_mode_path",get_module_path
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
#		print "diff:",diff
	return diff


def update_diff_html_report_line(html_class_path,line_no):
	try:    
        	f=open(html_class_path)
                data=f.read()
                f.close()
                soup = BeautifulSoup(data,'lxml')
                diff_line2="    +"+str(line_no)+" "
                print "diff_line2:",diff_line2                       
                span_soup=soup.select('span[class="lineNum"]')
                for ss in span_soup:
                	if str(ss.string).strip()==str(line_no):
                        	ss.string=diff_line2
                                ss.prettify()
                f=file(html_class_path,'w')
                f.write(str(soup))
		print "add + success for diff line"
	except Exception,e:
		print "className is update_diff_html_report_line,failue by: %s"%e
        	print "add + failue for diff line"


def update_new_html_report_line(html_class_path):
	diff_line2=''
        try:
		f=open(html_class_path)
                data=f.read()
                f.close()
                soup = BeautifulSoup(data,'lxml')
               	span_soup=soup.select('span[class="lineNum"]')
                print "span_soup:",span_soup
                diff_file_num=len(span_soup)
                for ss in span_soup:
                	diff_line2="     +"+str(ss.string).strip()+" "
                        ss.string=diff_line2
                        ss.prettify()
                f=file(html_class_path,'w')
               	f.write(str(soup))
		print "add + success for new file"
	except Exception,e:
                print "add + failue for add file"
		print "className is update_new_html_report_line,failue by:%s"%e


def update_diff_html_report_trIndex(html_class_path,diff_line_num):
	no_hit_line=0
	hit_line=0
	result=[]
	try:
		f2=open(html_class_path)
                data2=f2.read()
		f2.close()
                soup2 = BeautifulSoup(data2,'lxml')
                span_soup2=soup2.select('span[class="lineNum"]')
                for s in span_soup2:
                	#print str(s.string).strip()
                	if str(s.string).strip().startswith('+'):
                        	if s.find_next('span')['class'][0] =='lineNoCov':
                                	no_hit_line=no_hit_line+1
                                        print "no_hit_line",no_hit_line
		hit_line=diff_line_num-no_hit_line
                bfb =round(hit_line/diff_line_num,3)*100  
                new_tr_tag=soup2.new_tag('tr')
                new_br_tag=soup2.new_tag('br')
                new_td_tag=soup2.new_tag('td')
		new_td_tag1=soup2.new_tag('td')
                new_td_tag2=soup2.new_tag('td')
                new_td_tag3=soup2.new_tag('td')
                new_td_tag3['class']="headerItem"
                new_td_tag3.string='diff_lines'
                new_td_tag4=soup2.new_tag('td')
                new_td_tag4['class']="headerCovTableEntry"
                new_td_tag4.string=str(hit_line)
                new_td_tag5=soup2.new_tag('td')
                new_td_tag5['class']="headerCovTableEntry"
                new_td_tag5.string=str(diff_line_num)
                new_td_tag6=soup2.new_tag('td')
                new_td_tag6['class']="headerCovTableEntryLo"
                new_td_tag6.string=str(bfb)+" %"
                img_tags=''
		img_tags=soup2.find_all('td',attrs={'class':'headerItem'})
                img_tag=img_tags[-1].find_next('td').find_next('td').find_next('td').find_next('tr')
                print "ima_tags:", img_tag,type(img_tags)
                img_tag.insert_before(new_tr_tag)
                img_tag.insert_before(new_br_tag)
                new_tr_tag.append(new_td_tag)
		new_tr_tag.append(new_td_tag1)
                new_tr_tag.append(new_td_tag2)
                new_tr_tag.append(new_td_tag3)
               	new_tr_tag.append(new_td_tag4)
                new_tr_tag.append(new_td_tag5)
                new_tr_tag.append(new_td_tag6)
                print soup2
               	f2=file(html_class_path,'w')
                f2.write(str(soup2))
		result=[diff_line_num,hit_line,bfb]
		print "result............................:",result
		print "add difflinecov success for diff file"
		return result
	except Exception,e:
        	print "className is update_diff_html_report_trIndex,failue by:%s"%e
		print "add difflinecov failue for diff file"


def update_nodiff_html_report_trIndex(html_class_path):
	no_hit_line=0
        hit_line=0
        diff_file_num=0
	try:
                f2=open(html_class_path)
                data2=f2.read()
		f2.close()
                soup2 = BeautifulSoup(data2,'lxml')
                bfb = "0.0"
                new_tr_tag=soup2.new_tag('tr')
                new_br_tag=soup2.new_tag('br')
		new_td_tag=soup2.new_tag('td')
                new_td_tag1=soup2.new_tag('td')
                new_td_tag2=soup2.new_tag('td')
                new_td_tag3=soup2.new_tag('td')
                new_td_tag3['class']="headerItem"
                new_td_tag3.string='diff_lines'
                new_td_tag4=soup2.new_tag('td')
                new_td_tag4['class']="headerCovTableEntry"
                new_td_tag4.string=str(hit_line)
                new_td_tag5=soup2.new_tag('td')
                new_td_tag5['class']="headerCovTableEntry"
                new_td_tag5.string=str(diff_file_num)
                new_td_tag6=soup2.new_tag('td')
                new_td_tag6['class']="headerCovTableEntryLo"
		new_td_tag6.string=str(bfb)+" %"
		img_tags=''
		img_tags=soup2.find_all('td',attrs={'class':'headerItem'})
                img_tag=img_tags[-1].find_next('td').find_next('td').find_next('td').find_next('tr')
                print "ima_tags:", img_tag,type(img_tags)
                img_tag.insert_before(new_tr_tag)
                img_tag.insert_before(new_br_tag)
		new_tr_tag.append(new_td_tag)
                new_tr_tag.append(new_td_tag1)
                new_tr_tag.append(new_td_tag2)
                new_tr_tag.append(new_td_tag3)
                new_tr_tag.append(new_td_tag4)
                new_tr_tag.append(new_td_tag5)
                new_tr_tag.append(new_td_tag6)
                print soup2
		f2=file(html_class_path,'w')
                f2.write(str(soup2))
                result=[diff_file_num,hit_line,bfb]
                return result

        except Exception,e:
		print "className is update_nodiff_html_report_trIndex,failue by:%s"%e
                print "add no difflinecov failue for diff file"





def update_new_html_report_trIndex(html_class_path):
	no_hit_line=0
        hit_line=0
	diff_file_num=0
        result=[]
        try:
		f2=open(html_class_path)
                data2=f2.read()
                soup2 = BeautifulSoup(data2,'lxml')
                hit_line=len(soup2.select('span[class="lineCov"]'))
                print "hit_line:",hit_line
                no_hit_line=len(soup2.select('span[class="lineNoCov"]'))
                print "no_hit_line:",no_hit_line
                diff_file_num = no_hit_line+hit_line
                bfb = round(hit_line/diff_line_num,3)*100
                new_tr_tag=soup2.new_tag('tr')
                new_br_tag=soup2.new_tag('br')
		new_td_tag=soup2.new_tag('td')
                new_td_tag1=soup2.new_tag('td')
                new_td_tag2=soup2.new_tag('td')
                new_td_tag3=soup2.new_tag('td')
                new_td_tag3['class']="headerItem"
                new_td_tag3.string='diff_lines'
                new_td_tag4=soup2.new_tag('td')
                new_td_tag4['class']="headerCovTableEntry"
               	new_td_tag4.string=str(hit_line)
                new_td_tag5=soup2.new_tag('td')
                new_td_tag5['class']="headerCovTableEntry"
                new_td_tag5.string=str(diff_file_num)
                new_td_tag6=soup2.new_tag('td')
                new_td_tag6['class']="headerCovTableEntryLo"
		new_td_tag6.string=str(bfb)+" %"
		img_tags=''
                img_tags=soup2.find_all('td',attrs={'class':'headerItem'})
                img_tag=img_tags[-1].find_next('td').find_next('td').find_next('td').find_next('tr')
                print "ima_tags:", img_tag,type(img_tags)
                img_tag.insert_before(new_tr_tag)
                img_tag.insert_before(new_br_tag)
		new_tr_tag.append(new_td_tag)
                new_tr_tag.append(new_td_tag1)
                new_tr_tag.append(new_td_tag2)
                new_tr_tag.append(new_td_tag3)
                new_tr_tag.append(new_td_tag4)
                new_tr_tag.append(new_td_tag5)
                new_tr_tag.append(new_td_tag6)
                print soup2
                f2=file(html_class_path,'w')
                f2.write(str(soup2))
		result=[diff_file_num,hit_line,bfb]
		return result
	except Exception,e:
		print "className is update_new_html_report_trIndex,failue by:%s"%e
                print "add difflinecov failue for diff file"




def update_index_diff(index_path,hit_num,total_num,bfb,hit,total,p_name):
	try:
                f2=open(index_path)
                data2=f2.read()
                soup2 = BeautifulSoup(data2,'lxml')
                new_tr_tag=soup2.new_tag('tr')
                new_br_tag=soup2.new_tag('br')
                new_td_tag=soup2.new_tag('td')
		new_td_tag1=soup2.new_tag('td')
                new_td_tag2=soup2.new_tag('td')
                new_td_tag3=soup2.new_tag('td')
                new_td_tag3['class']="headerItem"
                new_td_tag3.string='diff_lines'
                new_td_tag4=soup2.new_tag('td')
                new_td_tag4['class']="headerCovTableEntry"
                new_td_tag4.string=str(hit_num)
                new_td_tag5=soup2.new_tag('td')
                new_td_tag5['class']="headerCovTableEntry"
                new_td_tag5.string=str(total_num)
                new_td_tag6=soup2.new_tag('td')
                new_td_tag6['class']="headerCovTableEntryLo"
		new_td_tag6.string=str(bfb)+" %"
		img_tags=''
                img_tags=soup2.find_all('td',attrs={'class':'headerItem'})
		img_tag=img_tags[-1].find_next('td').find_next('td').find_next('td').find_next('tr')
                print "ima_tags:", img_tag,type(img_tags)
                img_tag.insert_before(new_tr_tag)
                img_tag.insert_before(new_br_tag)
		new_tr_tag.append(new_td_tag)
                new_tr_tag.append(new_td_tag1)
                new_tr_tag.append(new_td_tag2)
                new_tr_tag.append(new_td_tag3)
                new_tr_tag.append(new_td_tag4)
                new_tr_tag.append(new_td_tag5)
                new_tr_tag.append(new_td_tag6)

			
		new_tableHead_tags=soup2.find_all('td',attrs={'class':'tableHead'})
		new_tableHead_tag=new_tableHead_tags[-1]
		try:
			td_widths=soup2.select('td[width="50%"]')
			td_width=td_widths[0]
			td_width['width']='30%'
			new_width_td1=soup2.new_tag('td')
			new_width_td1['width']='10%'
			new_width_td2=soup2.new_tag('td')
			new_width_td2['width']='10%'
			td_width.insert_after(new_width_td1)
			td_width.insert_after(new_width_td2)
		except Exception,e:
			pass
		print "new_tableHead_tag",new_tableHead_tag
		new_tableHead_td1=soup2.new_tag('td')
		new_tableHead_td1['class']="tableHead"
		new_tableHead_td1['colspan']=2
		new_tableHead_td1.string="diff lines"
		new_tableHead_span=soup2.new_tag('span')
		new_tableHead_span['class']="tableHeadSort"
		new_tableHead_a=soup2.new_tag('a')
		new_tableHead_a['href']="index-sort-f.html"
		new_tableHead_img=soup2.new_tag('img')
		new_tableHead_img['src']="../..updown.png"
		new_tableHead_img['width']=10
		new_tableHead_img['height']=14
		new_tableHead_img['alt']="Sort by function coverage"
		new_tableHead_img['title']="Sort by function coverage"
		new_tableHead_img['border']=0
		new_tableHead_a.append(new_tableHead_img)
		new_tableHead_span.append(new_tableHead_a)
		new_tableHead_td1.append(new_tableHead_span)
		new_tableHead_tag.insert_after(new_tableHead_td1)
		#new_tableHead_tag.append(new_tableHead_td1)
		print "................"
		


		new_coverFile_tags=soup2.find_all('td',attrs={'class':'coverFile'})
		for i in range(len(p_name)):
			print "p_name",p_name[i]
			p_t=p_name[i].split('.')[0]+"."+p_name[i].split('.')[1]
			print "p_t:",p_t
			for s in new_coverFile_tags:
                        	hit_line=0
                        	total_line=0
                        	bfb1="0.0"
                        	s_t=str(s.string).split('/')[-1]
				print "s_t:",s_t
                                if p_t==s_t:
                                        hit_line=hit[i]
                                        total_line=total[i]
                                        if total_line==0:
                                                bfb1='0.0'
                                        else:
                                                bfb1=round(hit_line/total_line,3)*100
			
                        		c_tag=s.find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td')
                        		print "c_tag:",c_tag
                        		print "hit_line:",hit_line
                        		print "total_line:",total_line

                        		if int(str(bfb1).split(".")[0])<50:
                                		con="coverNumLo"
                                		pcon="coverPerLo"
                        		elif int(str(bfb1).split(".")[0])>50 and int(str(bfb1).split(".")[0])<80:
                                		con="coverNumMed"
                                		pcon="coverPerMed"
                        		else:
                                		con="coverNumHi"
                                		pcon="coverPerHi"

                        		new_coverNumLo_td=soup2.new_tag('td')
                        		new_coverPerLo_td=soup2.new_tag('td')
                        		new_coverNumLo_td['class']=con
                        		new_coverNumLo_td.string="%s / %s"%(hit_line,total_line)
                        		new_coverPerLo_td['class']=pcon
                        		new_coverPerLo_td.string="%s"%bfb1+" %"
                        		c_tag.insert_after(new_coverNumLo_td)

                        		c_tag.insert_after(new_coverPerLo_td)
		
	
		print".............................soup2:", soup2
		f2=file(index_path,'w')
                f2.write(str(soup2))
	

        except Exception,e:
		print "className is update_index_diff,failue by:%s"%e
                print "add difflinecov failue for diff file"





def update_html(index_path,diff_lines):
#	try:
		f2=open(index_path)
                data2=f2.read()
		f2.close()
                soup2 = BeautifulSoup(data2,'lxml')
				
		html_total_diff=[]
                html_hit_diff=[]
		for k,v in diff_lines.items():
			print "v:",v,v[0],v[1]
			html_hit_diff.append(v[0])
			html_total_diff.append(v[1])
		html_total_num=sum(html_total_diff)
		html_hit_num=sum(html_hit_diff)
		print "total_diff:",html_total_num
                print "hit_diff:",html_hit_num
                if html_total_num==0:
                        bfb='0.0'
                else:
                        bfb=round(html_hit_num/html_total_num,3)*100

		new_tr_tag=soup2.new_tag('tr')
                new_br_tag=soup2.new_tag('br')
                new_td_tag=soup2.new_tag('td')
                new_td_tag1=soup2.new_tag('td')
                new_td_tag2=soup2.new_tag('td')
                new_td_tag3=soup2.new_tag('td')
                new_td_tag3['class']="headerItem"
                new_td_tag3.string='diff_lines'
                new_td_tag4=soup2.new_tag('td')
                new_td_tag4['class']="headerCovTableEntry"
                new_td_tag4.string=str(html_hit_num)
                new_td_tag5=soup2.new_tag('td')
                new_td_tag5['class']="headerCovTableEntry"
                new_td_tag5.string=str(html_total_num)
                new_td_tag6=soup2.new_tag('td')
                new_td_tag6['class']="headerCovTableEntryLo"
                new_td_tag6.string=str(bfb)+" %"
                img_tags=''
                img_tags=soup2.find_all('td',attrs={'class':'headerItem'})
                img_tag=img_tags[-1].find_next('td').find_next('td').find_next('td').find_next('tr')
                print "ima_tags:", img_tag,type(img_tags)
                img_tag.insert_before(new_tr_tag)
                img_tag.insert_before(new_br_tag)
                new_tr_tag.append(new_td_tag)
                new_tr_tag.append(new_td_tag1)
                new_tr_tag.append(new_td_tag2)
                new_tr_tag.append(new_td_tag3)
                new_tr_tag.append(new_td_tag4)
                new_tr_tag.append(new_td_tag5)
                new_tr_tag.append(new_td_tag6)
		try:
			new_tableHead_tags=soup2.find_all('td',attrs={'class':'tableHead'})
                	new_tableHead_tag=new_tableHead_tags[-1]
                	td_widths=soup2.select('td[width="50%"]')
                	td_width=td_widths[0]
                	td_width['width']='30%'
                	new_width_td1=soup2.new_tag('td')
                	new_width_td1['width']='10%'
                	new_width_td2=soup2.new_tag('td')
                	new_width_td2['width']='10%'
                	td_width.insert_after(new_width_td1)
                	td_width.insert_after(new_width_td2)
		except Exception,e:
			pass
                print "new_tableHead_tag",new_tableHead_tag
                new_tableHead_td1=soup2.new_tag('td')
                new_tableHead_td1['class']="tableHead"
                new_tableHead_td1['colspan']=2
                new_tableHead_td1.string="diff lines"
                new_tableHead_span=soup2.new_tag('span')
                new_tableHead_span['class']="tableHeadSort"
                new_tableHead_a=soup2.new_tag('a')
                new_tableHead_a['href']="index-sort-f.html"
                new_tableHead_img=soup2.new_tag('img')
                new_tableHead_img['src']="../..updown.png"
                new_tableHead_img['width']=10
                new_tableHead_img['height']=14
                new_tableHead_img['alt']="Sort by function coverage"
                new_tableHead_img['title']="Sort by function coverage"
                new_tableHead_img['border']=0
                new_tableHead_a.append(new_tableHead_img)
                new_tableHead_span.append(new_tableHead_a)
                new_tableHead_td1.append(new_tableHead_span)
                new_tableHead_tag.insert_after(new_tableHead_td1)
                #new_tableHead_tag.append(new_tableHead_td1)
                print "................"
		
		
		new_coverFile_tag=soup2.find_all('td',attrs={'class':'coverFile'})
		
		for s in new_coverFile_tag:
			hit_line=0
			total_line=0
			bfb1="0.0"
			s_t=str(s.string).split('/')[-1]
			for k1,v1 in diff_lines.items(): 				
				if k1==s_t:
					hit_line=v1[0]
					total_line=v1[1]
					if total_line==0:
                        			bfb1='0.0'
                			else:
                        			bfb1=round(hit_line/total_line,3)*100
			
			c_tag=s.find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td')
			print "c_tag:",c_tag
			print "hit_line:",hit_line
			print "total_line:",total_line

			if int(str(bfb1).split(".")[0])<50:
				con="coverNumLo"
				pcon="coverPerLo"
			elif int(str(bfb1).split(".")[0])>50 and int(str(bfb1).split(".")[0])<80:
				con="coverNumMed"
				pcon="coverPerMed"
			else:
				con="coverNumHi"
				pcon="coverPerHi"
				
			new_coverNumLo_td=soup2.new_tag('td')
                        new_coverPerLo_td=soup2.new_tag('td')
                        new_coverNumLo_td['class']=con
                        new_coverNumLo_td.string="%s / %s"%(hit_line,total_line)
                        new_coverPerLo_td['class']=pcon
                        new_coverPerLo_td.string="%s"%bfb1+" %"
                        c_tag.insert_after(new_coverNumLo_td)

                        c_tag.insert_after(new_coverPerLo_td)
				
		print soup2
        	f2=file(index_path,'w')
                f2.write(str(soup2))												



#	except Exception,e:
 #               print "className is update_html,failue by:%s"%e
                


		


def diff_index_html(report_dir,diff_lines={}):
	diff_module={}
	path_module={}
	root_module={}
        for path,d,filelist in os.walk(report_dir):
                if len(filelist)!=0:
			gcov=[]
			for fl in filelist:
                                if ".gcov.html" in fl:
					gcov.append(fl)
			print "path:",path
			print "gcov",gcov	
			if gcov:
				for gs in gcov:
					print gs
					className=gs.split(".")[0]+"."+gs.split(".")[1]
					print "className:",className
					html_class_path=os.path.join(path,gs)
					print "html_class_path:",html_class_path
				#	if [x for x in [k for k in diff_lines] if className in x]:
					flag=False
					temp=[]
					md=[]
					for k,v in diff_lines.items():
						if className in k:
							flag=True
							temp=v		
					if flag==True:			
						diff_line=temp
                				diff_line_num=len(temp)
						print "diff_line",diff_line	
						diff_line_num=len(diff_line)
						print "diff_line_num:",diff_line_num
						if diff_line_num !=0 and diff_line[0]!=0:
							for i in diff_line:
								update_diff_html_report_line(html_class_path,i)

							md=update_diff_html_report_trIndex(html_class_path,diff_line_num)
						elif diff_line_num !=0 and diff_line[0]==0:
							update_new_html_report_line(html_class_path)
							md=update_new_html_report_trIndex(html_class_path)				
						else:
							md=update_nodiff_html_report_trIndex(html_class_path)
							print "some diff lines only by removed"		
					else:
						md=update_nodiff_html_report_trIndex(html_class_path)
					
					diff_module[gs]=md
					#print "diff_module:",diff_module

				path_module[path]=diff_module
				diff_module={}
		
	print "................................................path_module:",path_module						
		

	for p,m in path_module.items():
		index_path=os.path.join(p,"index.html")
		print "index_path:",index_path
		total_diff=[]
		hit_diff=[]
		pre_diff=[]
		print "m.............................:",m
		for p2,m2 in m.items():
			if m2:				
				total_diff.append(m2[0])
				hit_diff.append(m2[1])
				pre_diff.append(p2)
			else:
				total_diff.append(0)
				hit_diff.append(0)
				pre_diff.append(p2)
		print "total_diff:",total_diff
		print "hit_diff:",hit_diff
		print "pre_diff:",pre_diff
								
		index_total_num=sum(total_diff)
		index_hit_num=sum(hit_diff)

		
		if index_total_num==0:
			bfb='0.0'
		else:
			bfb=round(index_hit_num/index_total_num,3)*100
		update_index_diff(index_path,index_hit_num,index_total_num,bfb,hit_diff,total_diff,pre_diff)
		
		last_module=p.split('/')[-1].strip()


		root_module[last_module]=[index_hit_num,index_total_num,bfb]

	print"root_module:",root_module
	root_path=os.path.join(report_dir,"index.html")
	update_html(root_path,root_module)
	

													
		


if __name__ =="__main__":
	#local git repoisty dir
	local_git_repoisty_dir='/users/mobile/vip_spec/vip_spec/'
	#want to diff version A_V,B_V,local or origin
	A_V='origin/feature/feature-6.5-long'
	B_V='origin/feature/feature-6.4.-long'
	diff_report_dir='/users/mobile/XcodeCoverage/report/'

	a=git_diff_by_version(local_git_repoisty_dir,A_V,B_V)
	print "a:",a
	
	b=git_diff_by_file(local_git_repoisty_dir,A_V,B_V,a)
        print "b:",b

#	diff_mode=update_html(diff_report_dir,b)
#	print diff_mode
	diff_index_html(diff_report_dir,b)


