# OpenHomePlanner

OpenHomePlanner est un logiciel libre de conception des reseaux techniques
d'une habitation a partir d'un plan existant, notamment au format DXF.

## Version de travail

V0.6.2 finalisee : import DXF, affichage du plan comme fond de travail,
gestion des calques, barre d'outils, barre d'etat, snap activable,
ajustement automatique de la vue, suppression propre des objets et systeme
generique de ghost preview pour les outils de placement.

## Lancer l'application

```bash
py main.py
```

## Verifier la V0.6.2

Un script de validation rapide permet de verifier la compilation, l'import DXF,
les calques, le demarrage Qt, l'outil Prise, la suppression et le ghost preview.

```bash
py scripts/check_v062.py rochette.dxf
```

Le script affiche un resume `OK` / `FAIL` pour chaque etape et retourne le code
`0` si tous les checks passent.

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

La preview V0.6.2 est temporaire : elle n'est pas stockee dans le `Project`,
ne cree aucun objet metier avant le clic et disparait automatiquement lors du
changement d'outil.

La V0.6.2 ne contient pas de reconnaissance de murs, d'interrupteurs ou de
circuits electriques. Ces sujets restent reserves aux versions suivantes.
