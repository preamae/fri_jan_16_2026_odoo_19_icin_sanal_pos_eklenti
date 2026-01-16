# -*- coding: utf-8 -*-

import requests
import json
import logging
from odoo import api, models, _
from odoo. exceptions import UserError

_logger = logging.getLogger(__name__)


class PhpGatewayService:
    """PHP Gateway ile iletişim servisi"""
    
    def __init__(self, env):
        self.env = env
        self. 