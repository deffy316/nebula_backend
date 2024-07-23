import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from Marigold import marigold_helper as mrg
import glob

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})


UPLOAD_FOLDER = "Marigold/input"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/api", methods=["GET"])
def api_root():
    return jsonify(message="Welcome to API")


@app.route("/upload", methods=["POST"])
def upload_image():
    if "file" not in request.files:
        return jsonify({"message": "No file part"}), 400

    sId = request.form.get("sessionId")
    file = request.files["file"]

    if not sId:
        return jsonify({"message": "Session Id is missing"}), 400
    if file.filename == "":
        return jsonify({"message": "No selected file"}), 400

    if file:

        filename = secure_filename(file.filename)
        # Extract the base name without extension
        file_basename, file_extension = os.path.splitext(filename)
        # Change file name to session id
        filename = "".join([sId, file_extension])
        # Create a directory with the session name
        file_dir = os.path.join(app.config["UPLOAD_FOLDER"], sId)
        os.makedirs(file_dir, exist_ok=True)
        # Save the file inside this directory
        file_path = os.path.join(file_dir, filename)
        file.save(file_path)
        return (
            jsonify(
                {
                    "message": "File uploaded successfully",
                    "filename": filename,
                    "filepath": file_path,
                }
            ),
            200,
        )


@app.route("/file", methods=["GET"])
def get_file():
    filename = request.args.get("filename")

    # Validate the parameter
    if not filename:
        return jsonify(message="Filename parameter is missing"), 400

    # Sanitize the filename to prevent path traversal attacks
    if ".." in filename or filename.startswith("/"):
        return jsonify(message="Invalid filename"), 400

    # Define the directory containing the files
    file_directory = "/home/def/Marigold/input/"

    # Create the full file path
    file_path = os.path.join(file_directory, filename)

    # Check if the file exists
    if not os.path.isfile(file_path):
        return jsonify(message="File not found"), 404

    # Read the file content (as an example, you can do other operations as needed)
    with open(file_path, "r") as file:
        file_content = file.read()

    # Return the file content in the response
    return jsonify(content=file_content)


@app.route("/marigold", methods=["GET"])
def run_marigold():

    sId = request.args.get("sessionId")
    main_input_dir = "Marigold/input"
    main_output_dir = "Marigold/output"
    input_path = os.path.join(main_input_dir, sId)
    output_path = os.path.join(main_output_dir, sId)

    # run model
    if mrg.depth_estimate(input_path, output_path) == 0:
        return jsonify(message="Model ran successfully"), 200
    else:
        return jsonify(message="There is something wrong at our end"), 500


@app.route("/marigold/layer", methods=["GET"])
def layer():

    sId = request.args.get("sessionId")
    start = float(request.args.get("start"))
    end = float(request.args.get("end"))
    index = int(request.args.get("index"))

    if not (sId or start or end or index):
        return jsonify(message="Parameter is missing"), 400

    rgb_dir = "/home/def/nebula_backend/my_api_server/Marigold/input"
    layer_dir = "/home/def/nebula_backend/my_api_server/Marigold/layer"
    npy_dir = "/home/def/nebula_backend/my_api_server/Marigold/output"

    layer_path = os.path.join(layer_dir, sId)
    rgb_path = os.path.join(rgb_dir, sId)
    npy_path = os.path.join(os.path.join(npy_dir, sId), f"{sId}.npy")

    os.makedirs(layer_path, exist_ok=True)
    
    file_name = str(index) + ".png"
    file_path = os.path.join(layer_path, file_name)
    # try:
    mrg.display_depth_range(
        rgb_path=rgb_path,
        depth_path=npy_path,
        min_depth=start,
        max_depth=end,
        output_path=file_path,
    )
    return jsonify(message="Layering complete"), 200
    # except:
    #     return jsonify(message="There is something wrong at our end"), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
