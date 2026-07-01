# OpenHomePlanner - Suivi du developpement

Derniere mise a jour : 2026-07-01

---

# Etat global

Version de travail : V0.7.0 finalisee

OpenHomePlanner est actuellement capable d'importer un plan DXF, de l'afficher comme fond de plan, de placer des objets electriques simples, de gerer leur selection, de proposer une experience utilisateur stabilisee, d'afficher une preview temporaire pour les outils de placement et de stocker un modele architectural pur Python dans le Project.

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
- Import DXF depuis `Fichier > Importer un DXF...`
- Ajustement automatique de la vue avec `fitInView()`
- Couleurs de calques recuperees et utilisees au rendu
- Etat de verrouillage des calques conserve dans le modele
- Gestion propre des DXF invalides, vides, blocs manquants et entites non supportees

## V0.6.1 - Amelioration de l'experience utilisateur

- Ajout d'une vraie toolbar synchronisee avec le `ToolManager`
- Activation des outils Selection et Prise depuis la toolbar
- Synchronisation de la toolbar lors du changement d'outil depuis la bibliotheque
- Ajout d'une barre d'etat permanente
- Affichage de l'outil actif, des coordonnees souris, du snap et du zoom
- Snap activable/desactivable depuis la toolbar
- Placement libre quand le snap est desactive
- Affichage/masquage de la grille
- Methode generique `Canvas.fit_to_content()`
- Ajustement de la vue apres import DXF et via `Ctrl+0`
- Suppression propre des objets via `Project.remove_object(...)`
- Suppression par touche `Suppr`
- Menu contextuel avec `Supprimer` et `Proprietes`
- Retour a l'outil Selection avec `ESC`
- Selection de tous les objets avec `Ctrl+A`

## V0.6.2 - Ghost preview generique

- Ajout de `PreviewDefinition`, donnee pure sans dependance Qt
- Ajout de `PreviewItem` pour afficher un apercu temporaire non selectionnable
- Ajout de `PreviewFactory` pour creer les items temporaires de preview
- Ajout de `PreviewManager` pour gerer creation, mise a jour et destruction
- Integration du cycle de preview dans `ToolManager`
- Ajout de primitives de vue dans `Canvas` pour afficher, deplacer et supprimer la preview
- Ajout d'une preview semi-transparente pour `OutletTool`
- Suppression automatique de la preview lors du changement d'outil
- Aucun objet metier cree avant le clic utilisateur

## V0.7.0 - Modele architectural

- Ajout de `House` pour representer une habitation complete
- Ajout de `Floor` pour representer un etage
- Ajout de `Room` pour representer une piece
- Ajout de `Wall` pour representer un mur sans dessin
- Ajout de `Opening`, `Door` et `Window` pour preparer les ouvertures
- Integration de `House` et `DXFDocument` dans `Project`
- Ajout d'une serialisation simple avec `to_dict()` / `from_dict()`
- Preparation de `GraphicsFactory` avec un registre extensible
- Ajout de tests unitaires independants de Qt
- Aucun `WallTool`, `WallItem`, dessin, analyse DXF ou reconnaissance automatique

---

# En cours

## Stabilisation V0.7.0 terminee

- Import reel teste avec `rochette.dxf` : 191 entites importees
- Calques detectes sur le fichier de test : `0`, `Defpoints`, `Layer 1`
- Panneau `Layers` synchronise automatiquement apres import
- Masquage/affichage des calques sans rechargement du DXF
- Toolbar, barre d'etat, snap, grille et raccourcis clavier connectes
- Suppression d'objets validee via le flux Project/ObjectManager/Canvas
- Ghost preview validee par compilation Python
- Check automatique disponible : `py scripts/check_v062.py rochette.dxf`
- Modele architectural valide par tests unitaires sans Qt

---

# Points techniques a surveiller

