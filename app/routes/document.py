import os
import uuid
import zipfile

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
    abort
)

from flask_login import (
    login_required,
    current_user
)

from werkzeug.utils import secure_filename

from app import db, limiter

from app.models.document import Document
from app.models.match_result import MatchResult

from app.services.document_processing_service import (
    process_and_store_document
)

from app.services.document_matching_service import (
    match_document_pair
)

from app.services.exporters.xlsx_exporter import (
    export_match_result_to_xlsx
)

from app.services.exporters.pdf_exporter import (
    export_match_result_to_pdf
)

from app.services.exporters.docx_exporter import (
    export_match_result_to_docx
)

from app.services.exporters.txt_exporter import (
    export_match_result_to_txt
)


document = Blueprint(
    "document",
    __name__,
    url_prefix="/documents"
)


ALLOWED_EXTENSIONS = {
    "xlsx",
    "docx",
    "pdf",
    "txt",
    "png",
    "jpg",
    "jpeg"
}


MAX_FILE_SIZE = 10 * 1024 * 1024


def get_project_root():
    return os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    )


def get_upload_folder():
    return os.path.join(
        get_project_root(),
        "uploads"
    )


def get_output_folder():
    return os.path.join(
        get_project_root(),
        "outputs"
    )


def allowed_file(filename):

    if not filename:
        return False

    if "." not in filename:
        return False

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    return extension in ALLOWED_EXTENSIONS


def validate_file_content(
    file_path,
    extension
):

    try:

        if extension in {
            "xlsx",
            "docx"
        }:

            with zipfile.ZipFile(
                file_path,
                "r"
            ) as archive:

                if archive.testzip() is not None:
                    return False

            return True

        if extension == "pdf":

            with open(
                file_path,
                "rb"
            ) as file:

                header = file.read(5)

            return header == b"%PDF-"

        if extension == "png":

            with open(
                file_path,
                "rb"
            ) as file:

                header = file.read(8)

            return header == (
                b"\x89PNG\r\n\x1a\n"
            )

        if extension in {
            "jpg",
            "jpeg"
        }:

            with open(
                file_path,
                "rb"
            ) as file:

                header = file.read(3)

            return header == b"\xff\xd8\xff"

        if extension == "txt":

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                file.read(4096)

            return True

        return False

    except Exception:

        return False


@document.route(
    "/upload",
    methods=["GET", "POST"]
)
@login_required
@limiter.limit(
    "20 per minute",
    methods=["POST"]
)
def upload():

    if request.method == "POST":

        if "file" not in request.files:

            flash(
                "No file was selected.",
                "error"
            )

            return redirect(
                url_for("document.upload")
            )

        file = request.files["file"]

        if not file or not file.filename:

            flash(
                "Please select a file.",
                "error"
            )

            return redirect(
                url_for("document.upload")
            )

        if not allowed_file(
            file.filename
        ):

            flash(
                "Unsupported file type.",
                "error"
            )

            return redirect(
                url_for("document.upload")
            )

        extension = file.filename.rsplit(
            ".",
            1
        )[1].lower()

        file.seek(
            0,
            os.SEEK_END
        )

        file_size = file.tell()

        file.seek(0)

        if file_size > MAX_FILE_SIZE:

            flash(
                "File size exceeds the 10 MB limit.",
                "error"
            )

            return redirect(
                url_for("document.upload")
            )

        safe_original_name = secure_filename(
            file.filename
        )

        if not safe_original_name:

            flash(
                "Invalid filename.",
                "error"
            )

            return redirect(
                url_for("document.upload")
            )

        stored_name = (
            f"{uuid.uuid4().hex}.{extension}"
        )

        upload_folder = get_upload_folder()

        os.makedirs(
            upload_folder,
            exist_ok=True
        )

        file_path = os.path.join(
            upload_folder,
            stored_name
        )

        try:

            file.save(
                file_path
            )

            if not validate_file_content(
                file_path,
                extension
            ):

                if os.path.exists(file_path):

                    os.remove(
                        file_path
                    )

                flash(
                    "The uploaded file content is invalid.",
                    "error"
                )

                return redirect(
                    url_for("document.upload")
                )

            new_document = Document(
                user_id=current_user.id,
                original_name=safe_original_name,
                stored_name=stored_name,
                original_type=extension,
                status="uploaded"
            )

            db.session.add(
                new_document
            )

            db.session.commit()

            processing_result = (
                process_and_store_document(
                    document_id=new_document.id,
                    user_id=current_user.id
                )
            )

            if processing_result.get(
                "success"
            ):

                flash(
                    (
                        "File uploaded and processed "
                        "successfully. Records: "
                        f"{processing_result.get('record_count', 0)}"
                    ),
                    "success"
                )

            else:

                flash(
                    (
                        "File uploaded, but processing failed: "
                        f"{processing_result.get('error', 'Unknown error')}"
                    ),
                    "error"
                )

            return redirect(
                url_for("document.upload")
            )

        except Exception as error:

            db.session.rollback()

            if os.path.exists(file_path):

                try:

                    os.remove(
                        file_path
                    )

                except OSError:

                    pass

            flash(
                f"Upload failed: {error}",
                "error"
            )

            return redirect(
                url_for("document.upload")
            )

    return render_template(
        "documents/upload.html"
    )


