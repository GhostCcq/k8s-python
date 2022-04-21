#!/bin/env python
# -*- coding: utf-8 -*-


from kubernetes import client, config
from kubernetes.client.rest import ApiException


config.load_kube_config('./kube_config')
k8s_apps_v1 = client.CustomObjectsApi()


ret = k8s_apps_v1.delete_namespaced_custom_object(group="networking.istio.io", version="v1beta1", plural="virtualservices", namespace='test', name='business-hs-user-web-test')

print(ret.get('status'))