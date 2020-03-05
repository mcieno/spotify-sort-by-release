# -*- coding: utf8 -*-
import requests


s = requests.Session()


def init(oauth):
    s.headers.update({
        'Authorization': f"Bearer {oauth}",
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    })
