import os

import pytest_bdd

import custom_yaml

from fixtures import *
from steps.givens import *
from steps.whens import *
from steps.thens import *

pytest_bdd.scenarios('features/insert_data.feature')
