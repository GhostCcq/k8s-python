#!/bin/env python
# -*- coding: utf-8 -*-

from typing import Optional
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from kubernetes import client, config
from kubernetes.client.rest import ApiException


app = FastAPI()


class Params(BaseModel):
    destination: Optional[str] = None
    virtualService: Optional[str] = None
    deployment: Optional[str] = None
    service: Optional[str] = None
    namespace: str
    configString: str
    content: Optional[dict] = None



@app.post("/applyService")    # 更新Service信息
def applyService(params: Params):
    namespace = params.namespace
    service = params.service
    content = params.content
    init_cluster(params.configString)   # 加载集群认证配置信息

    k8s_Core_v1 = client.CoreV1Api()
    # 先查询是否有对应资源，如果不存在做异常处理，进行创建。如果存在则进行更新
    try:
        ret = k8s_Core_v1.read_namespaced_service(name=service, namespace=namespace)
    except ApiException:
        try:
            ret = k8s_Core_v1.create_namespaced_service(body=content, namespace=namespace)
            return JSONResponse(content={'Code': 1000, 'Msg': f'{ret.metadata.name} Create succeed!!!'})
        except ApiException as e:
            return JSONResponse(content={'Code': 2999, 'Msg': e.body})
    else:
        ret = k8s_Core_v1.patch_namespaced_service(name=service, body=content, namespace=namespace)
        return JSONResponse(content={'Code': 1001, 'Msg': f'{ret.metadata.name} Update succeed!!!'})


@app.post("/applyDeployment")    # 更新Deployment信息
def applyDeployment(params: Params):
    namespace = params.namespace
    init_cluster(params.configString)   # 加载集群认证配置信息
    deployment = params.deployment
    content = params.content
    k8s_apps_v1 = client.AppsV1Api()
    try:
        ret = k8s_apps_v1.read_namespaced_deployment(name=deployment, namespace=namespace)
    except ApiException:
        try:
            ret = k8s_apps_v1.create_namespaced_deployment(body=content, namespace=namespace)
            return JSONResponse(content={'Code': 1000, 'Msg': f'{ret.metadata.name} Create succeed!!!'})
        except ApiException as e:
            return JSONResponse(content={'Code': 2999, 'Msg': e.body})
    else:
        ret = k8s_apps_v1.patch_namespaced_deployment(name=deployment, body=content, namespace=namespace)
        return JSONResponse(content={'Code': 1001, 'Msg': f'{ret.metadata.name} Update succeed!!!'})


@app.post("/applyVirtualService")    # 更新VirtualService信息
def applyVirtualService(params: Params):
    namespace = params.namespace
    init_cluster(params.configString)    # 加载集群认证配置信息
    virtualService = params.virtualService
    content = params.content
    v1 = client.CustomObjectsApi()
    # 先获取dr资源是否存在，如果不存在则进行create，如果存在则进行patch
    try:
        ret = v1.get_namespaced_custom_object(group="networking.istio.io", version="v1alpha3", plural="virtualservices", namespace=namespace, name=virtualService)   # 获取dr资源是否存在
    except ApiException:
        try:
            ret = v1.create_namespaced_custom_object(group="networking.istio.io", version="v1beta1", plural="virtualservices", namespace=namespace, body=content)

            return JSONResponse(content={'Code': 1000, 'Msg': 'Create succeed!!!', 'Ret': ret})
        except ApiException as e:
            return JSONResponse(content={'Code': 2999, 'Msg': e.body})
    else:
        try:
            ret = v1.patch_namespaced_custom_object(group="networking.istio.io", version="v1beta1", plural="virtualservices", name=virtualService, namespace=namespace, body=content)
            return JSONResponse(content={'Code': 1001, 'Msg': 'Update succeed!!!', 'Ret': ret})
        except ApiException as e:
            return JSONResponse(content={'Code': 2999, 'Msg': e.body})


