# OpenHomePlanner - Architecture

Version : V0.7.2

---

# Objectif

L'objectif de cette architecture est de construire un logiciel évolutif, modulaire et performant permettant de concevoir les réseaux techniques d'une habitation.

Le logiciel est construit autour de plusieurs principes :

- séparation entre les données et l'affichage
- composants indépendants
- architecture orientée objets
- extensibilité maximale
- performances élevées

Le logiciel ne doit jamais dépendre d'une technologie particulière (DXF, Qt, SVG, etc.).

---

# Architecture générale

```
                Utilisateur

                      │

                      ▼

              MainWindow (UI)

                      │

          ┌───────────┴───────────┐

          ▼                       ▼

      LibraryPanel         PropertyPanel

          │

          ▼

      ToolManager

          │

          ▼

     Current Tool

          │

          ▼

        Project

          │

   ┌──────┴────────┐

   ▼               ▼

ObjectManager  SelectionManager

          │

          ▼

 GraphicsFactory

          │

          ▼

 Graphics Items

          │

          ▼

      QGraphicsScene

          │

          ▼

        Canvas
```

---

# Architecture du projet

```
OpenHomePlanner/

core/
    project.py
    object_manager.py
    selection_manager.py

analysis/
    analyzer.py
    calibration.py
    detectors/
        unit_detector.py
        dimension_detector.py
        wall_detector.py
        opening_detector.py
        room_detector.py

graphics/
    base_item.py
    outlet_item.py
    wall_item.py
    dxf_item.py
    factory.py
    preview_item.py
    preview_factory.py
    preview_manager.py

importer/
    dxf_importer.py

library/

model/
    architecture.py
    base_object.py
    electrical.py
    dxf.py

tools/
    tool.py
    tool_manager.py
    select_tool.py
    outlet_tool.py
    wall_tool.py

ui/
    main_window.py
    canvas.py
    toolbar.py
    statusbar.py
    library_panel.py
    property_panel.py

resources/

tests/
```

---

# Le modèle métier

Le dossier model contient uniquement les données.

Il ne contient aucun code Qt.

Exemple :

```
Outlet

nom

position

rotation

circuit

hauteur
```

Les objets métier ne savent jamais comment ils sont dessinés.

Ils décrivent uniquement la réalité.

---

# Modele architectural

La V0.7.0 ajoute un modele architectural pur Python. Il prepare les futures
versions de dessin et d'analyse sans ajouter d'outil graphique.

```
House
|-- Floor
|   |-- Room
|   |-- Wall
|       |-- Opening
|           |-- Door
|           |-- Window
```

Responsabilites :

- `House` represente l'habitation complete, son nom, son adresse, ses etages et ses parametres
- `Floor` represente un niveau avec ses pieces et ses murs
- `Room` represente une piece, sa surface future, son contour et ses murs associes
- `Wall` represente un segment de mur, ses points, son epaisseur, sa hauteur, son materiau et son orientation
- `Opening` represente une ouverture associee a un mur
- `Door` et `Window` specialisent `Opening` sans comportement graphique

Toutes ces classes exposent une serialisation simple avec `to_dict()` et
`from_dict()` lorsque la reconstruction est necessaire.

---

# Le Project

Le Project est le cœur du logiciel.

Il contient tous les objets.

```
Project

|-- DXFDocument
|-- AnalysisReport
|-- House
|-- ObjectManager
|-- SelectionManager
```

Toutes les modifications passent obligatoirement par le Project.

Le dernier rapport d'analyse du batiment peut etre stocke dans le `Project`
via `set_analysis_report(...)`. Ce stockage ne modifie pas les flux existants
d'import, de dessin, de selection ou de suppression.

---

# Analyse du batiment

La V0.7.2 ajoute un package `analysis/` independant de Qt. Il prepare la
transformation progressive d'un DXF en modele architectural, sans reconnaitre
encore automatiquement les murs, ouvertures ou pieces.

