# /var/www/abstractendeavors/secure-files/big_man/flask_app/login_app/routes.py
from ....imports import *
# ──────────────────────────────────────────────────────────────────────────────
# 2) Hard‐code the absolute path to your “public/” folder, where index.html, login.html, main.js live:
# Make a folder named “uploads” parallel to “public”:
from typing import Optional, Union, Dict, Any, List
from flask import Request
from werkzeug.datastructures import MultiDict, FileStorage
from abstract_logins.query_utils.py.ip_queries.userIpManager import UserIPManager
from abstract_logins.query_utils.py.user_queries.userManager import UserManager
from abstract_database import update_any_combo,fetch_any_combo
import json


ensure_blacklist_table_exists()
secure_settings_bp, logger = get_bp('secure_settings_bp',
                                    __name__,
                                    url_prefix=URL_PREFIX,
                                    static_folder = STATIC_FOLDER)
def get_all_key_unfos(req):
    keys =["created_at",
           "download_count",
           "download_limit",
           "filename",
           "filepath",
           "fullpath",
           "id",
           "share_password",
           "shareable",
           "uploader_id",
           "is_shareable",
           "needsPassword",
           "downloadPassword",
           "max_downloads"]           
    username = req.user['username']
    data = parse_and_spec_vars(req,keys)
    created_at = data.get("created_at",datetime.utcnow())
    download_count = data.get("download_count",0)
    download_limit = data.get("download_limit",None)
    filename = data.get("filename",None)
    filepath = data.get("filepath",None)
    fullpath = data.get("fullpath",None)
    file_id = data.get("id",None)
    share_password = data.get("share_password", None)
    shareable = data.get("shareable", False)
    uploader_id = data.get("uploader_id",username)
    is_shareable = data.get("is_shareable",False)
    needsPassword = data.get("needsPassword", False)
    downloadPassword = data.get("downloadPassword",None)
    max_downloads = data.get("max_downloads",None)

def split_rel_path(rel_path: str):
    """Split 'foo/bar.txt' → ('foo', 'bar.txt')."""
    if '/' in rel_path:
        parts = rel_path.rsplit('/', 1)
        return parts[0], parts[1]
    return '', rel_path
def get_request_data(req):
    """Retrieve JSON data (for POST) or query parameters (for GET)."""
    if req.method == 'POST':
        return req.json
    else:
        return req.args.to_dict()

# only these columns may be toggled via the API:
ALLOWED_FIELDS = {
    'shareable':    'query_update_upload_shareable',
    'download_limit': 'query_update_upload_limit',
    'share_password': 'query_update_upload_password',
}

@secure_settings_bp.route(
    '/files/<int:file_id>/settings/<field>',
    methods=['PATCH']
)
@login_required
def patch_file_setting(file_id, field):
    # 1) Validate field
    key = ALLOWED_FIELDS.get(field)
    if not key:
        return jsonify(error="Invalid setting"), HTTPStatus.BAD_REQUEST

    # 2) Parse new value from body
    body = request.get_json(silent=True) or {}
    if 'value' not in body:
        return jsonify(error="Missing 'value' in JSON"), HTTPStatus.BAD_REQUEST
    new_value = body['value']

    # 3) Run the update via your manager
    #    assume you added a JSON entry like:
    #      query_update_upload_shareable: "UPDATE uploads SET shareable = %s WHERE id = %s"
    try:
        UPLOAD_MGR.run(
            key,
            new_value,
            file_id,
            commit=True
        )
    except Exception as e:
        return jsonify(error=str(e)), HTTPStatus.INTERNAL_SERVER_ERROR

    # 4) Return the updated record or a 204
    updated = UPLOAD_MGR.run('query_select_upload_from_id', file_id, one=True)
    return jsonify(updated), HTTPStatus.OK
