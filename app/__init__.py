
from flask import Flask

webapp = Flask(__name__)


from app import courses
from app import fileupload
from app import main

