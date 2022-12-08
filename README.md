# Stratégie

## Stratégie globale

Tout simplement, la voiture ira à la position la plus éloignée de lui.

## Filtrage

Pour éviter les coins, on filtre d'abord les distances mesurées par lidar. Après le filtrage, la distance filtré dans une direction $\alpha$ est $d_f=moyen(d[\alpha-30],d[\alpha+30])$

## Loi de la direction

Pour la voiture, il n'y a que 3 angles à tourner. Soit $\theta$ la direction où la distance entre l'obstacle et la voiture est maximale. Alors, la direction $\alpha$ pour la voiture est :

- si $|\theta|<15$ alors $\alpha=0$
- si $15\le|\theta|<50$ alors $\alpha=\alpha_1$
- si $|\theta|\ge50$ alors $\alpha=\alpha_2$

Dans la course, on a pris $|\alpha_1|\approx14$ et $|\alpha_2|=30$, de plus, la signe de $\alpha_i$ dépend de la signe de $\theta$

## Loi de la vitesse

Pour la loi de la vitesse, Nous considérons la distance $d$ de l'obstacle devant la voiture et l'angle de braquage $\alpha$ de la voiture. On limite la vitesse de la voiture entre $v_{min}$ et $v_{max}$

La vitesse de la voiture $v$ est donc :
$$
v=v_{min}+(v_{max}-v_{min})\times(1-\exp(-d/d_{max}))\times(1-|\alpha|/\alpha_{max})
$$
avec $d_{max}$ la distance maximale détecté par lidar pendant la cours, et $\alpha_{max}$ pour nous c'est 30°.

# Structure des données

# Les codes

## main.py

On utilise `main.py` pour la course. Après avoir lancé `main.py` , le lidar va d'abord tourner. Vous pouvez cliquer '**g**' pour lancer la voiture et '**s**' pour l'arrêter. Le programme va vous donner deux fichier pour affichage les données.

## evitement.py

On a écrit des fonctions supplémentaires pour éviter différents types de l'obstacle, mais on ne les a pas utilisé dans la course" 

## filtrage.py

On utilise `filtrage.py` pour filtrer les données du lidar.

## stop_lidar.py

Après avoir arrêté le programme, le lidar ne peut pas être arrêté automatiquement. Il faut lancer ce code pour arrêter le lidar.

## show_result.py

Après avoir lancé `main.py` , on a deux fichier de données. En lançant `show_result.py`, on peut obtenir deux figure:

*axis x = temps*

- figure 1: 
  - sous-figure 1 : la distance entre l'obstacle et la voiture (la distance détecté par lidar après le filtrage)
  - sous-figure 2 : la vitesse qu'on donne au moteur

- figure 2:
  - sous-figure 1 : la direction où la distance entre l'obstacle et la voiture est maximale.
  - sous-figure 2 : la direction qu'on donne au servo-moteur.



## config.json

On met toutes les configurations dans ce fichier. Vous pouvez changer les valeurs dans ce fichier pour changer les configurations de la voiture.
