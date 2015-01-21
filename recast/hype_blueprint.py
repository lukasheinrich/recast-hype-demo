from flask import Blueprint, render_template, jsonify, request
blueprint = Blueprint('hype_analysis', __name__, template_folder='hype_templates')

RECAST_ANALYSIS_ID = 'ce317406-8e8d-8a54-d9a5-899b6d50f176'

import json
import requests
import hype_backendtasks
import requests
import os
from zipfile import ZipFile
import glob

@blueprint.route('/result/<requestId>/<parameter_pt>/limits')
def limits(requestId,parameter_pt):
  results =  hype_backendtasks.results(requestId,parameter_pt)
  return jsonify(results=results)

@blueprint.route('/result/<requestId>/<parameter_pt>')
def result_view(requestId,parameter_pt):
  return render_template('hype_result.html',analysisId = RECAST_ANALYSIS_ID,requestId=requestId,parameter_pt=parameter_pt)


