# OpenHomePlanner

## Présentation

OpenHomePlanner est un logiciel libre développé en Python avec Qt (PySide6).

Son objectif est de permettre la conception complète des réseaux techniques d'une maison existante à partir d'un plan DXF.

Le logiciel est destiné principalement aux particuliers, aux électriciens et aux rénovateurs souhaitant préparer une rénovation complète d'une habitation.

Contrairement à Sweet Home 3D ou LibreCAD, OpenHomePlanner ne cherche pas uniquement à dessiner un plan.

Son objectif est d'être un véritable outil d'aide à la conception :

- réseau électrique
- plomberie
- chauffage
- VMC
- réseau informatique
- sécurité
- domotique

à partir d'un plan existant.

---

# Philosophie

Le logiciel repose sur plusieurs principes :

- architecture modulaire
- code orienté objet
- outils indépendants
- séparation stricte entre le modèle métier et l'affichage
- performances élevées même sur de gros plans DXF

Le Canvas ne contient jamais de logique métier.

Les outils ne dessinent jamais directement.

Ils créent uniquement des objets du modèle.

Le GraphicsFactory transforme ensuite ces objets en représentation graphique.

---

# Architecture

OpenHomePlanner/

```
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
    canvas.py
    library_panel.py
    property_panel.py
    main_window.py
```

---

# Technologies

Python 3.13

PySide6

ezdxf

Qt Graphics View Framework

---

# Fonctionnalités réalisées

## V0.1

Création de la fenêtre principale.

Canvas.

Grille.

Navigation.

---

## V0.2

Création des premiers objets métier.

Outlet.

BaseObject.

GraphicsItem.

GraphicsFactory.

---

## V0.3

Project.

ObjectManager.

SelectionManager.

PropertyPanel.

Sélection des objets.

Déplacement des objets.

Affichage des propriétés.

Architecture MVC.

---

## V0.4

Système d'outils.

Tool.

ToolManager.

SelectTool.

OutletTool.

Placement des prises.

Bibliothèque.

---

## V0.5

Lecture des fichiers DXF.

Support des INSERT.

Support des blocs.

Support des LWPOLYLINE.

Support des LINE.

Support des CIRCLE.

Affichage du plan complet dans le Canvas.

Les prises sont affichées au-dessus du plan.

Le plan est utilisé comme fond de travail.

---

# Architecture actuelle

```
DXF

↓

DXFImporter

↓

DXFDocument

↓

DXFItem

↓

Canvas

↓

Utilisateur
```

Pour les objets électriques :

```
Utilisateur

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

↓

Canvas
```

---

# Roadmap

## V0.6

Gestion des calques DXF

Masquer les cotations

Masquer les textes

Masquer les annotations

Importer plusieurs plans

---

## V0.7

Reconnaissance automatique des murs

Reconnaissance des portes

Reconnaissance des fenêtres

Accrochage intelligent des objets

Rotation automatique

---

## V0.8

Interrupteurs

Va-et-vient

Prises RJ45

Prises TV

Tableau électrique

Circuits

---

## V0.9

Dessin automatique des câbles

Calcul des longueurs

Calcul des gaines

Calcul des saignées

---

## V1.0

Projet complet

Export PDF

Export SVG

Export DXF

Impression

Liste du matériel

Schéma unifilaire

Schéma architectural

---

# Vision à long terme

OpenHomePlanner doit devenir un logiciel capable de concevoir entièrement les réseaux techniques d'une habitation.

Le logiciel devra être capable de :

- importer un plan DXF
- reconnaître automatiquement les murs
- placer intelligemment les équipements
- vérifier les normes électriques (NF C 15-100)
- générer automatiquement les circuits
- générer le tableau électrique
- calculer les longueurs de câble
- générer les nomenclatures
- exporter un dossier complet de chantier

---

# Principes de développement

Un fichier = une responsabilité.

Le modèle métier ne dépend jamais de Qt.

Le Canvas ne contient jamais de logique métier.

Les outils sont indépendants.

Le GraphicsFactory est le seul responsable de la création des objets graphiques.

Le code doit rester lisible et documenté.

Chaque version doit rester compilable.

Le projet doit pouvoir évoluer pendant plusieurs années sans remise en cause de son architecture.

---

# Idées futures

Support DWG.

Support IFC.

Support PDF vectoriel.

Support SVG.

Vue 3D.

Reconnaissance IA des plans.

Calcul d'éclairage.

Calcul thermique.

Calcul hydraulique.

Simulation énergétique.

Plugin système.

Scripts Python utilisateur.

Synchronisation cloud.

Multi-utilisateur.
