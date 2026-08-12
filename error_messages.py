import json
import re
import urllib.error
import xml.sax

import rdflib.plugin
from rdflib.plugins.parsers.notation3 import BadSyntax

from custom_exceptions import ResourceNotFoundError


def format_human_readable_error(e: Exception) -> str:
    if isinstance(e, urllib.error.HTTPError):
        return f"Could not download the catalog. The remote server returned an error: {e.code} {e.reason}."

    elif isinstance(e, urllib.error.URLError):
        return "Could not reach the catalog URL. Please check if the link is correct and the server is online."

    elif isinstance(e, rdflib.plugin.PluginException):
        error_msg = str(e)
        match = re.search(r"No plugin registered for \(([^,]+),", error_msg)
        if match:
            full_mime_type = match.group(1).strip()
            return f"Format error. The server returned an unsupported file format ({full_mime_type}). Ensure the endpoint supports Linked Data"
        return f"Format error. The server returned an unsupported file format. Details: {error_msg}."

    elif isinstance(
        e, (xml.sax.SAXParseException, json.decoder.JSONDecodeError, BadSyntax)
    ):
        return "Syntax error. The catalog data was downloaded but contains malformed syntax."

    elif isinstance(e, ResourceNotFoundError):
        return f"Internal Database Error: {e!s}"

    else:
        return f"An unexpected error occurred: {e!s}"
