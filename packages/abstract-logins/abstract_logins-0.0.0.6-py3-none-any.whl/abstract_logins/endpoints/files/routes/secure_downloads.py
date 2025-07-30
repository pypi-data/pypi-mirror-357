from flask import Response
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from abstract_database import update_any_combo,fetch_any_combo
from ...imports import *
secure_download_bp = Blueprint('secure_download_bp', __name__)
def get_file_inits(req,file_id=None):
    request_data = extract_request_data(req)
    data = request_data.get('json',{})
    args = request_data.get('args',[])
    logger.info(request_data)
    username = get_user_name(req=req)
    search_map={}
    pwd_given=None
    if 'rel_path' in data:
        search_map['rel_path']= data.get('rel_path')
    if 'id' in data or 'file_id' in data or file_id:
        inetger = file_id or data.get('id') or data.get('file_id')
        if inetger is not None:
            search_map['id']= int(inetger)
    if search_map == {}:
        return get_json_call_response('Missing file path. and missing id.', 400)
    if 'pwd' in data:
        pwd_given = data.get('pwd')
    return search_map,pwd_given,username
def add_to_download_count(search_map):
    if not isinstance(search_map,dict):
        if is_number(search_map):
            search_map = {"id":search_map}
    columnName = ["download_count","download_limit"]
    result = fetch_any_combo(column_names=columnName,
                                 table_name='uploads',
                                 search_map=search_map)
    download_count = result[0].get(columnName[0])
    download_limit = result[0].get(columnName[1])
    new_count = int(download_count) + 1
    if download_limit and new_count > download_limit:
        return 'Download limit reached.'
   
    update_any_combo(table_name='uploads',
                                  update_map={columnName[0]:new_count},
                                  search_map=search_map)

    return new_count
def get_path_and_filename(filepath):
    abs_path = os.path.join(ABS_UPLOAD_DIR, filepath)
    if not os.path.isfile(abs_path):
        return False,'File missing on disk.'
    basename = os.path.basename(abs_path)
    filename,ext = os.path.splitext(basename)
    return abs_path,filename

def get_download(req,file_id=None):
    search_map,pwd_given,username = get_file_inits(req,file_id=file_id)
    column_names = ['uploader_id','shareable','filepath','share_password']
    # fetch metadata
    row = fetch_any_combo(column_names='*',
                                 table_name='uploads',
                         search_map=search_map)
    logger.info(row)
    if not row:
        return get_json_call_response('File not found.', 404)
    if len(row) == 1:
        row = row[0]
    uploader_id = row['uploader_id']
    is_user = uploader_id == username
    shareable = row['shareable']
    logger.info(f"shareable={shareable}")
    if shareable == False and not is_user:
        return 'not allowed', 404
    filepath = row['filepath']
    # optional password check, limit check, increment count…
    abs_path,filename = get_path_and_filename(filepath)
    if not abs_path:
        return filename, 404
    share_password = row['share_password']
    if share_password:
        if not verify_password(pwd_given, share_password):
            return 'Incorrect password.', 401
    new_count = add_to_download_count(search_map)
    if not isinstance(new_count,int):
        return new_count, 404
    return abs_path,filename
@secure_download_bp.route('/download', methods=['POST','GET'])
@login_required
def downloadFile():
    initialize_call_log()
    abs_path,filename = get_download(request)
    if isinstance(filename,int):
        return get_json_call_response(abs_path, filename)
    return send_file(
        abs_path,
        as_attachment=True,
        download_name=filename)
            
@secure_download_bp.route('/secure-files/download/<path:file_id>', methods=['GET'])
def download_file(file_id=None):
    initialize_call_log()
    abs_path,filename = get_download(request,file_id=file_id)
    if isinstance(filename,int):
        return get_json_call_response(abs_path, filename)
    return send_file(
        abs_path,
        as_attachment=True,
        download_name=filename)


secure_limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
@secure_download_bp.route("/download/token/<token>")
@secure_limiter.limit("10 per minute")
@login_required
def download_with_token(token):
    initialize_call_log()
    try:
        data = decode_token(token)
    except jwt.ExpiredSignatureError:
        return get_json_call_response("Download link expired.", 410)
    except jwt.InvalidTokenError:
        return get_json_call_response("Invalid download link.", 400)
    # Check that the token’s user matches the logged-in user
    if data["sub"] != get_user_name(request):
        return get_json_call_response("Unauthorized.", 403)
    # Then serve exactly like before, using data["path"]
    return _serve_file(data["path"])

def _serve_file(rel_path: str):
    # after all your checks…
    internal_path = f"/protected/{rel_path}"
    resp = Response(status=200)
    resp.headers["X-Accel-Redirect"] = internal_path
    # optionally set download filename:
    resp.headers["Content-Disposition"] = (
        f'attachment; filename="{os.path.basename(rel_path)}"'
    )
    return resp
