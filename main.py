import os
from flask import Flask, request, render_template, abort

import processor

app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    try:
        if request.method == 'GET':
            return render_template('index.html')

        if request.method == 'POST':
            filename = request.files["filename"]
            attr_list = request.form["attr_list"]
            ban_list = request.form["ban_list"]
            oriented = request.form["oriented"]
            print(filename, ' ', attr_list, ' ', ban_list, ' ', oriented, ' ')
            inp_json = processor.JSONParser.download_to_JSON(ttlfile = filename,
                                                      ban_list = ban_list,
                                                      attr_list = attr_list,
                                                      oriented = oriented)
            print(inp_json)
            # clusters = processor.LengthCluster.markov_clustering(inp_json)
            # out = processor.JSONParser.output_to_JSON(clusters, inp_json)
            return render_template('index.html', filename=filename,
                                   attr_list=attr_list,
                                   ban_list = ban_list,
                                   oriented = oriented,
                                   down_file = 'down_file')
    except Exception:
        abort(500)


if __name__ == '__main__':
    app.run(threaded=True, debug = True)
