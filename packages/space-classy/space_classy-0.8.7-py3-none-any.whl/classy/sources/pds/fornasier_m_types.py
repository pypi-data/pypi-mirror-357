import pandas as pd
import rocks

from classy import index
from classy import config
from classy.sources import pds

SHORTBIB, BIBCODE = "Fornasier+ 2010", "2010Icar..210..655F"

DATA_KWARGS = {"names": ["wave", "refl", "refl_err"], "delimiter": r"\s+"}


# ------
# Module functions
def _build_index(PATH_REPO):
    """Create index of spectra collection."""

    entries = []

    # Iterate over data directory
    for dir in (PATH_REPO / "data").iterdir():
        if not dir.is_dir():
            continue

        # Extract meta from XML file
        for xml_file in dir.glob("**/*xml"):
            id_, _, date_obs = pds.parse_xml(xml_file)
            file_ = xml_file.with_suffix(".tab")

            # Identify asteroid
            name, number = rocks.id(id_)

            # Create index entry
            entry = pd.DataFrame(
                data={
                    "name": name,
                    "number": number,
                    "date_obs": date_obs,
                    "shortbib": SHORTBIB,
                    "bibcode": BIBCODE,
                    "source": "Misc",
                    "host": "PDS",
                    "module": "fornasier_m_types",
                    "filename": file_.relative_to(config.PATH_DATA),
                },
                index=[0],
            )

            entries.append(entry)
    entries = pd.concat(entries)

    index.add(entries)
