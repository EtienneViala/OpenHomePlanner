"""
DXF importer.
"""

from __future__ import annotations

import ezdxf

from model.dxf import (
    DXFCircle,
    DXFDocument,
    DXFLine,
    DXFPolyline,
)


class DXFImporter:

    def load(self, filename: str) -> DXFDocument:

        drawing = ezdxf.readfile(filename)

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
                entity
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

            document.ensure_layer(
                name=layer.dxf.name,
                color=layer.color,
                visible=not layer.is_off(),
            )

    # -------------------------------------------------------------

    def _read_entity(self, drawing, document, entity):

        entity_type = entity.dxftype()

        layer_name = getattr(
            entity.dxf,
            "layer",
            "0",
        )

        color = getattr(
            entity.dxf,
            "color",
            7,
        )

        document.ensure_layer(
            layer_name,
            color=color,
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

            block = drawing.blocks.get(
                entity.dxf.name
            )

            if block is None:
                return

            print(
                f"Reading block: {entity.dxf.name}"
            )

            for sub_entity in block:

                self._read_entity(
                    drawing,
                    document,
                    sub_entity
                )