Pipeline :

```
DXF
|
v
UnitDetector
|
v
DimensionDetector + CalibrationEngine
|
v
WallDetector placeholder
|
v
OpeningDetector placeholder
|
v
RoomDetector placeholder
|
v
AnalysisReport
```

Responsabilites :

- `BuildingAnalyzer` orchestre les detecteurs et produit un rapport
- `UnitDetector` lit `$INSUNITS` et normalise `mm`, `cm`, `m` et `in`
- `DimensionDetector` recherche les entites `TEXT`, `MTEXT` et `DIMENSION`, et
  dispose d'un fallback pour les cotes vectorisees en `LWPOLYLINE`
- `CalibrationEngine` calcule un facteur d'echelle a partir des cotations,
  en centimetres par unite DXF par defaut
- `AnalysisReport` expose une serialisation `to_dict()` / `from_dict()`
- `WallDetector`, `OpeningDetector` et `RoomDetector` sont des squelettes
  documentes, remplacables independamment dans les versions futures

---

# ObjectManager

Responsable de :

- ajouter un objet
- supprimer un objet
- parcourir les objets
- notifier les vues

Il ne dessine jamais.

---

# SelectionManager

Responsable de :

- objet sélectionné
- sélection multiple
- CTRL+A
- rectangle de sélection

Toutes les vues utilisent cette sélection.

---

# Canvas

Le Canvas est uniquement une vue.

Il :

- affiche
- zoom
- déplace
- transmet les événements
- fournit le snap courant aux outils
- ajuste la vue au contenu

Il ne crée jamais d'objets métier.

Il ne supprime jamais directement un objet métier : il transmet l'action au
`ToolManager`, puis le `Project` notifie la vue via `ObjectManager`.

---

# GraphicsFactory

Responsable de créer la représentation graphique.

```
Outlet

↓

OutletItem
```

Le Canvas ne connaît jamais les objets.

Depuis la V0.7.1, `WallItem` est enregistre dans le registre pour le modele
`Wall`. Le Canvas ne contient aucun branchement specifique aux murs.

---

# Ghost Preview

La V0.6.2 ajoute une infrastructure generique de previsualisation pour les
outils de placement.

```
Tool

|
v

PreviewDefinition

|
v

ToolManager

|
v

PreviewManager

|
v

PreviewFactory

|
v

PreviewItem

|
v

Canvas
```

Regles :

- le `PreviewDefinition` est une donnee pure sans dependance Qt
- les outils declarent seulement le type d'apercu souhaite
- le `ToolManager` gere la creation, la mise a jour et la destruction
- le `PreviewFactory` cree les items temporaires de preview
- le `Canvas` affiche, deplace et supprime uniquement l'item temporaire recu
- aucun objet metier n'est cree avant le clic utilisateur
- aucun item de preview n'est conserve dans le `Project`
- la preview est non selectionnable et semi-transparente
- la V0.7.1 etend la meme infrastructure pour la preview orientee des murs,
  avec longueur, angle et epaisseur

---

# GraphicsItem

Les GraphicsItems représentent les objets dans Qt.

Ils :

- dessinent
- déplacent
- sélectionnent

Ils ne contiennent jamais de logique métier.

---

# Les outils

Tous les outils héritent de Tool.

```
Tool

│

├── SelectTool

├── OutletTool

├── WallTool

├── CableTool
```

Les outils créent uniquement des objets métier.

Ils ne dessinent jamais directement.

---

## WallTool

`WallTool` est le premier outil architectural manuel. Il suit le flux standard :

```
Premier clic -> point de depart
Souris -> preview de mur
Deuxieme clic -> creation du Wall
Project -> ObjectManager -> GraphicsFactory -> WallItem
```

