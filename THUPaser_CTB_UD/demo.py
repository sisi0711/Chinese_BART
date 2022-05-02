# coding:utf-8
import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, render_template, request, g, flash, redirect, url_for, jsonify
from datetime import datetime
import thulac
import joint_parser as jp 
import re
# Variables
app=Flask(__name__)

app.config.update(dict(
	DATABASE=os.path.join(app.root_path, 'parser.db'), # os.path以及app.root_path都是为了确定当前app的位置
	DEBUG=True,
	SECRET_KEY='development key',
	USERNAME='admin',
	PASSWORD='default'
))
app.config.from_envvar('FLASK_SETTINGS',silent=True)

# Load THULAC and Parser models
#thu1 = thulac.thulac(seg_only=True, model_path="thulac/models")  #设置模式为行分词模式
thu1 = thulac.thulac( model_path="thulac/models")  #设置模式为行分词模式
jp.Init('models/ctb.ud.model553') # 服务器中要改动！
#jp.Init('models/joint.ctb5.model') # 服务器中要改动！

# Functions about SQLite 
def connect_db():
	print('connect_db')
	rv=sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row
	return rv

def init_db():
	print('init_db')
	db=get_db()
	with app.open_resource('parser_schema.sql', mode = 'r') as f:
		db.cursor().executescript(f.read())
	db.commit()

@app.cli.command('initdb')
def initdb_command():
	init_db()
	print('Initialized the database.')

	
def get_db():  # 这个函数的目的是确保只连接一次数据库
	print('get_db')
	if not hasattr(g, 'sqlite_db'): # hasattr意思是has attribute
		g.sqlite_db = connect_db()
	return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
	print('close_db')
	if hasattr(g,'sqlite_db'):
		g.sqlite_db.close()

# Index page		
@app.route('/', methods=['GET', 'POST'])
def index():  
	if request.method=='POST':
		sentence_get=request.form.get('sentence','')[:100] #返回的是unicode，需要转变成utf-8才可以？
		#sentence_get = re.findall(u'[^!?。？！\.\!\?]+[!?。？！\.\!\?]?', sentence_get, flags=re.U)[0]
		sentence_get = re.findall(u'[^!?。？！\!\?]+[!?。？！\!\?]?', sentence_get, flags=re.U)[0]
		sentence_get=sentence_get.encode('utf8') # utf-8
		# 输出句子（UTF-8）
		print sentence_get 
		
		# 存入数据库
		db=get_db()
		db.execute('insert into thuparser (sentence,ip,query_time) values (?,?,?)',
					[sentence_get.decode('utf-8'),request.remote_addr,datetime.now()])
		db.commit()
		
		# 分词
		lac = thu1.cut(sentence_get) #（UTF-8）
                #loc = " ".join([wp[0] for wp in thu1.cut(sentence_get)])
		lac_string=''
		word=['ROOT']
		for i in range(0,len(lac)):
			word.append(lac[i][0])
			lac_string=lac_string+lac[i][0]+' '
		#print lac_string
		
		# 句法分析
		parser_string=jp.getResults(lac_string.decode('utf-8')) # Parse（传入Unicode）得到Unicode
		# print parser_string #输出Parsing结果（Unicode）
		parser_string=parser_string.encode('utf-8')
		
		# 转为json文件
		dependencies=[]
		tokens=[]
		len_now=0
		string_now=parser_string
		for i in range(1,len(word)):
			index_now=string_now.index('\n')
			tab_num=0
			tab_loc=[]
			for j in range(0,index_now):
				if string_now[j]=='\t':
					tab_loc.append(j)
					tab_num=tab_num+1
			# 完成dependencies的构建
			dep_tmp={}
			dep_tmp['dep']=string_now[tab_loc[6]+1:tab_loc[7]]
			dep_tmp['governor']=int(string_now[tab_loc[5]+1:tab_loc[6]])
			dep_tmp['governorGloss']=word[dep_tmp['governor']]
			dep_tmp['dependent']=i
			dep_tmp['dependentGloss']=word[i]
			# print dep_tmp
			if dep_tmp['governor']==0:
				dependencies.insert(0,dep_tmp)
			else:
				dependencies.append(dep_tmp)
			# 完成tokens的构建
			token_tmp={}
			token_tmp['index']=i
			token_tmp['word']=word[i]
			token_tmp['originalText']=""
			token_tmp['characterOffsetBegin']=len_now
			token_tmp['characterOffsetEnd']=len_now+len(word[i].decode('utf-8'))
			token_tmp['pos']=string_now[tab_loc[2]+1:tab_loc[3]]
			tokens.append(token_tmp)
			# 转移
			len_now=len_now+len(word[i].decode('utf-8'))
			string_now=string_now[index_now+1:]
		sentence={}
		sentence['index']=0
		sentence['basicDependencies']=dependencies
		sentence['tokens']=tokens
		sentences=[sentence]
		data={'sentences':sentences,'Conll_data':parser_string,'sentence_get': sentence_get}
		
		# 向前端传送
		return jsonify(**data)
	else:
		return render_template('demo.html')
