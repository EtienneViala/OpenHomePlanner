# OpenHomePlanner - Suivi du developpement

Derniere mise a jour : 2026-07-01

---

# Etat global

Version de travail : V0.7.2 finalisee

OpenHomePlanner est actuellement capable d'importer un plan DXF, de l'afficher comme fond de plan, de placer des objets electriques simples, de dessiner manuellement des murs, de gerer leur selection, de proposer une experience utilisateur stabilisee, d'afficher une preview temporaire pour les outils de placement, de stocker un modele architectural pur Python dans le Project et de produire un premier rapport d'analyse DXF du batiment.

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

## V0.7.1 - Outil mur manuel

- Ajout de `WallTool` pour creer un mur en deux clics
- Reutilisation du modele `model.architecture.Wall`
- Ajout de `DEFAULT_WALL_THICKNESS` pour centraliser l'epaisseur par defaut
- Ajout des proprietes calculees `length` et `angle` au modele `Wall`
- Ajout de `WallItem` pour afficher un mur sous forme de rectangle oriente
- Enregistrement de `WallItem` dans `GraphicsFactory`
- Extension de la preview V0.6.2 avec la forme dynamique `wall`
- Affichage de la longueur, de l'angle et de l'epaisseur pendant la preview
- Ajout du bouton `Mur` dans la toolbar et de l'activation depuis la bibliotheque
- Affichage lecture seule des proprietes d'un mur selectionne
- Suppression des murs via le flux existant `Project.remove_object(...)`
- Ajout de `tests/test_wall_tool.py`
- Ajout de `scripts/check_v071.py`

## V0.7.2 - Infrastructure d'analyse du batiment

- Ajout du package `analysis/`
- Ajout de `BuildingAnalyzer` pour orchestrer le pipeline d'analyse
- Ajout de `AnalysisReport`, rapport serialisable
- Ajout de `UnitDetector` pour lire et normaliser les unites DXF
- Ajout de `DimensionDetector` pour rechercher `TEXT`, `MTEXT` et `DIMENSION`
- Ajout d'un fallback pour les cotations vectorisees en `LWPOLYLINE`
- Ajout de `CalibrationEngine` pour calculer un facteur d'echelle
- Ajout de squelettes documentes `WallDetector`, `OpeningDetector` et `RoomDetector`
- Ajout d'un emplacement `Project.analysis_report`
- Ajout de `tests/test_analysis.py`
- Ajout de `scripts/check_v072.py`
- Aucune reconnaissance automatique de murs, ouvertures ou pieces

---

# En cours

## Stabilisation V0.7.2 terminee

- Import reel teste avec `rochette.dxf` : 191 entites importees
- Calques detectes sur le fichier de test : `0`, `Defpoints`, `Layer 1`
- Panneau `Layers` synchronise automatiquement apres import
- Masquage/affichage des calques sans rechargement du DXF
- Toolbar, barre d'etat, snap, grille et raccourcis clavier connectes
- Suppression d'objets validee via le flux Project/ObjectManager/Canvas
- Ghost preview validee par compilation Python
- Check automatique disponible : `py scripts/check_v062.py rochette.dxf`
- Modele architectural valide par tests unitaires sans Qt
- WallTool valide par tests Qt offscreen
- Check automatique V0.7.1 disponible : `py scripts/check_v071.py`
- Infrastructure d'analyse validee par tests unitaires sans Qt
- Check automatique V0.7.2 disponible : `py scripts/check_v072.py rochette.dxf`
- Detection de la cote vectorisee `410` dans `rochette.dxf`
- Application du facteur d'echelle d'analyse au rendu `DXFItem`

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

## 2026-07-01 - V0.7.1

- Ajout de `graphics/wall_item.py`
- Ajout de `tools/wall_tool.py`
- Extension de `core/preview.py`, `graphics/preview_item.py` et
  `graphics/preview_manager.py` pour la preview de mur
- Enregistrement de `WallItem` dans `graphics/factory.py`
- Integration de l'outil Mur dans `ui/main_window.py` et `ui/toolbar.py`
- Extension de `ui/property_panel.py` pour les proprietes lecture seule du mur
- Extension de `core/project.py` pour lier les murs au `House`
- Ajout de tests unitaires et du script `scripts/check_v071.py`

## 2026-07-01 - V0.7.2

- Ajout de `analysis/analyzer.py`
- Ajout de `analysis/calibration.py`
- Ajout de `analysis/detectors/unit_detector.py`
- Ajout de `analysis/detectors/dimension_detector.py`
- Ajout des squelettes `wall_detector.py`, `opening_detector.py` et `room_detector.py`
- Ajout du stockage du dernier rapport d'analyse dans `core/project.py`
- Application du facteur `AnalysisReport.scale_factor` lors de l'affichage DXF
- Ajout de `tests/test_analysis.py`
- Ajout de `scripts/check_v072.py`
- Mise a jour du README et de l'architecture
