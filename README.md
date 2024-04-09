# Hackathon Meteofrance : Cap Prevention Meteo

Projet pour le Hackathon Meteofrance https://meteo.data.gouv.fr/hackathon de l'équipe Cap Prevention Meteo

### Défi : 
Anticiper, prévenir et gérer les risques naturels (incendies, feux de forêt, inondations, etc.) 

### Objectif du projet et problématique résolue :  

La connaissance du niveau d’un cours d’eau (eau douce) est essentielle afin d’anticiper, prévenir et gérer les risques de sécheresses et d’inondation. L’eau douce est prélevée par de multiples secteurs : industries, centrales nucléaires (qui fournissent de l’électricité), agriculture, usage domestique. Le niveau d’eau douce dépend de facteurs météorologiques et des prélèvements effectués par les industries et l’agriculture. À cause des sécheresses répétées et à venir, les industries prélevant de l’eau sont mises à rude épreuve en été, lorsque les débits d’étiage sont trop faibles. Par exemple, les centrales nucléaires ne peuvent réglementairement pas prélever de l’eau en dessous d’un certain débit normatif. De même les agriculteurs sont soumis à des autorisations de prélèvements. Afin de prévoir leur activité en cas de sécheresse, nous proposons de prédire les débits des fleuves à quelques jours près en prenant en compte les prévisions météorologiques, et informer les intéressés des dépassements d’étiage, ainsi que leur durée. 

 

### Approche adoptée : 
À partir des données de débits historiques des stations hydrologiques Hub’Eau sur un fleuve, et des données pluviométriques historiques des stations MétéoFrance, nous entraînons un modèle de machine learning permettant de prédire jusqu’à J+X le débit à un endroit donné d’un cours d’eau. Un modèle unique est créé pour chaque station hydrologique. 
En utilisant les prédictions pluviométriques Arpege les plus proches des stations MétéoFrance, nous inférons pour les 3 prochains jours les débits des cours d’eau. 
Une carte permet aux utilisateurs de visualiser ces prédictions, et d’obtenir des alertes lorsque le débit est en dessous (sécheresse) ou au-dessus (inondation) d’un seuil choisi. Grâce à l’utilisation du modèle Arpege, nous pouvons également estimer un minimum de durée de la sécheresse. 

 

### Usagers pressentis :  
Les utilisateurs sont tous les acteurs de prélèvement d’eau douce (agriculteurs, industriels, centrales électriques, consommateurs domestiques) 

Membres de l’équipe et leurs compétences :  
- Thierry MANDON : développeur informatique 
- Virgil COURVALET : dev front-end 
- Mélodie PAYEN : développeur informatique 
- Sarah GRIB : dev front-end 
- José Manuel FLORES PEREZ : rapporteur 
- Paul GERSBERG : data scientist 
- Karine SUN : rapportrice 

## Arborescence  
- data/ : fichiers de données issus des bases de données MeteoFrance et Hub'Eau.Eaufrance
- projet Django

L'algorithme de machine learning s'effectue dans ce sens 
1.  recuperation-meteo-affluents.ipynb : récupération de certaines stations hydrologiques et météorologiques (les plus proches des sources), sur les affluents de la Garonne
2. machine-leraning.ipynb : entraînement d'une régression linéaire et d'un réseau de neurone jusqu'à J+5 
3. inference-arpege.ipynb : inférer la régression linéaire à J+2 en utilisant la prédiction Arpege la plus proche des stations météo

