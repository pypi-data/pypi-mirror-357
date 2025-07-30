# -*- coding: utf-8 -*-
"""
---------------------------------------------
Copyright (c) 2025 ZhangYundi
Licensed under the MIT License. 
Created on 2025/6/24 22:07
Email: yundi.xxii@outlook.com
Description: 
---------------------------------------------
"""

from .loader import DataLoader
from .updater import DataUpdater, submit, do

__version__ = "0.1.1"

__all__ = [
    "DataLoader",
    "DataUpdater",
    "submit",
    "do"
]