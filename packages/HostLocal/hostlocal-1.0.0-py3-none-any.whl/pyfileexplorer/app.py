from flask import Flask, render_template, send_from_directory, request, abort, redirect, url_for, jsonify
import os
import mimetypes
from datetime import datetime
import argparse

app = Flask(__name__, static_folder='static', template_folder='templates')

# Define the base folder (host directory's parent)
BASE_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def get_file_info(entry):
    path = entry.path
    name = entry.name
    is_dir = entry.is_dir()
    stat = entry.stat()
    is_hidden = name.startswith('.') or name.startswith('~') or name == 'desktop.ini'

    return {
        'name': name,
        'is_dir': is_dir,
        'is_hidden': is_hidden,
        'size': "-" if is_dir else f"{stat.st_size / 1024:.2f} KB",
        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
    }


@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def index(path):
    query = request.args.get('q', '').lower()
    target_path = os.path.join(BASE_FOLDER, path)

    if not os.path.exists(target_path):
        return abort(404)

    # Handle file upload (batch upload support)
    if request.method == 'POST' and 'file' in request.files:
        files = request.files.getlist('file')
        uploaded = []
        for file in files:
            if file and file.filename:
                save_path = os.path.join(target_path, file.filename)
                file.save(save_path)
                uploaded.append(file.filename)
        # Check if AJAX (fetch) upload
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'message': f'Uploaded: {", ".join(uploaded)}'}), 200
        return redirect(request.url)

    try:
        entries = [get_file_info(entry) for entry in os.scandir(target_path)]
        if query:
            entries = [f for f in entries if query in f['name'].lower()]
        entries.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
        return render_template('index.html', files=entries, current_path=path)
    except Exception as e:
        return f"<h2>Error: {str(e)}</h2>", 500


@app.route('/files/<path:filename>')
def serve_file(filename):
    full_path = os.path.join(BASE_FOLDER, filename)
    if not os.path.isfile(full_path):
        return abort(404)
    dir_name = os.path.dirname(full_path)
    file_name = os.path.basename(full_path)
    return send_from_directory(directory=dir_name, path=file_name, as_attachment=False)


def main():
    parser = argparse.ArgumentParser(description='HostLocal - Local File Hosterr')
    parser.add_argument('-l', '--location', type=str, default=None, help='Path to host (base folder)')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to run the server on')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--debug', action='store_true', help='Enable Flask debug mode')
    args = parser.parse_args()

    global BASE_FOLDER
    if args.location:
        BASE_FOLDER = os.path.abspath(args.location)
    else:
        BASE_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    app.run(debug=args.debug, port=args.port, host=args.host)


if __name__ == '__main__':
    main()
