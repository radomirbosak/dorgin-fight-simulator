"""
========================
Dorgin Fight Simulator 2
========================
- popis

-----
FIXME
-----
a) bojaschopnost (str 69)
b) iniciativa (1k6 vs. 1k6, str 71?)
c) 
"""


from random import randrange, randint
import math
#import ipdb

STRATEGIA_NORMAL = 0
STRATEGIA_UTOKUTOK = 1
STRATEGIA_FAKEUTOK = 2
logging = False

class Bojic():
	def __init__(self, meno, zivoty_max, utocne_cislo, obranne_cislo, obrana_zbrane , utocnost, odolnost, iniciativa, strategia):
		self.meno = meno
		self.zivoty = zivoty_max
		self.zivoty_max = zivoty_max
		self.utocne_cislo = utocne_cislo
		self.obranne_cislo = obranne_cislo
		self.obrana_zbrane = obrana_zbrane
		self.utocnost = utocnost

		self.odolnost = odolnost
		self.iniciativa = iniciativa
		self.strategia = strategia

		o = self.odolnost
		if o <= 5:
			self.medz_vyradenia = int(zivoty_max / 4)
			self.postih_bs = -3
		elif o <= 11:
			self.medz_vyradenia = int(zivoty_max / 6)
			self.postih_bs = -2
		elif o <= 16:
			self.medz_vyradenia = int(zivoty_max / 8)
			self.postih_bs = -1
		else:
			self.medz_vyradenia = 1
			self.postih_bs = 0

	def ozi(self):
		self.zivoty = self.zivoty_max

	def zivy(self):
		return self.zivoty > 0

	def mrtvy(self):
		return not self.zivy()

	def bojaschopny(self):
		return self.zivoty > self.medz_vyradenia

def kocka1k6():
	return randint(1, 6)

def kocka1k6_plus():
	r = kocka1k6()
	suma = r
	while r == 6:
		r = kocka1k6()
		suma += r
	return suma

def kocka2k6_plus():
	return kocka1k6_plus() + kocka1k6_plus()

class NekonecnySubojException(Exception):
	def __init__(self, message=""):
		super(NekonecnySubojException, self).__init__("suboj trva pridlho bez ziadneho vysledku")

def akcie_from_inic(iniciativa):
	return max(int(math.ceil(iniciativa/6))*2, 0)

def log(message):
	if logging:
		print(message)

def suboj(postava1, postava2):
	POISTKA_POCET_UDEROV = 10000
	pocet_subojov = 0
	postavy = [postava1, postava2]
	postava1.akcie = 0
	postava2.akcie = 0

	na_tahu = 0 if randrange(2) == 0 else 1
	#ipdb.set_trace()
	while all([postava.bojaschopny() for postava in postavy]):
		log("zacalo sa kolo %d" % pocet_subojov)
		if all([postava.akcie <= 0 for postava in postavy]):
			for postava in postavy:
				postava.koloakcie = akcie_from_inic(kocka1k6() + postava.iniciativa)
				postava.akcie = postava.koloakcie
				log("{} má {} akcii".format(postava.meno, postava.akcie))

			for pos in range(2):
				if postavy[pos].strategia == STRATEGIA_NORMAL:
					if postavy[pos].koloakcie >= postavy[1 - pos].koloakcie:
						postavy[pos].pocet_obran = int(postavy[1 - pos].koloakcie / 2)
						postavy[pos].pocet_utokov = min(postavy[pos].koloakcie - postavy[pos].pocet_obran, int(postavy[pos].koloakcie / 2) + 1)
						postavy[pos].pocet_obran = min(postavy[pos].koloakcie - postavy[pos].pocet_utokov,  int(postavy[pos].koloakcie / 2) + 1)
					else:
						postavy[pos].pocet_utokov = 1
						postavy[pos].pocet_obran = min(postavy[pos].koloakcie - postavy[pos].pocet_utokov,  int(postavy[pos].koloakcie / 2) + 1)
				else:
					postavy[pos].pocet_utokov = min(postavy[pos].koloakcie, int(postavy[pos].koloakcie / 2) + 1)
					postavy[pos].pocet_obran = min(postavy[pos].koloakcie - postavy[pos].pocet_utokov,  int(postavy[pos].koloakcie / 2) + 1)

				postavy[pos].save_pocet_utokov = postavy[pos].pocet_utokov
				postavy[pos].save_pocet_obran = postavy[pos].pocet_obran

			if postava1.akcie == postava2.akcie:
				na_tahu = randint(0, 1)
			else:
				na_tahu = 0 if postava1.akcie > postava2.akcie else 1

		utocnik = postavy[na_tahu]
		obranca = postavy[1 - na_tahu]

		pouzi_akcie = min(postavy[na_tahu].akcie, int(postavy[na_tahu].koloakcie / 2))
		
		def uder(utocnik, obranca, kocka_method=kocka1k6_plus):
			utmod = 0
			if obranca.pocet_obran > 0 and obranca.akcie > 0:
				ocmod = obranca.obranne_cislo + obranca.obrana_zbrane
				obranca.pocet_obran -= 1
				obranca.akcie -= 1
			else:
				ocmod = obranca.obranne_cislo - 3

			if obranca.zivoty < obranca.zivoty_max / 3:
				ocmod += obranca.postih_bs
			if utocnik.zivoty < utocnik.zivoty_max / 3:
				utmod += utocnik.postih_bs
			


			zranenie = utocnik.utocne_cislo + utmod + kocka_method() - ocmod - kocka1k6_plus()
			#raise Exception("zranenie = {}".format(zranenie))
			if zranenie > 0:
				obranca.zivoty -= max(0, zranenie + utocnik.utocnost)

			

		while pouzi_akcie:
			if utocnik.strategia == STRATEGIA_FAKEUTOK and pouzi_akcie >= 2 and utocnik.pocet_utokov >= 2:
				uder(utocnik, obranca, kocka_method=kocka2k6_plus)
				pouzi_akcie -= 2
				utocnik.pocet_utokov -= 2
				utocnik.akcie -= 2
			elif pouzi_akcie >= 1 and utocnik.pocet_utokov >= 1:
				uder(utocnik, obranca)
				log("{} bije {}".format(utocnik.meno, obranca.meno))
				pouzi_akcie -= 1
				utocnik.pocet_utokov -= 1
				assert(utocnik.pocet_utokov >= 0)
				utocnik.akcie -= 1
			else:
				pouzi_akcie = 0
				utocnik.akcie -= 1

		if pocet_subojov > POISTKA_POCET_UDEROV:
			raise NekonecnySubojException()

		pocet_subojov += 1
		na_tahu = 1 - na_tahu

	return postava1.bojaschopny()

def statistika(postava1, postava2, subojov=1000):
	vyhra1 = 0

	for _ in range(subojov):
		if suboj(postava1, postava2):
			vyhra1 += 1
		postava1.ozi()
		postava2.ozi()
	return vyhra1 / subojov


if __name__ == '__main__':
	print("Ten druhý súbor treba spustiť.")
	logging = True
	#(meno, zivoty_max, utocne_cislo, obranne_cislo, obrana_zbrane ,
	# utocnost, odolnost, iniciativa, strategia):
	magic = Bojic("Merlin", 50, 10, 10, 0, -5, 11, 12, 0)
	skrat = Bojic("Škrato", 50, 30, 15, 0, 10, 11, 0, 0)

	if suboj(magic, skrat):
		log("vyhral " + magic.meno)
	else:
		log("vyhral " + skrat.meno)
	