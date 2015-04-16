from flask import Blueprint, render_template, jsonify, request
blueprint = Blueprint('hype_analysis', __name__, template_folder='templates')

import json
import requests
import requests
import os
from zipfile import ZipFile
import glob
import yaml

from recastbackend.resultaccess import resultfilepath

@blueprint.route('/result/<requestId>/<parameter_pt>')
def result_view(requestId,parameter_pt):
    results = None
    with open(resultfilepath(requestId,parameter_pt,'dedicated','/results.yaml')) as f:
        results = yaml.load(f)

    print results
    return render_template('hype_result.html',results = results, requestId=requestId,parameter_pt=parameter_pt)


