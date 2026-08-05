# Bean & Brew ☕

Application web de coffee shop développée avec :

* Python
* Flask
* MySQL
* HTML
* CSS
* JavaScript
* bcrypt

---

## 1. Prérequis

Avant de commencer, installer :

* Python 3.9+
* MySQL Server 8.0
* MySQL Workbench
* Git (optionnel)

Le projet a été développé avec Python 3.9.

---

## 2. Structure du projet

 text
html_python/
│
├── main.py
├── coffee_shop_database.sql
├── README.md
├── .env
├── requirements.txt
│
├── static/
│   ├── script.js
│   ├── style.css
│   └── seller.css
│
└── templates/
    ├── index.html
    ├── login.html
    ├── register.html
    ├── orders.html
    ├── seller.html
    ├── add_product.html
    └── edit_product.html
 

---

# 3. Créer l'environnement Python

Ouvrir un terminal dans le dossier du projet.

 bash
python -m venv venv
 

Activer l'environnement virtuel sous Windows :

 bash
venv\Scripts\activate
 

Si tout fonctionne, le terminal affiche :

 text
(venv)
 

---

# 4. Installer les dépendances

Installation complète :

 bash
pip install Flask mysql-connector-python bcrypt python-dotenv
 

Les bibliothèques utilisées sont :

 text
Flask
mysql-connector-python
bcrypt
python-dotenv
 

---

# 5. Fichier requirements.txt

Pour installer toutes les dépendances automatiquement, créer :

 text
requirements.txt
 

avec :

 text
Flask
mysql-connector-python
bcrypt
python-dotenv
 

Puis utiliser :

 bash
pip install -r requirements.txt
 

---

# 6. Installer la base de données

Ouvrir MySQL Workbench.

Ouvrir :

 text
coffee_shop_database.sql
 

Exécuter tout le script.

La base suivante sera créée :

 text
coffee_shop
 

Avec les tables :

 text
users
categories
products
orders
order_items
 

---

# 7. Vérifier la base

Dans MySQL :

 sql
USE coffee_shop;
 

Puis :

 sql
SHOW TABLES;
 

Tu dois obtenir :

 text
categories
order_items
orders
products
users
 

Vérifier les produits :

 sql
SELECT * FROM products;
 

La table `products` contient notamment :

 text
id
name
description
price
image
category_id
active
 

---

# 8. Configuration MySQL

À la racine du projet, créer un fichier :

 text
.env
 

Exemple :

 env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=TON_MOT_DE_PASSE
DB_NAME=coffee_shop
 

Remplacer :

 text
TON_MOT_DE_PASSE
 

par le mot de passe MySQL utilisé sur ton ordinateur.

---

# 9. Sécurité du fichier .env

Ne jamais envoyer `.env` sur GitHub.

Créer un fichier :

 text
.gitignore
 

avec :

 text
.env
venv/
__pycache__/
*.pyc
 

---

# 10. Lancer l'application

Vérifier que l'environnement virtuel est activé :

 bash
venv\Scripts\activate
 

Puis :

 bash
python main.py
 

Flask doit afficher une adresse similaire à :

 text
http://127.0.0.1:5000
 

Ouvrir cette adresse dans le navigateur.

---

# 11. Arrêter l'application

Dans le terminal :

 text
CTRL + C
 

Pour quitter l'environnement virtuel :

 bash
deactivate
 

---

# 12. Relancer le projet

À chaque nouvelle utilisation :

 bash
cd chemin\vers\html_python
 

Puis :

 bash
venv\Scripts\activate
 

Puis :

 bash
python main.py
 

---

# 13. Gestion des produits

La colonne :

 text
active
 

permet de gérer la disponibilité des produits.

### Produit disponible

 text
active = 1
 

Le produit est visible et peut être commandé.

### Produit indisponible

 text
active = 0
 

Le produit est conservé dans la base mais n'est plus disponible pour les clients.

Cela permet notamment de conserver les références nécessaires aux anciennes commandes.

---