@secure_settings_bp.route('/files/share', methods=['PATCH'])
@login_required
def share_settings():
    request_data = extract_request_data(request)
    data = request_data.get('json')
    logger.info(data)
    username = request.user['username']
    data = request.get_json() or {}
    
    keys =["created_at",
           "download_count",
           "download_limit",
           "filename",
           "filepath",
           "fullpath",
           "id",
           "share_password",
           "shareable",
           "uploader_id",
           "is_shareable",
           "needsPassword",
           "downloadPassword",
           "max_downloads"]  
    """
    PATCH /files/share
    Body JSON:
      {
        "id":               <int>,
        "shareable":        <bool>,
        "downloadPassword": "<string>" or "", 
        "download_limit":   <int> or null
      }
    """
    sample_js = {"created_at":None,
                 "download_count":None,
                 "download_limit":None,
                 "filename":None,
                 "filepath":None,
                 "fullpath":None,
                 "id":None,
                 "share_password":None,
                 "shareable":None,
                 "uploader_id":None,
                 "is_shareable":None,
                 "needsPassword":None,
                 "downloadPassword":None,
                 "max_downloads":None}
    
    file_id       = data.get('id')
    
    
    search_keys = [
        "id"
        ]
    search_map={}
    update_keys = [
            "download_count",
            "download_limit",
            "share_password",
            "shareable",
            "is_shareable",
            "needsPassword",
            "downloadPassword",
            "max_downloads"
            ]
    try:
        update_map={}
        for key in search_keys:
            if key in data:
                value = data.get(key)
                if key == 'id':
                    value = int(value)
                search_map[key] = value
        logger.info(f"search_map == {search_map}")
        if search_map:
            row = fetch_any_combo(column_names='*',
                                  table_name='uploads',
                                  search_map=search_map)
            if isinstance(row,list) and len(row) ==1:
                row = row[0]
            total_row = row.copy()
            
            if row.get('uploader_id') != username:
                return jsonify(message="Forbidden"), 403
            if isinstance(row,list) and len(row) == 1:
                row = row[0]
            if not row:
                return jsonify(message="File not found"), 404
            for key in update_keys:
                if key in data and key not in ["needsPassword"]:
                    value = data.get(key)
                    if key in ["shareable","is_shareable"]:
                       key = "shareable"
                       value  = update_map.get("shareable") or update_map.get("is_shareable") or value
                    if key in ["needsPassword","downloadPassword"]:
                        key = "share_password"
                        value  = update_map.get("share_password") or update_map.get("downloadPassword") or update_map.get("needsPassword") or value
                    if key in ["max_downloads","download_limit"]:
                        key = "download_limit"
                        value  = update_map.get("download_limit") or update_map.get("max_downloads") or value
                    update_map[key] = value
                    total_row[key] = value
            logger.info(f"update_map == {update_map}")
            if update_map:
                share_password = total_row.get("share_password")
                download_url=None
                shareable = total_row["shareable"]
                fullpath = total_row.get('fullpath')
                if not shareable:
                    for key in ["download_limit","share_password"]:
                        if total_row[key] != None:
                            update_map[key] = value
                            total_row[key] = value
                else:
                    token = generate_download_token(
                          username=username,
                          rel_path=fullpath,
                          exp=3600*24
                          )
                    if share_password:
                        pass_hash = bcrypt.hashpw(share_password.encode(), bcrypt.gensalt()).decode()
                    download_url = url_for('secure_download_bp.download_with_token',token=token, _external=True)
                

                
                    update_any_combo(table_name='uploads',
                                  update_map=update_map,
                                  search_map=search_map)
                
                response = {"message": "Settings updated"}
                if download_url:
                    response["download_url"] = download_url
                return jsonify(response), 200
            else:
                return jsonify(message="no ssettings to update"), 404
        else:
            return jsonify(message="no ssettings to update"), 404  
    except Exception as e:
        logger.error(f"DB error: {e}")
        return jsonify({"message": "Unable to update settings"}), 500
