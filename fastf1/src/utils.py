import pycountry
import re


def country_to_code(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_2.lower()
    except LookupError:
        return None


def slugify_location(location):
    slug = location.lower().replace(" ", "-")
    slug = re.sub(r"[^\w\-]", "", slug)
    return f"{slug}-gp"


def nationality_to_country_code(nationality: str) -> str:
    """Convert nationality or country name to ISO 3166-1 alpha-2 code."""
    try:
        # Try to match nationality as country
        country = pycountry.countries.get(name=nationality)
        if country:
            return country.alpha_2.lower()

        # Try to match by common name
        country = pycountry.countries.get(common_name=nationality)
        if country:
            return country.alpha_2.lower()

        mapping = {
            "American": "us",
            "Argentine": "ar",
            "Australian": "au",
            "Austrian": "at",
            "Belgian": "be",
            "Brazilian": "br",
            "British": "gb",
            "Canadian": "ca",
            "Chilean": "cl",
            "Chinese": "cn",
            "Colombian": "co",
            "Czech": "cz",
            "Danish": "dk",
            "Dutch": "nl",
            "Finnish": "fi",
            "French": "fr",
            "German": "de",
            "Hungarian": "hu",
            "Indian": "in",
            "Indonesian": "id",
            "Irish": "ie",
            "Italian": "it",
            "Japanese": "jp",
            "Luxembourgish": "lu",
            "Malaysian": "my",
            "Mexican": "mx",
            "Monegasque": "mc",
            "New Zealander": "nz",
            "Polish": "pl",
            "Portuguese": "pt",
            "Russian": "ru",
            "Saudi": "sa",
            "Singaporean": "sg",
            "South African": "za",
            "South Korean": "kr",
            "Spanish": "es",
            "Swedish": "se",
            "Swiss": "ch",
            "Thai": "th",
            "Turkish": "tr",
            "Venezuelan": "ve",
        }
        return mapping.get(nationality, "")
    except:
        return ""
