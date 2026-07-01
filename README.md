# OpenHomePlanner

OpenHomePlanner est un logiciel libre de conception des reseaux techniques
d'une habitation a partir d'un plan existant, notamment au format DXF.

## Version de travail

V0.7.2 finalisee : import DXF, affichage du plan comme fond de travail,
gestion des calques, barre d'outils, barre d'etat, snap activable,
ghost preview generique et modele architectural pur Python pour representer
une habitation. La V0.7.1 ajoute le premier outil architectural manuel :
`WallTool`. La V0.7.2 ajoute l'infrastructure d'analyse DXF du batiment :
detecteur d'unites, detecteur de cotations, moteur de calibration, rapport
serialisable et detecteurs squelettes pour les futures analyses.

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

## Verifier la V0.7.1

Un script dedie valide le dessin manuel des murs, le `WallItem`, l'ajout au
`Project`, la preview et la suppression.

```bash
py scripts/check_v071.py
```

## Verifier la V0.7.2

Un script dedie valide l'infrastructure d'analyse : compilation, import DXF,
lecture des unites, detection des cotations, creation du rapport et
serialisation.

```bash
py scripts/check_v072.py rochette.dxf
```

## Importer un plan DXF

Depuis l'application :

1. Ouvrir le menu `Fichier`.
2. Cliquer sur `Importer un DXF...`.
3. Choisir un fichier `.dxf`.

Le plan est charge, centre et zoome automatiquement. Le panneau `Layers` est
mis a jour avec les calques du DXF, leur couleur, leur etat de visibilite et
leur verrouillage. Si une cote exploitable est detectee, le fond DXF est mis a
l'echelle du projet en centimetres avant affichage.

## Confort d'utilisation

- `ESC` revient a l'outil Selection.
- `Ctrl+0` ajuste la vue au contenu.
- `Suppr` supprime la selection.
- `Ctrl+A` selectionne tous les objets du projet.
- La toolbar permet d'activer Selection, Mur, Prise, Zoom +, Zoom -, Ajuster au
  plan, Snap ON/OFF et Afficher/Masquer la grille.

## Architecture

Le modele ne depend pas de Qt. L'importeur DXF produit un `DXFDocument` pur
Python, le `Canvas` reste une vue, et les objets graphiques sont crees dans la
couche `graphics`.

La preview V0.6.2 est temporaire : elle n'est pas stockee dans le `Project`,
ne cree aucun objet metier avant le clic et disparait automatiquement lors du
changement d'outil.

La V0.7.0 ajoute le modele architectural `House`, `Floor`, `Room`, `Wall`,
`Opening`, `Door` et `Window`. Ce modele est integre au `Project`, serialisable
via `to_dict()` / `from_dict()` et reste totalement independant de Qt.

La V0.7.1 reutilise ce modele `Wall` pour le dessin manuel. `WallTool` cree un
mur en deux clics, `GraphicsFactory` cree automatiquement le `WallItem`, et la
preview V0.6.2 affiche le futur mur avant creation. La version ne contient pas
de reconnaissance automatique, d'analyse DXF ou d'outils portes/fenetres.

La V0.7.2 ajoute le package `analysis/`. `BuildingAnalyzer` execute le pipeline
unites -> calibration -> detecteurs placeholder -> rapport. Le detecteur de
cotations lit aussi les cotes vectorisees en polylignes, comme la cote `410`
de `rochette.dxf`, et le `Canvas` applique le facteur calcule au `DXFItem`.
Cette version ne reconnait pas encore automatiquement les murs, ouvertures ou
pieces.
