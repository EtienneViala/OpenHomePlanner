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

        msp = drawing.modelspace()

        for entity in msp:

            self._read_entity(
                drawing,
                document,
                entity
            )

        return document

    # -------------------------------------------------------------

    def _read_entity(self, drawing, document, entity):

        entity_type = entity.dxftype()

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
                    layer=entity.dxf.layer,
                    color=entity.dxf.color,
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
                    layer=entity.dxf.layer,
                    color=entity.dxf.color,
                )

            )

            return

        #
        # LWPOLYLINE
        #

        if entity_type == "LWPOLYLINE":

            poly = DXFPolyline(

                layer=entity.dxf.layer,

                color=entity.dxf.color,

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