Le mur cree reutilise exclusivement `model.architecture.Wall`. Son epaisseur
par defaut est centralisee par `DEFAULT_WALL_THICKNESS`. Le `Project` reference
le mur dans l'`ObjectManager` pour l'affichage et dans l'etage par defaut du
`House` pour conserver le modele architectural.

`WallItem` affiche un rectangle oriente base sur les deux extremites du mur,
avec un contour de selection et un pen cosmetique pour rester lisible quel que
soit le zoom. Le deplacement met a jour les deux points du `Wall`.

---

# Bibliothèque

La bibliothèque permet d'activer les outils.

```
Electrical

↓

Outlet

↓

OutletTool
```

Aucune logique métier.

---

# Import DXF

```
DXF

↓

ezdxf

↓

DXFImporter

↓

DXFDocument

↓

DXFItem

↓

Canvas
```

L'importeur ne dépend pas de Qt.

---

# Les couches

Le Canvas contient plusieurs couches.

```
+--------------------------------+

Project Layer

Prises

Interrupteurs

Luminaires

---------------------------------

DXF Layer

Plan de la maison

---------------------------------

Background

Grille

+--------------------------------+
```

Le plan DXF reste verrouillé.

Le modele DXF stocke les calques dans `DXFDocument` sous forme de donnees
pures :

- nom
- visibilite
- verrouillage
- couleur ACI
- couleur RGB resolue

Le panneau `Layers` lit ce modele et emet uniquement des changements de
visibilite. Le `Canvas` applique ce changement au document courant et demande
au `DXFItem` de se repeindre, sans recharger le fichier DXF.

Quand une analyse fournit un `scale_factor`, le `Canvas` le transmet au
`DXFItem`. Le fond DXF est alors dessine dans l'unite projet, en centimetres,
sans modifier les donnees importees.

---

# Gestion des événements

```
Utilisateur

↓

Canvas

↓

ToolManager

↓

Tool

↓

Project

↓

ObjectManager

↓

GraphicsFactory

↓

GraphicsItem
```

---

# Suppression des objets

```
Utilisateur

↓

Canvas

↓

ToolManager / Action

↓

Project.remove_object(...)

↓

ObjectManager

↓

Canvas
```

La suppression retire l'objet du projet, notifie la vue, vide la selection et
met a jour le panneau de proprietes. Ce flux reste compatible avec un futur
systeme Undo/Redo.

---

# Gestion des propriétés

```
Sélection

↓

SelectionManager

↓

PropertyPanel
```

---

# Dépendances

```
Qt

↑

Graphics

↑

Core

↑

Model
```

Le Model ne dépend jamais des couches supérieures.

---

# Règles de développement

## 1

Un fichier = une responsabilité.

## 2

Le modèle ne dépend jamais de Qt.

## 3

Le Canvas ne contient jamais de logique métier.

## 4

Les outils créent uniquement des objets métier.

## 5

Le GraphicsFactory est le seul autorisé à créer les GraphicsItems.

## 6

Le Project est le point d'entrée unique.

## 7

Les vues écoutent les événements.

Elles ne modifient jamais directement les données.

## 8

Toutes les nouvelles fonctionnalités doivent pouvoir être ajoutées sans modifier le Canvas.

---

# Évolutions prévues

## Réseaux

- électrique
- plomberie
- chauffage
- VMC
- réseau informatique

---

## Reconnaissance

- murs
- portes
- fenêtres

---

## Calculs

- longueurs
- surfaces
- volumes
- puissance
- éclairage

---

## Vérifications

- NF C 15-100
- plomberie
- ventilation

---

## Export

- PDF
- SVG
- DXF
- IFC

---

# Vision

OpenHomePlanner doit devenir un logiciel libre de conception des réseaux techniques d'une habitation.

Le logiciel doit rester simple pour un particulier tout en offrant des fonctionnalités avancées proches des logiciels professionnels.

L'architecture doit permettre au projet d'évoluer pendant de nombreuses années sans remise en cause de ses fondations.
