# Add domaine 
## Réservation du nom de domaine sur OVH
### Paramétrage du DNS (1)
Pour associer votre nom de domaine (acheté chez OVH) à votre application Heroku, vous devrez mettre à jour les enregistrements DNS dans le panneau de gestion d'OVH. Voici un guide étape par étape pour le faire :

- Connectez-vous à votre compte OVH :
Accédez à https://www.ovh.com/manager/ et connectez-vous avec vos identifiants.

- Accédez à votre zone DNS :

Dans le tableau de bord, cliquez sur l'onglet "Web".
Cliquez sur votre nom de domaine sotisimmo.app dans la section "Vos domaines".
Dans le menu de gauche, cliquez sur "Zone DNS".
Modifier l'enregistrement A :

- Trouvez l'enregistrement A pour sotisimmo.app et cliquez sur le bouton "modifier".
Supprimez l'adresse IP actuelle (213.186.33.5) et remplacez-la par l'adresse IP associée à votre application Heroku. (Heroku n'utilise pas les enregistrements A pour les domaines racine, donc cette étape est juste pour s'assurer que l'enregistrement A n'interfère pas avec le CNAME que nous allons configurer.)
Ajouter un enregistrement CNAME :

- Cliquez sur le bouton "Ajouter un enregistrement".
Sélectionnez "CNAME" comme type d'enregistrement.
Dans le champ "Sous-domaine", saisissez www.
Dans le champ "Cible", saisissez la valeur DNS fournie par Heroku : shrouded-loon-nlebyptg33bce5mc9mbwgpom.herokudns.com.
Cliquez sur "Valider".
Supprimez les enregistrements CNAME inutiles :

Si vous voyez un autre enregistrement CNAME pour www.sotisimmo.app pointant vers sotisimmo.app, supprimez-le pour éviter tout conflit.
SSL/TLS :

Heroku fournit des certificats SSL pour les domaines personnalisés. Assurez-vous que le cryptage SSL est activé pour votre application Heroku. Si ce n'est pas le cas, vous devrez le configurer.
Patientez :

Les modifications DNS peuvent prendre un certain temps pour se propager à travers l'Internet. Cela peut prendre de quelques minutes à 48 heures.
Testez votre domaine :

Une fois que vous avez attendu un certain temps, ouvrez un navigateur et accédez à www.sotisimmo.app. Vous devriez voir votre application Heroku.

### Paramétrage du DNS (2)
Le message d'erreur que vous recevez indique que vous avez déjà des enregistrements DNS pour le sous-domaine www.sotisimmo.app, et ces enregistrements entrent en conflit avec l'ajout d'un nouvel enregistrement CNAME pour le même sous-domaine.

Pour résoudre ce problème :

Supprimez les enregistrements existants pour www.sotisimmo.app :

Dans votre panneau de gestion OVH, trouvez les enregistrements DNS pour www.sotisimmo.app.
Supprimez les enregistrements TXT pour www.sotisimmo.app ayant comme cible "3|welcome" et "l|fr".
Assurez-vous qu'il n'y a pas d'autres enregistrements (comme A, CNAME, etc.) pour www.sotisimmo.app. Si c'est le cas, supprimez-les également.
Ajoutez l'enregistrement CNAME :

Après avoir supprimé les enregistrements existants, ajoutez un nouvel enregistrement CNAME avec les détails que vous avez mentionnés :
Type de champ : CNAME
Domaine : www.sotisimmo.app.
Cible : shrouded-loon-nlebyptg33bce5mc9mbwgpom.herokudns.com.
Vérifiez vos enregistrements :

Assurez-vous que l'enregistrement CNAME a été correctement ajouté et qu'il n'y a pas d'autres enregistrements conflictuels pour www.sotisimmo.app.
Patientez :

Les modifications apportées à la zone DNS peuvent prendre un certain temps pour se propager sur Internet. Vous devriez voir les changements dans quelques heures, mais cela peut parfois prendre jusqu'à 48 heures.
Testez votre domaine :

Après avoir attendu, ouvrez un navigateur et accédez à www.sotisimmo.app. Vous devriez voir votre application Heroku.
C'est tout ! Vous avez maintenant correctement configuré votre nom de domaine avec Heroku.

### Ajout d'une entrée CNAME sur OVH
sous-domaine : www
TTL : par défaut
Cible : lien donné dans mon appli Heroku (DNS Target)
--> Attente de la propagation.

### Ajout d'un certificat SSL sur Heroku
Gestion automatique par Heroku.