@document.route(
    "/download/<int:document_id>"
)
@login_required
def download_document(
    document_id
):

    document_record = db.session.get(
        Document,
        document_id
    )

    if document_record is None:
        abort(404)

    if document_record.user_id != current_user.id:
        abort(403)

    upload_folder = get_upload_folder()

    file_path = os.path.join(
        upload_folder,
        document_record.stored_name
    )

    if not os.path.isfile(
        file_path
    ):

        abort(404)

    return send_from_directory(
        upload_folder,
        document_record.stored_name,
        as_attachment=True,
        download_name=document_record.original_name
    )


@document.route(
    "/match",
    methods=["GET", "POST"]
)
@login_required
def match():

    documents = Document.query.filter_by(
        user_id=current_user.id,
        status="processed"
    ).order_by(
        Document.id.asc()
    ).all()

    if request.method == "GET":

        return render_template(
            "documents/match.html",
            documents=documents
        )

    main_document_id = request.form.get(
        "main_document_id"
    )

    secondary_document_id = request.form.get(
        "secondary_document_id"
    )

    if (
        not main_document_id
        or not secondary_document_id
    ):

        flash(
            "Please select both documents.",
            "error"
        )

        return redirect(
            url_for("document.match")
        )

    try:

        main_document_id = int(
            main_document_id
        )

        secondary_document_id = int(
            secondary_document_id
        )

    except ValueError:

        flash(
            "Invalid document selection.",
            "error"
        )

        return redirect(
            url_for("document.match")
        )

    main_document = db.session.get(
        Document,
        main_document_id
    )

    secondary_document = db.session.get(
        Document,
        secondary_document_id
    )

    if main_document is None:
        abort(404)

    if secondary_document is None:
        abort(404)

    if main_document.user_id != current_user.id:
        abort(403)

    if secondary_document.user_id != current_user.id:
        abort(403)

    if main_document_id == secondary_document_id:

        flash(
            "Main and Secondary documents must be different.",
            "error"
        )

        return redirect(
            url_for("document.match")
        )

    result = match_document_pair(
        main_document_id=main_document_id,
        secondary_document_id=secondary_document_id,
        user_id=current_user.id
    )

    if not result.get("success"):

        flash(
            result.get(
                "error",
                "Matching failed."
            ),
            "error"
        )

        return redirect(
            url_for("document.match")
        )

    output_folder = get_output_folder()

    os.makedirs(
        output_folder,
        exist_ok=True
    )

    output_id = uuid.uuid4().hex

    output_filename = (
        f"match_result_{output_id}.xlsx"
    )

    pdf_filename = (
        f"match_result_{output_id}.pdf"
    )

    docx_filename = (
        f"match_result_{output_id}.docx"
    )

    txt_filename = (
        f"match_result_{output_id}.txt"
    )

    output_path = os.path.join(
        output_folder,
        output_filename
    )

    pdf_path = os.path.join(
        output_folder,
        pdf_filename
    )

    docx_path = os.path.join(
        output_folder,
        docx_filename
    )

    txt_path = os.path.join(
        output_folder,
        txt_filename
    )

    export_result = export_match_result_to_xlsx(
        result,
        output_path
    )

    pdf_export_result = export_match_result_to_pdf(
        result,
        pdf_path
    )

    docx_export_result = export_match_result_to_docx(
        result,
        docx_path
    )

    txt_export_result = export_match_result_to_txt(
        result,
        txt_path
    )

    if export_result.get("success"):

        match_result_record = MatchResult(
            user_id=current_user.id,
            filename=output_filename
        )

        db.session.add(
            match_result_record
        )

        db.session.commit()

    return render_template(
        "documents/match_result.html",
        result=result,
        export_result=export_result,
        pdf_export_result=pdf_export_result,
        docx_export_result=docx_export_result,
        txt_export_result=txt_export_result,
        output_filename=output_filename,
        pdf_filename=pdf_filename,
        docx_filename=docx_filename,
        txt_filename=txt_filename,
        main_document_name=main_document.original_name,
        secondary_document_name=secondary_document.original_name
    )