@app.post("/applyDestinationRule")    # 更新DestinationRule信息
def applyDestinationRule(params: Params):
    namespace = params.namespace
    init_cluster(params.configString)   # 加载集群认证配置信息
    destination = params.destination
    content = params.content
    v1 = client.CustomObjectsApi()

    # 先获取dr资源是否存在，如果不存在则进行create，如果存在则进行patch
    try:
        ret = v1.get_namespaced_custom_object(group="networking.istio.io", version="v1alpha3", plural="destinationrules", namespace=namespace, name=destination)   # 获取dr资源是否存在
    except ApiException:
        try:
            ret = v1.create_namespaced_custom_object(group="networking.istio.io", version="v1beta1", plural="destinationrules", namespace=namespace, body=content)
            return JSONResponse(content={'Code': 1000, 'Msg': 'Create succeed!!!', 'Ret': ret})
        except ApiException as e:
            return JSONResponse(content={'Code': 2999, 'Msg': e.body})
    else:
        try:
            ret = v1.patch_namespaced_custom_object(group="networking.istio.io", version="v1beta1", plural="destinationrules", name=destination, namespace=namespace, body=content)
            return JSONResponse(content={'Code': 1001, 'Msg': 'Update succeed!!!', 'Ret': ret})

        except ApiException as e:
            return JSONResponse(content={'Code': 2999, 'Msg': e.body})


@app.post("/getVirtualService")    # 获取VirtualService信息
def getVirtualService(params: Params):
    init_cluster(params.configString)  # 加载集群认证配置信息
    namespace = params.namespace
    virtualService = params.virtualService

    v1 = client.CustomObjectsApi()
    try:
        if virtualService != None:
            ret = v1.get_namespaced_custom_object(group="networking.istio.io", version="v1alpha3", plural="virtualservices", namespace=namespace, name=virtualService)
        else:
            ret = v1.list_namespaced_custom_object(group="networking.istio.io", version="v1alpha3", plural="virtualservices", namespace=namespace)   # 如果没有指定资源名称，则输出获取到的全部资源列表

        return JSONResponse(content={'Code': 1002, 'Msg': ret})
    except ApiException as e:
        return JSONResponse(content={'Code': 2999, 'Msg': e.body})


@app.post("/getDestinationRule")    # 获取DestinationRule信息
def getDestinationRule(params: Params):
    init_cluster(params.configString)  # 加载集群认证配置信息

    namespace = params.namespace
    destination = params.destination
    v1 = client.CustomObjectsApi()

    try:
        if destination != None:
            ret = v1.get_namespaced_custom_object(group="networking.istio.io", version="v1alpha3", plural="destinationrules", namespace=namespace, name=destination)
        else:
            ret = v1.list_namespaced_custom_object(group="networking.istio.io", version="v1alpha3", plural="destinationrules", namespace=namespace)   # 如果没有指定资源名称，则输出获取到的全部资源列表
        return JSONResponse(content={'Code': 1002, 'Msg': ret})
    except ApiException as e:
        return JSONResponse(content={'Code': 2999, 'Msg': e.body})


@app.delete("/delDestinationRule")
def delDestinationRule(params: Params):
    init_cluster(params.configString)  # 加载集群认证配置信息
    namespace = params.namespace
    destination = params.destination
    v1 = client.CustomObjectsApi()

    try:
        ret = getDestinationRule(params)
        if ret.status_code == 200:
            res = v1.delete_namespaced_custom_object(group="networking.istio.io", version="v1alpha3", plural="destinationrules", namespace=namespace, name=destination)
            return JSONResponse(content={'Code': '1004', 'Msg': res})
    except ApiException as e:
        return JSONResponse(content={'Code': '2998', 'Msg': e.body})


@app.delete("/delVirtualService")
def delVirtualService(params: Params):
    init_cluster(params.configString)  # 加载集群认证配置信息
    namespace = params.namespace
    virtualService = params.virtualService
    v1 = client.CustomObjectsApi()

    try:
        ret = getVirtualService(params)
        if ret.status_code == 200:
            res = v1.delete_namespaced_custom_object(group="networking.istio.io", version="v1alpha3", plural="virtualservices", namespace=namespace, name=virtualService)
            return JSONResponse(content={'Code': '1004', 'Msg': res})
    except ApiException as e:
        return JSONResponse(content={'Code': '2998', 'Msg': e.body})

def init_cluster(configstring):
    with open('./kube_config', 'w+', encoding='utf-8') as f:
        f.write(configstring)
    config.load_kube_config('./kube_config')

