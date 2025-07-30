from orcid import retrieveORCIDinfo

def information_linking_orcid(first_name, last_name, orcid_api_key):
    if not orcid_api_key:
        raise ValueError("\nPlease provide a valid ORCID API key: You can obtain a key from here: 'https://info.orcid.org/what-is-orcid/services/public-api/'")
    if not first_name or not last_name:
        raise ValueError("\nPlease provide a first name and a last name")
    else:
        orcid = retrieveORCIDinfo(first_name, last_name, orcid_api_key)

    return orcid