- Le modele ne doit jamais dependre de Qt
- Le canvas doit rester une vue et ne pas contenir de logique metier
- Les outils doivent creer des objets metier uniquement
- `GraphicsFactory` doit rester le point de creation des objets graphiques du projet
- Le DXF doit rester un fond de plan verrouille
- Les objets du projet doivent rester au-dessus du DXF
- Les previews doivent rester temporaires, hors `Project` et hors selection
- Le modele architectural doit rester pur Python et ne doit pas declencher de dessin

---

# Dette technique identifiee

- Certains textes dans les fichiers affichent des problemes d'encodage
- `requirements.txt` doit rester synchronise avec les imports reels du projet

---

# Prochaines etapes proposees

## Court terme

- Verifier visuellement le panneau `Layers` sur plusieurs fichiers DXF reels
- Corriger progressivement les anciens textes encodes incorrectement

## V0.7.1 - Outil mur

- WallTool
- Placement manuel des murs
- Preview de mur reutilisant l'infrastructure V0.6.2

## V0.7.2 - Analyse du batiment

- Analyse automatique du batiment
- Reconnaissance future des murs
- Reconnaissance future des portes
- Reconnaissance future des fenetres

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

## 2026-07-01

- Finalisation de la V0.6
- Ajout de l'action `Fichier > Importer un DXF...`
- Suppression de l'import automatique de `rochette.dxf` au demarrage
- Nettoyage des imports dupliques de `ui/main_window.py`
- Suppression de `Canvas.add_outlet()` pour respecter `GraphicsFactory`
- Ajout des couleurs RGB et de l'etat verrouille aux calques DXF
- Affichage des couleurs et du verrouillage dans le panneau `Layers`
- Rendu DXF avec les couleurs de calques
- Ajout d'erreurs utilisateur pour DXF invalide ou vide
- Journalisation des blocs manquants et entites non supportees
- Remplacement des `print()` par du logging
- Ajout d'un `.gitignore`
- Suppression des caches Python suivis ou generes localement

## 2026-07-01 - V0.6.1

- Ajout de `ui/toolbar.py` pour centraliser les actions utilisateur rapides
- Extension de `ui/statusbar.py` pour afficher l'etat permanent de l'application
- Ajout de signaux `ToolManager.toolChanged` pour synchroniser UI et outils
- Ajout des notifications de suppression dans `ObjectManager`
- Ajout de `Canvas.fit_to_content()`
- Ajout du snap activable et de l'affichage/masquage de la grille
- Ajout des raccourcis `ESC`, `Ctrl+0`, `Suppr` et `Ctrl+A`
- Ajout du menu contextuel objet avec suppression
- Validation par compilation Python et test d'import DXF sur `rochette.dxf`

## 2026-07-01 - V0.6.2

- Ajout de `core/preview.py`
- Ajout de `graphics/preview_item.py`
- Ajout de `graphics/preview_factory.py`
- Ajout de `graphics/preview_manager.py`
- Ajout de `Tool.preview_definition()`
- Integration de `PreviewManager` dans `ToolManager`
- Ajout de `Canvas.show_preview_item(...)`
- Ajout de `Canvas.move_preview_item(...)`
- Ajout de `Canvas.remove_preview_item()`
- Ajout de la preview generique de placement pour `OutletTool`
- Mise a jour de la documentation d'architecture
- Ajout de `scripts/check_v062.py` pour valider automatiquement la V0.6.2

## 2026-07-01 - V0.7.0

- Ajout de `model/architecture.py`
- Ajout des classes `House`, `Floor`, `Room`, `Wall`, `Opening`, `Door`, `Window`
- Integration de `House` dans `core/project.py`
- Ajout du stockage du `DXFDocument` dans `Project`
- Connexion de l'import DXF au `Project`
- Transformation de `GraphicsFactory` en registre extensible
- Ajout de `tests/test_architecture_model.py`
- Mise a jour du README et de l'architecture
