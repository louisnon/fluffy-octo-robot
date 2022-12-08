def filtrage(map, largeur_convolution):
	n=len(map)
	mapt=[0 for i in range(n)]
	for i in range(n):
		for k in range(-largeur_convolution,largeur_convolution):
			mapt[i]+=map[(i+k)%n]
		mapt[i]=mapt[i]/(2*largeur_convolution+1)
	return mapt
