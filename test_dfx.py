import logging
import sys

from importer.dxf_importer import DXFImporter


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if len(sys.argv) != 2:
    raise SystemExit("Usage: python test_dfx.py <file.dxf>")

document = DXFImporter().load(sys.argv[1])

logger.info("Nombre d'entites : %s", len(document.entities))
logger.info("Premiere entite : %s", type(document.entities[0]).__name__)
