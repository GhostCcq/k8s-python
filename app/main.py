#!/bin/env python
# -*- coding: utf-8 -*-

from typing import Optional, Dict
from fastapi import FastAPI
from kubernetes import client, config
from kubernetes.client.rest import ApiException


app = FastAPI()


@app.post("/applyService")    # 更新Service信息
async def applyService(namespace: str, configString: str, content: Dict[str, list], service: Optional[str] = None):
    init_cluster(configString)   # 加载集群认证配置信息
    k8s_apps_v1 = client.CoreV1Api()
    # 先查询是否有对应资源，如果不存在做异常处理，进行创建。如果存在则进行更新
    try:
        ret = k8s_apps_v1.read_namespaced_service(name=service, namespace=namespace)
    except ApiException:
        try:
            ret = k8s_apps_v1.create_namespaced_service(body=content.get('content')[0], namespace=namespace)
            return {'Code': 1000, 'Msg': f'{ret.metadata.name} Create succeed!!!'}
        except ApiException as e:
            return {'Code': 2999, 'Msg': e}
    else:
        ret = k8s_apps_v1.patch_namespaced_service(name=service, body=content.get('content')[0], namespace=namespace)
        return {'Code': 1001, 'Msg': f'{ret.metadata.name} Update succeed!!!'}


@app.post("/applyDeployment")    # 更新Deployment信息
async def applyDeployment(namespace: str, configString: str, content: Dict[str, list], deployment: Optional[str] = None):
    init_cluster(configString)   # 加载集群认证配置信息
    k8s_apps_v1 = client.AppsV1Api()
    try:
        ret = k8s_apps_v1.read_namespaced_deployment(name=deployment, namespace=namespace)
    except ApiException:
        try:
            ret = k8s_apps_v1.create_namespaced_deployment(body=content.get('content')[0], namespace=namespace)
            return {'Code': 1000, 'Msg': f'{ret.metadata.name} Create succeed!!!'}
        except ApiException as e:
            return {'Code': 2999, 'Msg': e}
    else:
        ret = k8s_apps_v1.patch_namespaced_deployment(name=deployment, body=content.get('content')[0], namespace=namespace)
        return {'Code': 1001, 'Msg': f'{ret.metadata.name} Update succeed!!!'}


@app.post("/applyVirtualService")    # 更新VirtualService信息
async def applyVirtualService(namespace: str, configString: str, content: Dict[str, list], virtualService: Optional[str] = None):
    init_cluster(configString)   # 加载集群认证配置信息
    v1 = client.CustomObjectsApi()
    # 先获取dr资源是否存在，如果不存在则进行create，如果存在则进行patch
    try:
        ret = v1.get_namespaced_custom_object(group="networking.istio.io", version="v1alpha3", plural="virtualservices", namespace=namespace, name=virtualService)   # 获取dr资源是否存在
    except ApiException:
        try:
            ret = v1.create_namespaced_custom_object(group="networking.istio.io", version="v1beta1", plural="virtualservices", namespace=namespace, body=content.get('content')[0])
            return{'Code': 1000, 'Msg': 'Create succeed!!!', 'Ret': ret}
        except ApiException as e:
            return {'Code': 2999, 'Msg': e}
    else:
        try:
            ret = v1.patch_namespaced_custom_object(group="networking.istio.io", version="v1beta1", plural="virtualservices", name=virtualService, namespace=namespace, body=content.get('content')[0])
            return {'Code': 1001, 'Msg': 'Update succeed!!!', 'Ret': ret}
        except ApiException as e:
            return {'Code': 2999, 'Msg': e}


@app.post("/applyDestinationRule")    # 更新DestinationRule信息
async def applyDestinationRule(namespace: str, configString: str, content: Dict[str, list], destination: Optional[str] = None):
    init_cluster(configString)   # 加载集群认证配置信息
    v1 = client.CustomObjectsApi()
    # 先获取dr资源是否存在，如果不存在则进行create，如果存在则进行patch
    try:
        ret = v1.get_namespaced_custom_object(group="networking.istio.io", version="v1alpha3", plural="destinationrules", namespace=namespace, name=destination)   # 获取dr资源是否存在
    except ApiException:
        try:
            ret = v1.create_namespaced_custom_object(group="networking.istio.io", version="v1beta1", plural="destinationrules", namespace=namespace, body=content.get('content')[0])
            return{'Code': 1000, 'Msg': 'Create succeed!!!', 'Ret': ret}
        except ApiException as e:
            return {'Code': 2999, 'Msg': e}
    else:
        try:
            ret = v1.patch_namespaced_custom_object(group="networking.istio.io", version="v1beta1", plural="destinationrules", name=destination, namespace=namespace, body=content.get('content')[0])
            return {'Code': 1001, 'Msg': 'Update succeed!!!', 'Ret': ret}

        except ApiException as e:
            return {'Code': 2999, 'Msg': e}


@app.get("/getVirtualService")    # 获取VirtualService信息
async def getVirtualService(namespace: str, configString: str, virtualService: Optional[str] = None):
    init_cluster(configString)   # 加载集群认证配置信息
    v1 = client.CustomObjectsApi()
    try:
        if virtualService != None:
            ret = v1.get_namespaced_custom_object(group="networking.istio.io", version="v1alpha3", plural="virtualservices", namespace=namespace, name=virtualService)
        else:
            ret = v1.list_namespaced_custom_object(group="networking.istio.io", version="v1alpha3", plural="virtualservices", namespace=namespace)   # 如果没有指定资源名称，则输出获取到的全部资源列表

        return {'Code': 1002, 'Msg': ret}
    except ApiException as e:
        return {'Code': 2999, 'Msg': e}


@app.get("/getDestinationRule")    # 获取DestinationRule信息
async def getDestinationRule(namespace: str, configString: str, destination: Optional[str] = None):
    init_cluster(configString)   # 加载集群认证配置信息
    v1 = client.CustomObjectsApi()
    try:
        if destination != None:
            ret = v1.get_namespaced_custom_object(group="networking.istio.io", version="v1alpha3", plural="destinationrules", namespace=namespace, name=destination)
        else:
            ret = v1.list_namespaced_custom_object(group="networking.istio.io", version="v1alpha3", plural="destinationrules", namespace=namespace)   # 如果没有指定资源名称，则输出获取到的全部资源列表
        return {'Code': 1002, 'Msg': ret}
    except ApiException as e:
        return {'Code': 2999, 'Msg': e}


def init_cluster(configstring):
    with open('./kube_config', 'w+', encoding='utf-8') as f:
        f.write(configstring)
    try:
        config.load_kube_config('./kube_config')
    except ApiException as e:
        print(e)

