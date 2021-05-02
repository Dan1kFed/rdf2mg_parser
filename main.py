import os
from flask import Flask, request, render_template, abort, send_file
import json
import os

import processor

app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route('/get-files/<path:path>', methods = ['GET', 'POST'])
def get_files(path):
    try:
        return send_file(path, as_attachment=True)
    except FileNotFoundError:
        abort(404)


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'GET':
        return render_template('index.html')

    if request.method == 'POST':
        file = request.files["file"]
        attr_list = request.form["attr_list"]
        ban_list = request.form["ban_list"]
        oriented = request.form["oriented"]
        print(file.filename, ' ', attr_list, ' ', ban_list, ' ', oriented, ' ')
        inp_json = processor.JSONParser.download_to_JSON(ttlfile = file,
                                                         ban_list = ban_list,
                                                         attr_list = attr_list,
                                                         oriented = oriented)
        clusters = processor.LengthCluster.markov_clustering(inp_json)
        out = processor.JSONParser.output_to_JSON(clusters, inp_json)
        with open('result.json', 'w') as fp:
            json.dump(out, fp)
        return get_files('result.json')
    # os.remove('result.json')


if __name__ == '__main__':
    app.run(threaded=False, debug = True)
