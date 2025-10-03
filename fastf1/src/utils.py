import pycountry
import re


def iso2_country(country_input):
    """
    Maps a country name or list of country names to lowercase ISO alpha-2 codes using pycountry.
    Falls back to first 2 lowercase letters if country not found.

    Args:
        country_input (str or list[str]): A single country name or list of country names.

    Returns:
        str or list[str]: A single lowercase ISO alpha-2 code or list of codes.
    """

    def get_alpha2_code(name: str) -> str:
        try:
            return pycountry.countries.lookup(name).alpha_2.lower()
        except LookupError:
            return name[:2].lower() if name else ""

    if isinstance(country_input, str):
        return get_alpha2_code(country_input)
    elif isinstance(country_input, list):
        return [get_alpha2_code(name) for name in country_input]
    return ""


def iso3_country(country_input):
    """
    Maps a country name or list of country names to lowercase ISO alpha-3 codes using pycountry.
    Falls back to first 3 lowercase letters if country not found.

    Args:
        country_input (str or list[str]): A single country name or list of country names.

    Returns:
        str or list[str]: A single lowercase ISO alpha-3 code or list of codes.
    """

    def get_alpha3_code(name: str) -> str:
        try:
            return pycountry.countries.lookup(name).alpha_3.upper()
        except LookupError:
            return name[:3].upper() if name else ""

    if isinstance(country_input, str):
        return get_alpha3_code(country_input)
    elif isinstance(country_input, list):
        return [get_alpha3_code(name) for name in country_input]
    return ""


def slugify_location(location):
    """
    Creates an identifier for a race event.

    Args:
        location (str): Hosting city/country of race event.

    Returns:
        str: A string containing event host and shortened postfix "-gp".
    """

    slug = location.lower().replace(" ", "-")
    slug = re.sub(r"[^\w\-]", "", slug)
    return f"{slug}-gp"


def nationality_to_country_code(nationality: str) -> str:
    """
    Maps a nationality to lowercase ISO alpha-2 codes using pycountry.

    Args:
        nationality (str): Nationality of a driver.

    Returns:
        str: A single lowercase ISO alpha-2 code.
    """

    try:
        country = pycountry.countries.get(name=nationality)
        if country:
            return country.alpha_2.lower()
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