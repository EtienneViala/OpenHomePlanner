# OpenHomePlanner - Suivi du developpement

Derniere mise a jour : 2026-06-30

---

# Etat global

Version de travail : V0.6 en cours

OpenHomePlanner est actuellement capable d'importer un plan DXF, de l'afficher comme fond de plan, de placer des objets electriques simples et de gerer leur selection.

Le travail recent porte sur la structuration du DXF et la gestion des calques, afin de preparer les fonctions de filtrage, de reconnaissance et d'annotation.

---

# Fonctionnalites terminees

## V0.1 - Base application

- Fenetre principale PySide6
- Canvas central
- Grille de travail
- Navigation de base dans la scene

## V0.2 - Premiers objets metier

- `BaseObject`
- Objets electriques de base
- Premiere representation graphique des prises
- `GraphicsFactory`

## V0.3 - Projet et selection

- `Project`
- `ObjectManager`
- `SelectionManager`
- Selection des objets
- Deplacement des objets
- Panneau de proprietes

## V0.4 - Systeme d'outils

- Classe de base `Tool`
- `ToolManager`
- `SelectTool`
- `OutletTool`
- Placement de prises depuis un outil
- Panneau bibliotheque

## V0.5 - Import DXF

- Import DXF via `ezdxf`
- Lecture des entites `LINE`
- Lecture des entites `CIRCLE`
- Lecture des entites `LWPOLYLINE`
- Lecture des blocs `INSERT`
- Affichage du plan DXF dans le canvas
- Plan DXF place derriere les objets du projet

## V0.6 - Gestion des calques DXF

- Recuperation automatique des calques du DXF
- Stockage des calques dans `DXFDocument`
- Modele `DXFLayer`
- Panneau Qt `Layers`
- Liste des calques avec cases a cocher
- Masquage et affichage d'un calque sans recharger le DXF
- Rendu DXF decoupe par calque dans `DXFItem`

---

# En cours

## Stabilisation V0.6

- Tester l'import reel avec `rochette.dxf` dans un environnement ou `ezdxf` est installe
- Verifier le comportement du panneau `Layers` sur un fichier DXF contenant beaucoup de calques
- Verifier la coherence entre les calques lus dans la table DXF et les calques references par les entites
- Decider si les calques doivent etre groupes ou filtres par type dans l'interface

---

# Points techniques a surveiller

- Le modele ne doit jamais dependre de Qt
- Le canvas doit rester une vue et ne pas contenir de logique metier
- Les outils doivent creer des objets metier uniquement
- `GraphicsFactory` doit rester le point de creation des objets graphiques du projet
- Le DXF doit rester un fond de plan verrouille
- Les objets du projet doivent rester au-dessus du DXF

---

# Dette technique identifiee

- `ui/main_window.py` contient des imports dupliques ou ambigus, notamment autour de `Project`
- `Canvas.add_outlet()` cree encore directement un `OutletItem`, ce qui contourne l'architecture cible
- Certains textes dans les fichiers affichent des problemes d'encodage
- Les fichiers `__pycache__` ne devraient pas etre suivis par Git
- `requirements.txt` doit rester synchronise avec les imports reels du projet

---

# Prochaines etapes proposees

## Court terme

- Nettoyer les imports de `ui/main_window.py`
- Supprimer ou refactorer `Canvas.add_outlet()`
- Ajouter un `.gitignore`
- Installer les dependances puis tester l'import DXF complet
- Verifier visuellement le panneau `Layers`

## V0.7 - Reconnaissance du plan

- Reconnaissance automatique des murs
- Reconnaissance des portes
- Reconnaissance des fenetres
- Accrochage intelligent des objets
- Rotation automatique des equipements selon les murs

## V0.8 - Equipements electriques

- Interrupteurs
- Points lumineux
- Prises RJ45
- Prises TV
- Tableau electrique
- Circuits electriques

## V0.9 - Cablage

- Dessin des cables
- Calcul des longueurs
- Calcul des gaines
- Calcul des saignees

## V1.0 - Dossier projet

- Sauvegarde et chargement d'un projet complet
- Export PDF
- Export SVG
- Export DXF
- Impression
- Liste du materiel
- Schema unifilaire
- Schema architectural

---

# Journal des modifications

## 2026-06-30

- Ajout d'un gestionnaire de calques DXF
- Ajout du modele `DXFLayer`
- Extension de `DXFDocument` pour stocker les calques
- Mise a jour de `DXFImporter` pour lire les calques
- Mise a jour de `DXFItem` pour peindre par calque
- Ajout du panneau `Layers`
- Connexion du panneau `Layers` au `Canvas`
- Ajout de `ezdxf` dans `requirements.txt`
- Creation de ce fichier de suivi