# 14. Statuts des commandes

Les commandes utilisent actuellement les statuts :

 text
pending
preparing
ready
done
cancelled
 

Correspondance :

| Statut    | Signification  |
| --------- | -------------- |
| pending   | En attente     |
| preparing | En préparation |
| ready     | Prête          |
| done      | Terminée       |
| cancelled | Annulée        |

Les commandes terminées ne sont plus affichées dans le dashboard des commandes actives.

---

# 15. Utilisateur vendeur

Un utilisateur vendeur doit avoir :

 text
role = seller
 

Vérifier les utilisateurs :

 sql
SELECT id, username, email, role
FROM users;
 

Exemple :

 text
seller_test | seller@test.fr | seller
 

Le mot de passe doit être enregistré sous forme de **hash bcrypt**.

Ne jamais stocker un mot de passe en clair.

---

# 16. Problèmes fréquents

## Flask ne démarre pas

Vérifier que l'environnement virtuel est actif :

 bash
venv\Scripts\activate
 

Puis :

 bash
python main.py
 

---

## TemplateNotFound

Exemple :

 text
jinja2.exceptions.TemplateNotFound
 

Vérifier que les fichiers HTML sont dans :

 text
templates/
 

Exemple :

 text
templates/seller.html
 

---

## BuildError

Exemple :

 text
Could not build url for endpoint
 

Vérifier que le nom utilisé dans :

 python
url_for("nom_route")
 

correspond bien à la fonction Flask.

---

## MySQL Error 2013

Si MySQL affiche :

 text
Lost connection to MySQL server during query
 

Vérifier que le serveur MySQL est toujours démarré.

Sous Windows :

 text
Win + R
 

Puis :

 text
services.msc
 

Rechercher le service MySQL et vérifier qu'il est démarré.

---

## Waiting for table metadata lock

Si MySQL affiche :

 text
Waiting for table metadata lock
 

utiliser :

 sql
SHOW PROCESSLIST;
 

Identifier la requête bloquante.

Si nécessaire :

 sql
KILL ID;
 

Remplacer `ID` par l'identifiant de la connexion bloquante.

---

# 17. Installation complète sur un nouvel ordinateur

Pour installer Bean & Brew sur une nouvelle machine :

### Étape 1

Installer Python.

### Étape 2

Installer MySQL Server.

### Étape 3

Installer MySQL Workbench.

### Étape 4

Récupérer le projet.

### Étape 5

Créer l'environnement virtuel :

 bash
python -m venv venv
 

### Étape 6

Activer l'environnement :

 bash
venv\Scripts\activate
 

### Étape 7

Installer les dépendances :

 bash
pip install -r requirements.txt
 

### Étape 8

Importer :

 text
coffee_shop_database.sql
 

dans MySQL Workbench.

### Étape 9

Créer `.env` :

 env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=TON_MOT_DE_PASSE
DB_NAME=coffee_shop
 

### Étape 10

Lancer :

 bash
python main.py
 

### Étape 11

Ouvrir :

 text
http://127.0.0.1:5000
 

---

# 18. Commandes principales

### Création environnement

 bash
python -m venv venv
 

### Activation

 bash
venv\Scripts\activate
 

### Installation

 bash
pip install -r requirements.txt
 

### Lancement

 bash
python main.py
 

### Arrêt

 text
CTRL + C
 

### Désactivation

 bash
deactivate
 

---

# 19. Évolutions prévues

Fonctionnalités pouvant être ajoutées plus tard :

* 🗃️ Archive des anciennes commandes
* 🔎 Recherche dans les commandes archivées
* 📊 Statistiques de ventes
* 📈 Chiffre d'affaires
* 👥 Gestion avancée des utilisateurs
* 📦 Gestion des stocks
* 🔐 Amélioration de la sécurité
* 💳 Système de paiement
* 📱 Amélioration responsive
* 🚀 Déploiement en ligne

---

## Bean & Brew

Projet personnel de développement web avec Python, Flask et MySQL.
