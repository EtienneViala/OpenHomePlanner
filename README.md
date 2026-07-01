# OpenHomePlanner

OpenHomePlanner est un logiciel libre de conception des reseaux techniques
d'une habitation a partir d'un plan existant, notamment au format DXF.

## Version de travail

V0.6.1 finalisee : import DXF, affichage du plan comme fond de travail,
gestion des calques, barre d'outils, barre d'etat, snap activable,
ajustement automatique de la vue et suppression propre des objets.

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

## Confort d'utilisation

- `ESC` revient a l'outil Selection.
- `Ctrl+0` ajuste la vue au contenu.
- `Suppr` supprime la selection.
- `Ctrl+A` selectionne tous les objets du projet.
- La toolbar permet d'activer Selection, Prise, Zoom +, Zoom -, Ajuster au plan,
  Snap ON/OFF et Afficher/Masquer la grille.

## Architecture

Le modele ne depend pas de Qt. L'importeur DXF produit un `DXFDocument` pur
Python, le `Canvas` reste une vue, et les objets graphiques sont crees dans la
couche `graphics`.

La V0.6 ne contient pas de reconnaissance de murs, d'interrupteurs ou de
circuits electriques. Ces sujets restent reserves aux versions suivantes.
