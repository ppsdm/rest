import json, os
import pymysql
from tool import apm as apm
from tool import disc as disc
from tool import cfit as cfit
from tool import papi as papi
from tool import adkudag4 as adkudag4
from tool import gatb4 as gatb4, tese as tese, tkdinfo as tkdinfo, tkdanalogiverbal as tkdanalogiverbal, tkdidiot as tkdidiot, tpa as tpa, form as form
from tool import compre as compre
from tool import scale as scale
from flask import g

from dotenv import load_dotenv
import requests
from flask import Flask, jsonify, render_template, send_from_directory
import xml.etree.ElementTree as ET
from tool import scale
load_dotenv()

import logging
from controller import user_controller
from controller import interpret_controller
from controller import result_controller
from collections import Counter



namespaces = {'owl': 'http://www.imsglobal.org/xsd/imsqti_result_v2p1'}
