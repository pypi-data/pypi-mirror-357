import json
import os
import requests

# Load configuration from JSON file
CONFIG_PATH = os.getenv("CONFIG_PATH", "config.json")
with open(CONFIG_PATH, 'r') as cfg_file:
    config = json.load(cfg_file)

# Base URL and credentials from config
BASE_URL = config.get("base_url", "https://eutils.ncbi.nlm.nih.gov/entrez/eutils")
EMAIL = config["email"]
API_KEY = config.get("api_key")


def _esearch(db: str, term: str, retmax: int = 20) -> dict:
    """Perform an ESearch query and return JSON results."""
    params = {
        'db': db,
        'term': term,
        'retmax': retmax,
        'retmode': 'json',
        'email': EMAIL,
    }
    if API_KEY:
        params['api_key'] = API_KEY
    resp = requests.get(f"{BASE_URL}/esearch.fcgi", params=params)
    resp.raise_for_status()
    return resp.json()


def _esummary(db: str, ids: list) -> dict:
    """Fetch summaries for a list of IDs."""
    params = {
        'db': db,
        'id': ','.join(ids),
        'retmode': 'json',
        'email': EMAIL,
    }
    if API_KEY:
        params['api_key'] = API_KEY
    resp = requests.get(f"{BASE_URL}/esummary.fcgi", params=params)
    resp.raise_for_status()
    return resp.json()


def search_geo_profiles(term: str, retmax: int = 20) -> dict:
    """Search GEO Profiles."""
    data = _esearch('geoprofiles', term, retmax)
    ids = data.get('esearchresult', {}).get('idlist', [])
    return _esummary('geoprofiles', ids)


def search_geo_datasets(term: str, retmax: int = 20) -> dict:
    """Search GEO DataSets."""
    data = _esearch('gds', term, retmax)
    ids = data.get('esearchresult', {}).get('idlist', [])
    return _esummary('gds', ids)


if __name__ == '__main__':
    # Example config.json content:
    # {
    #     "base_url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils",
    #     "email": "your_email@example.com",
    #     "api_key": "YOUR_API_KEY"
    # }
    term = 'cancer'
    profiles = search_geo_profiles(term)
    print('Profiles:', profiles)
    datasets = search_geo_datasets(term)
    print('DataSets:', datasets)
