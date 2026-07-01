# OpenHomePlanner - Architecture

Version : V0.6

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

graphics/
    base_item.py
    outlet_item.py
    dxf_item.py
    factory.py

importer/
    dxf_importer.py

library/

model/
    base_object.py
    electrical.py
    dxf.py

tools/
    tool.py
    tool_manager.py
    select_tool.py
    outlet_tool.py

ui/
    main_window.py
    canvas.py
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

# Le Project

Le Project est le cœur du logiciel.

Il contient tous les objets.

```
Project

│

├── Electrical

├── Plumbing

├── HVAC

├── DXFDocument

└── Settings
```

Toutes les modifications passent obligatoirement par le Project.

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

Il ne crée jamais d'objets métier.

---

# GraphicsFactory

Responsable de créer la représentation graphique.

```
Outlet

↓

OutletItem
```

```
Wall

↓

WallItem
```

Le Canvas ne connaît jamais les objets.

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
