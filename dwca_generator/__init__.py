__version__ = "0.0.0"

from pathlib import Path

# from dwca_generator.dwca_utils import singleton
from dwca_generator.dwca_utils import ZipArchive
from dwca_generator.dwca_utils import create_extra_key
from dwca_generator.dwca_utils import is_daylight_savings_time

from dwca_generator.dwca_filters import DwcaFilters
from dwca_generator.dwca_translate import DwcaTranslate
from dwca_generator.dwca_taxa_worms import TaxaWorms

from dwca_generator.dwca_data_shark import DwcaDataSharkStandard
from dwca_generator.dwca_format_standard import DwcaFormatStandard
from dwca_generator.dwca_meta_xml import DarwinCoreMetaXml

from dwca_generator.metadata_content_auto import MetadataContentAuto
from dwca_generator.metadata_dwca_eml import MetadataDwcaEml
from dwca_generator.metadata_smhi_yame import MetadataSmhiYame

from dwca_generator.dwca_generator_config import DwcaGeneratorConfig

PROJECT_ROOT = Path(__file__).parent.parent