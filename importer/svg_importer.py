from PySide6.QtSvgWidgets import QGraphicsSvgItem


class SvgImporter:

    @staticmethod
    def import_svg(scene, filename):

        item = QGraphicsSvgItem(filename)

        scene.addItem(item)

        return item