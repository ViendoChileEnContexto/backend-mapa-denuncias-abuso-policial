import json
from os import environ
from time import time

import gspread
from flask import make_response
from oauth2client.service_account import ServiceAccountCredentials as SAC
from werkzeug.exceptions import InternalServerError


SHEET_ID = environ.get("SHEET_ID", "")


def _append_to_sheet(sheet_id, values):
    scopes = ['https://www.googleapis.com/auth/drive']
    cred = {
        "type": environ.get("TYPE", ""),
        "project_id": environ.get("PROJECT_ID", ""),
        "private_key_id": environ.get("PRIVATE_KEY_ID", ""),
        "private_key": environ.get("PRIVATE_KEY", "").replace("\\n", "\n"),
        "client_email": environ.get("CLIENT_EMAIL", ""),
        "client_id": environ.get("CLIENT_ID", ""),
        "auth_uri": environ.get("AUTH_URI", ""),
        "token_uri": environ.get("TOKEN_URI", ""),
        "auth_provider_x509_cert_url": environ.get("AUTH_PROVIDER", ""),
        "client_x509_cert_url": environ.get("CLIENT", ""),
    }
    credentials = SAC.from_json_keyfile_dict(cred, scopes)
    client = gspread.authorize(credentials)
    sheet = client.open_by_key(sheet_id)
    worksheet = sheet.sheet1
    worksheet.append_row(values)


def post_report(app, request):
    """
    Handle a report writing to a Google Sheet
    Fetches the report attributes and registers them in a Google Sheet
    with the timestamp of the event.
    """
    payload = request.get_json()
    try:
        attrs = {
            attr["name"]: attr["value"]
            for attr in payload
        }
    except (KeyError, TypeError) as e:
        raise BadRequest() from e

    try:
        timestamp = time()
        link = attrs.get("Link", "")
        label = attrs.get("Etiqueta", "")
        place = attrs.get("Lugar", "")
        lat = attrs.get("Latitud", "")
        lon = attrs.get("Longitud", "")
        desc = attrs.get("Description", "")
        _append_to_sheet(SHEET_ID, [
            str(timestamp), link, label, place, str(lat), str(lon), desc,
        ])
    except gspread.exceptions.GSpreadException:
        raise InternalServerError(description="Reporte no registrado (GSpreadException)")
    except Exception as e:
        raise InternalServerError(description=e.description)
    return make_response("Reporte recibido exitosamente", 200)
