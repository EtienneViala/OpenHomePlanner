"""
DXF importer.
"""

from __future__ import annotations

import logging

import ezdxf
from ezdxf import colors
from ezdxf.lldxf.const import DXFError

from model.dxf import (
    DXFCircle,
    DXFDocument,
    DXFLine,
    DXFPolyline,
)


logger = logging.getLogger(__name__)


class DXFImportError(Exception):
    """
    Raised when a DXF file cannot be imported as a usable document.
    """


class DXFImporter:

    def load(self, filename: str) -> DXFDocument:

        try:
            drawing = ezdxf.readfile(filename)
        except (OSError, DXFError) as exc:
            raise DXFImportError(
                f"Impossible de lire le fichier DXF : {filename}"
            ) from exc

        document = DXFDocument(filename=filename)

        self._read_layers(
            drawing,
            document,
        )

        msp = drawing.modelspace()

        for entity in msp:

            self._read_entity(
                drawing,
                document,
                entity,
            )

        if not document.entities:
            raise DXFImportError(
                "Le fichier DXF ne contient aucune entité exploitable."
            )

        return document

    # -------------------------------------------------------------

    def _read_layers(self, drawing, document):
        """
        Read the DXF layer table into the document model.

        Layer visibility is stored in the model instead of the graphics item so
        the UI can change it without re-importing or coupling itself to Qt
        rendering details.
        """

        for layer in drawing.layers:

            layer_color = self._normalize_color(layer.color)

            document.ensure_layer(
                name=layer.dxf.name,
                color=layer_color,
                color_rgb=self._aci_to_rgb(layer_color),
                visible=not layer.is_off(),
                locked=layer.is_locked(),
            )

    # -------------------------------------------------------------

    def _read_entity(self, drawing, document, entity):

        entity_type = entity.dxftype()

        layer_name = getattr(
            entity.dxf,
            "layer",
            "0",
        )

        raw_color = getattr(
            entity.dxf,
            "color",
            7,
        )

        layer = document.ensure_layer(layer_name)
        color = self._resolve_entity_color(raw_color, layer.color)
        color_rgb = self._aci_to_rgb(color)

        document.ensure_layer(
            layer_name,
            color=color,
            color_rgb=color_rgb,
        )

        #
        # LINE
        #

        if entity_type == "LINE":

            start = entity.dxf.start
            end = entity.dxf.end

            document.entities.append(

                DXFLine(
                    x1=start.x,
                    y1=start.y,
                    x2=end.x,
                    y2=end.y,
                    layer=layer_name,
                    color=color,
                    color_rgb=color_rgb,
                )

            )

            return

        #
        # CIRCLE
        #

        if entity_type == "CIRCLE":

            center = entity.dxf.center

            document.entities.append(

                DXFCircle(
                    x=center.x,
                    y=center.y,
                    radius=entity.dxf.radius,
                    layer=layer_name,
                    color=color,
                    color_rgb=color_rgb,
                )

            )

            return

        #
        # LWPOLYLINE
        #

        if entity_type == "LWPOLYLINE":

            poly = DXFPolyline(

                layer=layer_name,

                color=color,
                color_rgb=color_rgb,

                closed=entity.closed,

            )

            for p in entity:

                poly.points.append(
                    (p[0], p[1])
                )

            document.entities.append(poly)

            return

        #
        # INSERT (Block)
        #

        if entity_type == "INSERT":

            block_name = entity.dxf.name

            try:
                block = drawing.blocks.get(block_name)
            except DXFError:
                block = None

            if block is None:
                message = f"Bloc DXF manquant ignore : {block_name}"
                document.warnings.append(message)
                logger.warning(message)
                return

            for sub_entity in block:

                self._read_entity(
                    drawing,
                    document,
                    sub_entity,
                )

            return

        message = f"Entité DXF non supportée ignorée : {entity_type}"
        document.warnings.append(message)
        logger.info(message)

    # -------------------------------------------------------------

    def _normalize_color(self, color: int | None) -> int:
        if color is None or color <= 0:
            return 7

        if color == colors.BYLAYER:
            return 7

        if color == colors.BYBLOCK:
            return 7

        return color

    # -------------------------------------------------------------

    def _resolve_entity_color(
        self,
        entity_color: int | None,
        layer_color: int,
    ) -> int:
        if entity_color in (None, colors.BYLAYER, colors.BYBLOCK, 0):
            return self._normalize_color(layer_color)

        return self._normalize_color(entity_color)

    # -------------------------------------------------------------

    def _aci_to_rgb(
        self,
        color: int,
    ) -> tuple[int, int, int]:
        try:
            rgb = colors.aci2rgb(self._normalize_color(color))
        except (IndexError, ValueError):
            rgb = colors.aci2rgb(7)

        return rgb.r, rgb.g, rgb.b
