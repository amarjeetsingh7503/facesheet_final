'''from flask import Flask, request, Response, jsonify
import json

from facesheet import generate_facesheet

app = Flask(__name__)


@app.route("/generate-facesheet", methods=["POST"])
def generate_facesheet_api():
    try:
        # Get JSON string from form-data OR raw JSON
        data = request.form.get("data")

        if not data:
            # fallback: raw JSON body
            json_data = request.get_json()
        else:
            json_data = json.loads(data)

        if not json_data:
            return jsonify({"status": "error", "message": "Missing data"}), 400

        # Generate facesheet PDF
        result_bytes = generate_facesheet(json_data)

        return Response(
            result_bytes,
            mimetype="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=facesheet.pdf"
            }
        )

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)'''

from flask import Flask, request, Response, jsonify
import json
import base64
import io

from facesheet import generate_facesheet
from PyPDF2 import PdfReader, PdfWriter

app = Flask(__name__)


# -----------------------------
# MERGE PDFs
# -----------------------------
def merge_pdfs(facesheet_bytes, resume_bytes):
    writer = PdfWriter()

    # Add facesheet FIRST
    facesheet_reader = PdfReader(io.BytesIO(facesheet_bytes))
    for page in facesheet_reader.pages:
        writer.add_page(page)

    # Add resume AFTER
    resume_reader = PdfReader(io.BytesIO(resume_bytes))
    for page in resume_reader.pages:
        writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)

    return output.read()


# -----------------------------
# API ROUTE
# -----------------------------
@app.route("/generate-facesheet", methods=["POST"])
def generate_facesheet_api():
    try:
        # ✅ Get JSON from raw POST
        json_data = request.get_json()

        if not json_data:
            return jsonify({"status": "error", "message": "Missing JSON"}), 400

        # Extract candidate data & resume
        candidate_list = json_data.get("candidateData", [])
        resume_base64 = json_data.get("resumeFile")

        if not candidate_list or not resume_base64:
            return jsonify({"status": "error", "message": "Invalid payload"}), 400

        candidate = candidate_list[0]

        # Generate facesheet
        facesheet_bytes = generate_facesheet(candidate)

        # Decode resume
        resume_bytes = base64.b64decode(resume_base64)

        # Merge facesheet + resume
        merged_pdf = merge_pdfs(facesheet_bytes, resume_bytes)

        return Response(
            merged_pdf,
            mimetype="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=facesheet_merged.pdf"
            }
        )

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)