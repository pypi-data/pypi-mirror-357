from ...imports import *
secure_upload_bp = Blueprint('secure_upload_bp', __name__)
@secure_upload_bp.route("/upload", methods=['GET','POST'])
@secure_upload_bp.route('/upload/<path:rel_path>', methods=['GET','POST'])
@login_required
def upload_file():
    initialize_call_log()
    user_name = get_user_name(req=request)
    if not user_name:
        logger.error("Missing user_name")
        return jsonify({"message": "Missing user_name"}), 400

    if 'file' not in request.files:
        logger.error(f"No file in request.files: {request.files}")
        return jsonify({"message": "No file provided."}), 400

    file = request.files['file']
    if not file or not file.filename:
        logger.error("No file selected or empty filename")
        return jsonify({"message": "No file selected."}), 400

    filename = secure_filename(file.filename)
    if not filename:
        logger.error("Invalid filename after secure_filename")
        return jsonify({"message": "Invalid filename."}), 400
    kwargs = parse_and_spec_vars(request,['shareable','download_count','download_limit','share_password'])
    shareable = kwargs.get('shareable',False)
    download_count = kwargs.get('download_count',0)
    download_limit = kwargs.get('download_limit',None)
    share_password = kwargs.get('share_password',False)
    user_upload_dir = get_user_upload_dir(req=request, user_name=user_name)
    safe_subdir = get_safe_subdir(req=request) or ''
    user_upload_subdir = os.path.join(user_upload_dir, safe_subdir)
    os.makedirs(user_upload_subdir, exist_ok=True)
    full_path = os.path.join(user_upload_subdir, filename)
    logger.info(f"Received: file={filename}, subdir={safe_subdir}")
    file.save(full_path)
    rel_path = os.path.relpath(full_path, ABS_UPLOAD_ROOT)
    file_id = create_file_id(
                        filename=filename,
                        filepath=rel_path,
                        uploader_id= user_name,
                        shareable=shareable or False,
                        download_count=download_count or 0,
                        download_limit=download_limit or None,
                        share_password=share_password or False,
                    )
    




    return jsonify({
            "message": "File uploaded successfully.",
            "filename": filename,
            "filepath": rel_path,
            "file_id": file_id,
            "uploader_id": user_name,
            "shareable": shareable,
            "download_count": download_count,
            "download_limit": download_limit,
            "share_password": share_password,
        }), 200

