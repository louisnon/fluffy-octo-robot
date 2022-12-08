import math as m

def evite_coins(angle_entree,map):
	ecart=1000
	eps=25
	if m.isnan(angle_entree):
		return angle_entree
	if min(map[int(angle_entree)-eps],map[int(angle_entree)+eps])>2*ecart:
		eps=15
	if map[int(angle_entree)-eps]<map[int(angle_entree)]-ecart:
		if map[int(angle_entree)-eps]<ecart:
			return angle_entree+10
		else:
			return angle_entree+5
	if map[int(angle_entree)+eps]<map[int(angle_entree)]-ecart:
		if map[int(angle_entree)+eps]<ecart:
			return angle_entree-10
		else:
			return angle_entree-5
	return angle_entree
	
def evite_murs(angle_cible,delta,map):
	c=0
	for i in range(1,60):
		if map[i]<delta:
			c+=1
		if c>5:
			print("mur")
			return -45
		if map[-i]<delta:
			c-=1
		if c<-5:
			print("mur")
			return 45
	return angle_cible

def evite_obstacle(angle_cible,map):
	if m.isnan(angle_cible):
		return 0
	if abs(angle_cible)>45:
		signe=int(int(angle_cible)/int(abs(angle_cible)))
		c=0
		for i in range(25,int(abs(angle_cible))):
			if map[signe*i][1]<400:
				c+=1
		if c>10:
			return signe*1
	return 0
			
