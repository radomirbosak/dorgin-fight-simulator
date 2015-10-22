#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#import ipdb

import tkinter as t
from dfs_base import Bojic, statistika, NekonecnySubojException

import threading
import queue

def safe_int(value):
	try:
		return int(value)
	except ValueError:
		return 0

version = "2.2"
release_candidate = ""

class App():
	def __init__(self, master):
		frame = t.Frame(master)
		self.master = master
		frame.grid(column=0, row=0, sticky=(t.N, t.W, t.E, t.S))
		frame.columnconfigure(0, weight=1)
		frame.rowconfigure(0, weight=1)
		frame.pack(padx=10, pady=10)
		self.frame = frame
		self.done = False
		self.run_done = True
		self.queue = queue.Queue()

		self.thread_no = 0
		self.thread = None

		self.initUI(frame)

	def pocitaj_one(self):
		if not self.done:
			return
		print("pocitaj one entered")

		atribs = ['zi', 'uc', 'oc', 'oz', 'ut', 'mier', 'mn', 'mb', 'od', 'in', 'un']
		""" un: 0-normal, 1-utok utok, 2-fake utok """

		postava = []
		for pos in range(2):
			zi, uc, oc, oz, ut, mier, mn, mb, od, ini, un = [safe_int(self.postava[pos][key]()) for key in atribs]
			mstate = t.NORMAL if mier else t.DISABLED
			self.postava[pos]['w_mn'].config(state=mstate)
			self.postava[pos]['w_mb'].config(state=mstate)

			if mier == 1:
				uc -= mn
				ut += mn + mb
			#ipdb.set_trace()
			postava.append(
				Bojic("", zi, uc, oc, oz, ut, od, ini, un)
			)


		magic = postava[0] #Bojic("Merlin", zi[0], uc[0], oc[0], ut[0])
		skrat = postava[1] #Bojic("Škrato", zi[1], uc[1], oc[1], ut[1])
		#pravd = statistika(magic, skrat)
		
		textprepare = "..."
		self.vysledok.config(text=textprepare)	
		if not self.done:
			print('not done')
			return

		print("new thread run")
		
		self.thread_no += 1

		if self.thread:
			self.thread.stop()

		self.queue = queue.Queue()
		self.thread = ThreadedTask(self.queue, magic, skrat, self)
		self.thread.start()

	def process_queue(self):
		try:
			pravd = self.queue.get(0)
			#print('got')
			if pravd == -1:
				textprepare = "pat"
			else:
				textprepare = str(round(pravd * 100))+"%"
			self.vysledok.config(text=textprepare)
			if not self.run_done:
				print('.', end='')
		except queue.Empty:
			pass

		self.master.after(100, self.process_queue)

	def initUI(self, frame):
		self.postava = (dict(), dict())

		for pos in range(2):
			col = pos*2 + 1
			col2 = col + 1

			current_row = 1

			w = t.Label(frame, text="Postava {}:".format(pos+1)).grid(column=col, row=current_row)
			current_row += 1

			# [(widget, title, dictkey/textvarname), ...]
			prvky = [
				(t.Entry, "Životy",        'zi', "25"),
				(t.Entry, "Útočné číslo",  'uc', "10"),
				(t.Entry, "Obranné číslo", 'oc', "8"),
				(t.Entry, "Obrana zbrane", 'oz', "0"),
				(t.Entry, "Útočnosť",      'ut', "1"),
				(t.Entry, "Odolnosť", 'od', "11"),
				(t.Entry, "Bonus k iniciatíve", 'in', "0"),
				(t.Label, "Stratégia boja:", '', ""),
				(t.Radiobutton, "Normálny útok", 'un', 0),
				(t.Radiobutton, "Útok bez obrany", 'uu', 1),
				(t.Radiobutton, "Predstieraný výpad", 'uf', 2),
				(t.Checkbutton, "Mierenie", 'mier', ""),
				(t.Entry, "Náročnosť mierenia",    'mn', "0"),
				(t.Entry, "Rozdiel brnení súpera", 'mb', "0"),
			]
			# 20, 2, 1, -1, 0, 0

			def add_to_grid(widget, title, key, default, column, row):
				if widget == t.Entry:
					t.Label(frame, text=title).grid(column=column, row=row, ipadx=5)
					svar = t.StringVar()
					svar.trace("w", lambda name, index, mode, sv=svar: self.pocitaj_one())
					svar.set(default)

					w = t.Entry(frame, width=7, textvariable=svar)
					self.postava[pos][key] = svar.get
					w.grid(column=(column + 1), row=row)
					self.postava[pos]["w_" + key] = w
				elif widget == t.Checkbutton:
					ivar = t.IntVar()
					
					w = t.Checkbutton(frame, text=title, variable=ivar, command=(lambda: self.pocitaj_one()))
					self.postava[pos][key] = ivar.get
					w.grid(column=column, row=row)
					self.postava[pos]["w_" + key] = w
				elif widget == t.Radiobutton:
					if "radiovar" in self.postava[pos]:
						ivar = self.postava[pos]["radiovar"]
					else:
						ivar = t.IntVar()
						self.postava[pos]["radiovar"] = ivar

					w = t.Radiobutton(frame, text=title, variable=ivar, value=default, command=(lambda: self.pocitaj_one()))
					self.postava[pos][key] = ivar.get
					w.grid(column=column, row=row)
					self.postava[pos]["w_" + key] = w
				elif widget == t.Label:
					w = t.Label(frame, text=title)
					w.grid(column=column, row=row)

			for i,(widget, title, key, default) in enumerate(prvky):
				add_to_grid(widget, title, key, default, col, current_row + i)



		LASTROW = 2 + len(prvky)
		t.Label(frame, text="p. že prvý vyhral:").grid(column=1, row=LASTROW)
		self.vysledok = t.Label(frame, text="")
		self.vysledok.grid(column=2, row=LASTROW)

		for pos in range(2):
			self.postava[pos]['w_mier'].toggle()
			self.postava[pos]['w_mier'].invoke()
			self.postava[pos]['w_un'].select()

		self.done = True
		self.master.after(100, self.process_queue)
		print("INIT done")
		self.master.after(550, self.pocitaj_one)

class ThreadedTask(threading.Thread):
	def __init__(self, queue, postava1, postava2, app):
		threading.Thread.__init__(self)
		self.queue = queue
		self.postava1 = postava1
		self.postava2 = postava2
		self.app = app
		self.no = app.thread_no

		self.alive = True

	def run(self):
		#dokopy 100*100 = 10 000 subojov
		self.app.run_done = False
		print('run start')
		sumpravd = 0
		for s in range(100):
			if not self.alive:
				print('thread broke at',s ,'of', 1000)
				break	

			try:
				pravd = statistika(self.postava1, self.postava2, subojov=100)
				sumpravd += pravd
				self.queue.put(sumpravd / (s + 1))
			except NekonecnySubojException:
				print("nekonecny suboj encountered")
				self.queue.put(-1)
				break

			
		else:
			self.app.run_done = True
		print('run end')

	def stop(self):
		self.alive = False

if __name__=='__main__':
	root = t.Tk()
	root.title("Dorgin fight simulator 2.2")
	app = App(root)
	root.mainloop()