@document.route(
    "/download-result/<filename>"
)
@login_required
def download_result(filename):

    if not filename.endswith(
        ".xlsx"
    ):

        abort(404)

    safe_filename = secure_filename(
        filename
    )

    if safe_filename != filename:

        abort(404)

    match_result = MatchResult.query.filter_by(
        filename=safe_filename,
        user_id=current_user.id
    ).first()

    if match_result is None:

        abort(403)

    output_folder = get_output_folder()

    file_path = os.path.join(
        output_folder,
        safe_filename
    )

    if not os.path.isfile(
        file_path
    ):

        abort(404)

    return send_from_directory(
        output_folder,
        safe_filename,
        as_attachment=True,
        download_name=safe_filename
    )


@document.route(
    "/download-pdf-result/<filename>"
)
@login_required
def download_pdf_result(filename):

    if not filename.endswith(
        ".pdf"
    ):

        abort(404)

    safe_filename = secure_filename(
        filename
    )

    if safe_filename != filename:

        abort(404)

    xlsx_filename = (
        os.path.splitext(
            safe_filename
        )[0]
        + ".xlsx"
    )

    match_result = MatchResult.query.filter_by(
        filename=xlsx_filename,
        user_id=current_user.id
    ).first()

    if match_result is None:

        abort(403)

    output_folder = get_output_folder()

    file_path = os.path.join(
        output_folder,
        safe_filename
    )

    if not os.path.isfile(
        file_path
    ):

        abort(404)

    return send_from_directory(
        output_folder,
        safe_filename,
        as_attachment=True,
        download_name=safe_filename
    )


@document.route(
    "/download-docx-result/<filename>"
)
@login_required
def download_docx_result(filename):

    if not filename.endswith(
        ".docx"
    ):

        abort(404)

    safe_filename = secure_filename(
        filename
    )

    if safe_filename != filename:

        abort(404)

    xlsx_filename = (
        os.path.splitext(
            safe_filename
        )[0]
        + ".xlsx"
    )

    match_result = MatchResult.query.filter_by(
        filename=xlsx_filename,
        user_id=current_user.id
    ).first()

    if match_result is None:

        abort(403)

    output_folder = get_output_folder()

    file_path = os.path.join(
        output_folder,
        safe_filename
    )

    if not os.path.isfile(
        file_path
    ):

        abort(404)

    return send_from_directory(
        output_folder,
        safe_filename,
        as_attachment=True,
        download_name=safe_filename
    )


@document.route(
    "/download-txt-result/<filename>"
)
@login_required
def download_txt_result(filename):

    if not filename.endswith(
        ".txt"
    ):

        abort(404)

    safe_filename = secure_filename(
        filename
    )

    if safe_filename != filename:

        abort(404)

    xlsx_filename = (
        os.path.splitext(
            safe_filename
        )[0]
        + ".xlsx"
    )

    match_result = MatchResult.query.filter_by(
        filename=xlsx_filename,
        user_id=current_user.id
    ).first()

    if match_result is None:

        abort(403)

    output_folder = get_output_folder()

    file_path = os.path.join(
        output_folder,
        safe_filename
    )

    if not os.path.isfile(
        file_path
    ):

        abort(404)

    return send_from_directory(
        output_folder,
        safe_filename,
        as_attachment=True,
        download_name=safe_filename
    )


@document.route(
    "/compare-all",
    methods=["GET"]
)
@login_required
def compare_all():

    documents = Document.query.filter_by(
        user_id=current_user.id,
        status="processed"
    ).order_by(
        Document.id.asc()
    ).all()

    if len(documents) < 2:

        flash(
            "You need at least two documents to compare.",
            "error"
        )

        return redirect(
            url_for("auth.dashboard")
        )

    comparison_results = []

    for i in range(len(documents)):

        for j in range(i + 1, len(documents)):

            print(
                f"COMPARING {documents[i].id} vs {documents[j].id}",
                flush=True
            )

            main_document = documents[i]
            secondary_document = documents[j]

            result = match_document_pair(
                main_document_id=main_document.id,
                secondary_document_id=secondary_document.id,
                user_id=current_user.id
            )

            if result.get("success"):

                comparison_results.append(
                    result
                )

            print(
                f"DONE {documents[i].id} vs {documents[j].id}",
                flush=True
            )

    return render_template(
        "documents/compare_all_result.html",
        comparison_results=comparison_results
    )