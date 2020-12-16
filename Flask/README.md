# Projet Visualisation M1

## Le Cinéma Francophone

Nous avons choisi de nous baser sur les données des acteurs et films francophones pour notre projet. Ces données sont similaires aux données Marvel, étant donné qu'il s'agit à l'origine d'un graphe nœud-lien dont les sommets sont de deux types&nbsp;: 
* Les **acteurs** (Nom, Prénom, etc.)
* Les **films** (Titre, Année de sortie, Langue originale, Note moyenne, Popularité, Budget, Durée, etc.)

Ces sommets sont reliés par des arêtes qui correspondent aux acteurs ayant joués dans les films.

Sur la base de ce graphe, nous avons construit le résau social des acteurs, qui lie les acteurs ayant joué ensemble dans au moins un film (les arêtes ont un poids correspondant au nombre de rencontres entre les deux acteurs).

### Rendu final

Depuis le rendu intermédiaire, nous avons essayé sans succès d'implémenter le bar-chart-race. Cela dit, ce n'est pas forcément une grande perte étant donné que nous n'allions pas en tirer quelconque information sur le cinéma francophone.

Nous avons amélioré les visualisations déjà présentes dans le rendu intermédiaire. Par exemple, les informations sur le nombre de films en commun entre deux acteurs dans la heatmap s'affiche désormais directement au niveau du pointeur au survol de la souris. Nous avons aussi ajouté deux options sur les graphes nœud-lien&nbsp;:

* Il est désormais possible d'afficher ou de masquer les noms des acteurs secondaires dans le graphe.

* Un menu déroulant permet de basculer sur le graphe de n'importe quel acteur présent dans le réseau.

##### Routes correspondantes aux visualisations

* graphe nœud-lien à force : "/films/<nom de l'acteur>" (e.g. "/films/Jean-Paul%20Rouve")
Ce graphe est dynamique, on peut déplacer les acteurs et/ou les films avec la souris. Attention, malgré un travail d'optimisation de l'affichage, le graphe pour les acteurs les plus prolifiques perd en lisibilité (e.g. Gérard Depardieu, Brigitte Bardot).

* durée des films : "/runtime-scatter"
Ce graphique nous permet d'observer l'évolution de la durée des films dans le temps.

* nombre de films : "/nbfilms-scatter"
Ce graphique nous permet d'observer l'évolution du nombre de films réalisés par année.

* heatmap : "/actors-heatmap/<nombre d'acteurs>" (e.g. "/actors-heatmap/40")
Ce graphe est dynamique dans le sens où on peut voir le nombre précis de films en commun entre deux acteurs dans un encadré en-dessous de la heatmap. Les valeurs "raisonnables" pour une bonne lisibilité de la matrice sont les entiers entre 20 et 80. Mais nous n'avons pas interdit les autres valeurs pour le moment.

* communautés : "/communities"
Cette page est l'occasion d'aborder le sujet des communautés dans un réseau social. On y inclut des captures d'écran de graphes générés sur Tulip afin de ne pas faire de calculs inutiles lors de chaque visite. En revanche, le dernier graphe, qui correspond à une construction naïve de communauté en fonction du nombre de films en commun, est quant à lui dynamique. Les coordonnées sont pré-calculées par Tulip, et les noms et dates de sortie des films sont affichés au survol de la souris sur les arêtes du graphe.

### Rendu intermédiaire

#### Lancer le programme

À priori, si la machine sur laquelle on se trouve utilise les mêmes normes que Linux pour les chemins de fichier, il ne devrait pas y avoir besoin de modifier les routes dans le fichier webapp.py. En revanche, sous Windows, il est possible qu'elles doivent être modifiées "à la main" dans le fichier webapp.py.

S'il y avait un vrai problème pour lancer le programme, la version la plus récente de l'application est accessible à l'adresse suivante&nbsp;: https://tbaranger.pythonanywhere.com/.

#### Ce que nous avons fait

Nous avons développé deux visualisations. La première est un **graphe nœud-lien à force**. Il nous permet de visualiser l'ensemble des films dans lequel un acteur a joués, ainsi que les autres acteurs ayant joué dans ces films. Par soucis de visibilité, nous affichons le nom de l'acteur principal en grand, ainsi que le titre des films dans lesquels il figure. On ne peut pas lire le nom des autres acteurs directement sur ce graphe.

La seconde visualisation est une matrice de co-occurence des acteurs les plus prolifiques (sommets de plus haut degré dans le graphe du réseau social). Il s'agit d'une **heatmap** dont la taille est spécifiée par l'utilisateur dans l'URL.

##### Routes correspondantes aux visualisations

* graphe nœud-lien à force : "/films/<nom de l'acteur>" (e.g. "/films/Jean-Paul%20Rouve")
Ce graphe est dynamique, on peut déplacer les acteurs et/ou les films avec la souris. Attention, malgré un travail d'optimisation de l'affichage, le graphe pour les acteurs les plus prolifiques perd en lisibilité (e.g. Gérard Depardieu, Brigitte Bardot).

* heatmap : "/actors-heatmap/<nombre d'acteurs>" (e.g. "/actors-heatmap/40")
Ce graphe est dynamique dans le sens où on peut voir le nombre précis de films en commun entre deux acteurs dans un encadré en-dessous de la heatmap. Les valeurs "raisonnables" pour une bonne lisibilité de la matrice sont les entiers entre 20 et 80. Mais nous n'avons pas interdit les autres valeurs pour le moment.

#### Ce que nous aimerions ajouter

##### Site web

Il faudrait créer une page d'accueil pour accéder aux visualisations autrement que par l'URL, et ainsi pouvoir naviguer dans l'application de manière plus intuitive.

##### Visualisations

Concernant les visualisations déjà existantes, nous aimerions faire quelques additions. Par exemple, nous aimerions que le nom des acteurs s'affichent au survol de la souris sur le graphe nœud-lien. Il est déjà possible dans le code d'afficher seulement le nom des acteurs ayant un degré supérieur à 1, c'est-à-dire les acteurs ayant plus d'un film en commun avec l'acteur principal, mais nous préférons pour l'instant la version plus épurée avec seulement les titres de films en plus du nom de l'acteur principal. Nous aimerions également pouvoir faire en sorte d'avoir accès au graphe nœud-lien entre deux acteurs et leurs films communs lorsque l'on clique sur la case correspondante dans la heatmap.

Une autre visualisation, sur laquelle nous n'avons pas eu le temps de travailler, consisterait à visualiser de façon dynamique l'évolution dans le temps des acteurs ayant joué dans le plus de films. Nous avons en tête un diagramme en barre horizontal dans lequel figurerait par ordre décroissant du nombre de films, et qui s'actualiserait de façon automatique selon les années. Voici un exemple de ce que l'on aimerait reproduire&nbsp;: https://observablehq.com/@d3/bar-chart-race.
