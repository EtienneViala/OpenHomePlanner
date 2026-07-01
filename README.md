# OpenHomePlanner

OpenHomePlanner est un logiciel libre de conception des reseaux techniques
d'une habitation a partir d'un plan existant, notamment au format DXF.

## Version de travail

V0.6 finalisee : import DXF, affichage du plan comme fond de travail,
gestion des calques, masquage immediat des calques et ajustement automatique
de la vue apres import.

## Lancer l'application

```bash
py main.py
```

## Importer un plan DXF

Depuis l'application :

1. Ouvrir le menu `Fichier`.
2. Cliquer sur `Importer un DXF...`.
3. Choisir un fichier `.dxf`.

Le plan est charge, centre et zoome automatiquement. Le panneau `Layers` est
mis a jour avec les calques du DXF, leur couleur, leur etat de visibilite et
leur verrouillage.

## Architecture

Le modele ne depend pas de Qt. L'importeur DXF produit un `DXFDocument` pur
Python, le `Canvas` reste une vue, et les objets graphiques sont crees dans la
couche `graphics`.

La V0.6 ne contient pas de reconnaissance de murs, d'interrupteurs ou de
circuits electriques. Ces sujets restent reserves aux versions suivantes.
