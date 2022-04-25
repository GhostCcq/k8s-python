#!/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

f = open('./app/kube_config', mode='r', encoding='utf-8')

public_data = {
    "namespace": "test",
    "configString": f.read(),
}

app_destination_data = {
    "destination": "business-hs-user-web-test",
    "virtualService": "business-hs-user-web-test",
    "content": {
        "apiVersion": "networking.istio.io/v1beta1",
        "kind": "VirtualService",
        "metadata": {
            "name": "business-hs-user-web-test",
            "namespace": "test"
        },
        "spec": {
            "hosts": [
                "business-hs-user-web"
            ],
            "http": [
                {
                    "match": [
                        {
                            "headers": {
                                "istio-v": {}
                            }
                        }
                    ],
                    "route": [
                        {
                            "destination": {
                                "host": "business-hs-user-web-test",
                                "subset": "blue"
                            }
                        }
                    ]
                },
                {
                    "route": [
                        {
                            "destination": {
                                "host": "business-hs-user-web",
                                "subset": "green"
                            }
                        }
                    ]
                }
            ]
        }
    }
}




data = {**app_destination_data, **public_data}



res = requests.post(url='http://127.0.0.1:8000/applyVirtualService', data=json.dumps(data))
print(res.text)