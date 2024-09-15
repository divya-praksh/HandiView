from flask import Blueprint, request, jsonify, send_file
from cv_processing.cv_module import get_hand_scale_factor, process_hand_gestures, release_resources
from rendering.renderer import render_3d

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return "3D Model Viewer with Gesture Recognition"

@bp.route('/render', methods=['GET'])
def render():
    scale_factor = get_hand_scale_factor()
    image_path = render_3d(scale_factor)
    return send_file(image_path, mimetype='image/png')

@bp.route('/cleanup', methods=['GET'])
def cleanup():
    release_resources()
    return "Resources released"
