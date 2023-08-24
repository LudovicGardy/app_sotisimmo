# Domaine via Ionos (1&1)

## Achat d'un domaine sur Ionos (avec protection)
sotisanalytics.immo

## Ajout d'un domaine sur Heroku 
Dans les paramètres de l'application (sotisimmo), choisir **Add domain**, et remplir :
- Domain name: www.sotisanalytics.immo
Attention: ne pas oublier de mettre "www" !

Une fois le domaine ajouté, Heroku donne un "DNS Target" qu'il faut ajouter à Ionos dans un champ CNAME.

## Ajout d'une entrée CNAME sur Ionos
sous-domaine (nom d'hôte) : www
Cible (pointe vers): lien donné dans mon appli Heroku (DNS Target)
TTL : par défaut (1 heure)
--> Attente de la propagation (quelques secondes ou minutes).

Zone DNS finale:
TYPE	NOM D’HÔTE	VALEUR	SERVICE	ACTIONS
CNAME	_domainconnect	_domainconnect.ionos.com	Domain Connect	
MX	@	mx00.ionos.fr	Mail	
MX	@	mx01.ionos.fr	Mail	
TXT	@	"v=spf1 include:_spf-eu.ionos.com ~all"	Mail	
CNAME	autodiscover	adsredir.ionos.info	Mail	
A	@	217.160.0.89	Webhosting	
AAAA	@	2001:8d8:100f:f000:0:0:0:258	Webhosting	
CNAME	www	symmetrical-spire-ud68oghfef21462134kglro1.herokudns.com	-	

# Ajout d'un certificat SSL sur Heroku
Activer la gestion automatique par Heroku.
--> Attente de la propagation (quelques secondes ou minutes)
Ceci permet d'obtenir le https://. Il est géré par Heroku, pas la peine de le configurer auprès du fournisseur de nom de domaine (malgré l'alerte donné sur le site du fournisseur).

# Domaine via OVH
Même procédure que pour Ionos (quelques secondes ou minutes pour mettre le tout en oeuvre).
Contrairement à Ionos, OVH ne supprime pas automatiquement les entrées qui entrent en conflit avec le CNAME donné par Heroku, il faut les supprimer manuellement. J'ai du supprimer : 
-  TXT pour www.sotisimmo.app ayant comme cible "3|welcome" et "l|fr".

Zone DNS finale:
Domaine	TTL	Type Cible	
sotisimmo.app. 0 NS dns13.ovh.net.
sotisimmo.app. 0 NS ns13.ovh.net.
sotisimmo.app. 0 MX mx3.mail.ovh.net.
sotisimmo.app. 0 MX mx4.mail.ovh.net.	
sotisimmo.app. 0 TXT "1|www.sotisimmo.app"
sotisimmo.app. 0 SPF "v=spf1 include:mx.ovh.com ~all"	
sotisimmo.app. 0 CNAME vast-termite-ud68oghfef21462134kglro1.herokudns.com.	




