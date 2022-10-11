#!/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import tempfile
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from pydantic import BaseModel

app = FastAPI()


class Params(BaseModel):
    hpa: Optional[str] = None
    destination: Optional[str] = None
    virtualService: Optional[str] = None
    deployment: Optional[str] = None
    service: Optional[str] = None
    replicas: Optional[int] = None
    labelSelector: Optional[str] = None
    namespace: str
    configString: str
    content: Optional[dict] = None


@app.post("/applyhpa")  # 更新hpa信息
def applyhpa(params: Params):
    namespace = params.namespace
    hpa = params.hpa
    content = params.content

    config_file = init_cluster(params.configString)  # 加载集群认证配置信息

    v1 = client.CustomObjectsApi()
    # 先获取dr资源是否存在，如果不存在则进行create，如果存在则进行patch
    try:
        v1.get_namespaced_custom_object(group="autoscaling", version="v2beta2", plural="horizontalpodautoscalers",
                                        namespace=namespace, name=hpa)
    except ApiException:
        try:
            ret = v1.create_namespaced_custom_object(group="autoscaling", version="v2beta2",
                                                     plural="horizontalpodautoscalers", namespace=namespace, body=content)

            return JSONResponse(content={'code': 1000, 'msg': 'Create succeed!!!',
                                         'data': ret if isinstance(ret, dict) else json.loads(ret)})
        except ApiException as e:
            return JSONResponse(content={'code': 2999, 'msg': json.loads(e.body)})
    else:
        try:
            ret = v1.patch_namespaced_custom_object(group="autoscaling", version="v2beta2",
                                                    plural="horizontalpodautoscalers", name=hpa, namespace=namespace,
                                                    body=content)
            return JSONResponse(content={'code': 1001, 'msg': 'Update succeed!!!',
                                         'data': ret if isinstance(ret, dict) else json.loads(ret)})
        except ApiException as e:
            return JSONResponse(content={'code': 2999, 'msg': json.loads(e.body)})
    finally:
        os.remove(config_file)


@app.post("/applyService")  # 更新Service信息
def applyService(params: Params):
    namespace = params.namespace
    service = params.service
    content = params.content

    config_file = init_cluster(params.configString)  # 加载集群认证配置信息

    k8s_core_v1 = client.CoreV1Api()
    # 先查询是否有对应资源，如果不存在做异常处理，进行创建。如果存在则进行更新
    try:
        k8s_core_v1.read_namespaced_service(name=service, namespace=namespace)
    except ApiException:
        try:
            ret = k8s_core_v1.create_namespaced_service(body=content, namespace=namespace)
            return JSONResponse(content={'code': 1000, 'msg': f'{ret.metadata.name} Create succeed!!!'})
        except ApiException as e:
            return JSONResponse(content={'code': 2999, 'msg': json.loads(e.body.decode("UTF-8"))})
    else:
        ret = k8s_core_v1.patch_namespaced_service(name=service, body=content, namespace=namespace)
        return JSONResponse(content={'code': 1001, 'msg': f'{ret.metadata.name} Update succeed!!!'})
    finally:
        os.remove(config_file)


@app.post("/applyDeployment")  # 更新Deployment信息
def applyDeployment(params: Params):
    namespace = params.namespace
    deployment = params.deployment
    content = params.content

    config_file = init_cluster(params.configString)  # 加载集群认证配置信息

    k8s_apps_v1 = client.AppsV1Api()
    try:
        k8s_apps_v1.read_namespaced_deployment(name=deployment, namespace=namespace)
    except ApiException:
        try:
            ret = k8s_apps_v1.create_namespaced_deployment(body=content, namespace=namespace)
            return JSONResponse(content={'code': 1000, 'msg': f'{ret.metadata.name} Create succeed!!!'})
        except ApiException as e:
            return JSONResponse(content={'code': 2999, 'msg': json.loads(e.body)})
    else:
        ret = k8s_apps_v1.patch_namespaced_deployment(name=deployment, body=content, namespace=namespace)
        return JSONResponse(content={'code': 1001, 'msg': f'{ret.metadata.name} Update succeed!!!'})
    finally:
        os.remove(config_file)


@app.post("/applyVirtualService")  # 更新VirtualService信息
def applyVirtualService(params: Params):
    namespace = params.namespace
    virtual_service = params.virtualService
    content = params.content

    config_file = init_cluster(params.configString)  # 加载集群认证配置信息

    v1 = client.CustomObjectsApi()
    # 先获取dr资源是否存在，如果不存在则进行create，如果存在则进行patch
    try:
        v1.get_namespaced_custom_object(group="networking.istio.io", version="v1alpha3", plural="virtualservices",
                                        namespace=namespace, name=virtual_service)
    except ApiException:
        try:
            ret = v1.create_namespaced_custom_object(group="networking.istio.io", version="v1beta1",
                                                     plural="virtualservices", namespace=namespace, body=content)

            return JSONResponse(content={'code': 1000, 'msg': 'Create succeed!!!',
                                         'data': ret if isinstance(ret, dict) else json.loads(ret)})
        except ApiException as e:
            return JSONResponse(content={'code': 2999, 'msg': json.loads(e.body)})
    else:
        try:
            ret = v1.patch_namespaced_custom_object(group="networking.istio.io", version="v1beta1",
                                                    plural="virtualservices", name=virtual_service, namespace=namespace,
                                                    body=content)
            return JSONResponse(content={'code': 1001, 'msg': 'Update succeed!!!',
                                         'data': ret if isinstance(ret, dict) else json.loads(ret)})
        except ApiException as e:
            return JSONResponse(content={'code': 2999, 'msg': json.loads(e.body)})
    finally:
        os.remove(config_file)


@app.post("/applyDestinationRule")  # 更新DestinationRule信息
def applyDestinationRule(params: Params):
    namespace = params.namespace
    destination = params.destination
    content = params.content

    config_file = init_cluster(params.configString)  # 加载集群认证配置信息

    v1 = client.CustomObjectsApi()
    # 先获取dr资源是否存在，如果不存在则进行create，如果存在则进行patch
    try:
        v1.get_namespaced_custom_object(group="networking.istio.io", version="v1alpha3",
                                        plural="destinationrules", namespace=namespace,
                                        name=destination)  # 获取dr资源是否存在
    except ApiException:
        try:
            ret = v1.create_namespaced_custom_object(group="networking.istio.io", version="v1beta1",
                                                     plural="destinationrules", namespace=namespace, body=content)
            return JSONResponse(content={'code': 1000, 'msg': 'Create succeed!!!',
                                         'data': ret if isinstance(ret, dict) else json.loads(ret)})
        except ApiException as e:
            return JSONResponse(content={'code': 2999, 'msg': json.loads(e.body)})
    else:
        try:
            ret = v1.patch_namespaced_custom_object(group="networking.istio.io", version="v1beta1",
                                                    plural="destinationrules", name=destination, namespace=namespace,
                                                    body=content)
            return JSONResponse(content={'code': 1001, 'msg': 'Update succeed!!!',
                                         'data': ret if isinstance(ret, dict) else json.loads(ret)})
        except ApiException as e:
            return JSONResponse(content={'code': 2999, 'msg': json.loads(e.body)})
    finally:
        os.remove(config_file)


@app.post("/getVirtualService")  # 获取VirtualService信息
def getVirtualService(params: Params):
    namespace = params.namespace
    virtual_service = params.virtualService

    config_file = init_cluster(params.configString)  # 加载集群认证配置信息

    v1 = client.CustomObjectsApi()
    try:
        if virtual_service is not None:
            ret = v1.get_namespaced_custom_object(group="networking.istio.io", version="v1alpha3",
                                                  plural="virtualservices", namespace=namespace, name=virtual_service)
        else:
            ret = v1.list_namespaced_custom_object(group="networking.istio.io", version="v1alpha3",
                                                   plural="virtualservices",
                                                   namespace=namespace)  # 如果没有指定资源名称，则输出获取到的全部资源列表

        return JSONResponse(content={'code': 1002, 'msg': ret if isinstance(ret, dict) else json.loads(ret)})
    except ApiException as e:
        return JSONResponse(content={'code': 2999, 'msg': json.loads(e.body)})
    finally:
        os.remove(config_file)


@app.post("/getDestinationRule")  # 获取DestinationRule信息
def getDestinationRule(params: Params):
    namespace = params.namespace
    destination = params.destination

    config_file = init_cluster(params.configString)  # 加载集群认证配置信息

    v1 = client.CustomObjectsApi()
    try:
        if destination is not None:
            ret = v1.get_namespaced_custom_object(group="networking.istio.io", version="v1alpha3",
                                                  plural="destinationrules", namespace=namespace, name=destination)
        else:
            ret = v1.list_namespaced_custom_object(group="networking.istio.io", version="v1alpha3",
                                                   plural="destinationrules",
                                                   namespace=namespace)  # 如果没有指定资源名称，则输出获取到的全部资源列表
        return JSONResponse(content={'code': 1002, 'msg': ret if isinstance(ret, dict) else json.loads(ret)})
    except ApiException as e:
        return JSONResponse(content={'code': 2999, 'msg': json.loads(e.body)})
    finally:
        os.remove(config_file)


@app.post("/getDeployment")  # 获取Deployment信息
def getDeployment(params: Params):
    namespace = params.namespace
    deployment = params.deployment

    config_file = init_cluster(params.configString)  # 加载集群认证配置信息

    k8s_apps_v1 = client.AppsV1Api()
    try:
        ret = k8s_apps_v1.read_namespaced_deployment(name=deployment, namespace=namespace,
                                                     _preload_content=False).read()

        return JSONResponse(content={'code': 1002, 'msg': ret if isinstance(ret, dict) else json.loads(ret)})
    except ApiException as e:
        return JSONResponse(content={'code': 2999, 'msg': json.loads(e.body)})
    finally:
        os.remove(config_file)


@app.post("/getService")  # 获取Service信息
def getService(params: Params):
    namespace = params.namespace
    service = params.service

    config_file = init_cluster(params.configString)  # 加载集群认证配置信息

    k8s_core_v1 = client.CoreV1Api()
    try:
        ret = k8s_core_v1.read_namespaced_service(name=service, namespace=namespace, _preload_content=False).read()

        return JSONResponse(content={'code': 1002, 'msg': ret if isinstance(ret, dict) else json.loads(ret)})
    except ApiException as e:
        return JSONResponse(content={'code': 2999, 'msg': json.loads(e.body)})
    finally:
        os.remove(config_file)


@app.post("/getPods")
def getPods(params: Params):
    namespace = params.namespace
    # deployment = params.deployment
    label_selector = params.labelSelector

    config_file = init_cluster(params.configString)  # 加载集群认证配置信息

    core_v1 = client.CoreV1Api()
    try:
        ret = core_v1.list_namespaced_pod(namespace=namespace, label_selector=label_selector, watch=False,
                                          _preload_content=False).read()
        return JSONResponse(content={'code': 1002, 'msg': ret if isinstance(ret, dict) else json.loads(ret)})
    except ApiException as e:
        return JSONResponse(content={'code': 2999, 'msg': json.loads(e.body)})
    finally:
        os.remove(config_file)


@app.post("/getNameSpaces")
def getNameSpaces(params: Params):
    config_file = init_cluster(params.configString)  # 加载集群认证配置信息

    core_v1 = client.CoreV1Api()

    try:
        res = core_v1.list_namespace(_preload_content=False).read()

        return JSONResponse(content={'code': 0, 'msg': '', 'data': res if isinstance(res, dict) else json.loads(res)})
    except ApiException as e:
        return JSONResponse(content={'code': 1000, 'msg': json.loads(e.body), 'data': None})
    finally:
        os.remove(config_file)


@app.post("/getNameSpace")
def getNameSpace(params: Params):
    namespace, configString = params

    conf_file = init_cluster(configString)  # 加载集群认证配置信息

    core_v1 = client.CoreV1Api()

    try:
        res = core_v1.read_namespace(name=namespace, _preload_content=False).read()

        return JSONResponse(content={'code': 0, 'msg': '', 'data': res if isinstance(res, dict) else json.loads(res)})
    except ApiException as e:
        return JSONResponse(content={'code': 1000, 'msg': json.loads(e.body), 'data': None})
    finally:
        os.remove(conf_file)


@app.delete("/delhpa")
def delhpa(params: Params):
    namespace = params.namespace
    hpa = params.hpa

    config_file = init_cluster(params.configString)  # 加载集群认证配置信息

    v1 = client.CustomObjectsApi()
    try:
        ret = getDestinationRule(params)
        if ret.status_code == 200:
            res = v1.delete_namespaced_custom_object(group="autoscaling", version="v2beta2",
                                                     plural="horizontalpodautoscalers", namespace=namespace, name=hpa)
            return JSONResponse(content={'code': 1004, 'msg': res if isinstance(res, dict) else json.loads(res)})
    except ApiException as e:
        return JSONResponse(content={'code': 2998, 'msg': json.loads(e.body)})
    finally:
        os.remove(config_file)


@app.delete("/delDestinationRule")
def delDestinationRule(params: Params):
    namespace = params.namespace
    destination = params.destination

    config_file = init_cluster(params.configString)  # 加载集群认证配置信息

    v1 = client.CustomObjectsApi()
    try:
        ret = getDestinationRule(params)
        if ret.status_code == 200:
            res = v1.delete_namespaced_custom_object(group="networking.istio.io", version="v1alpha3",
                                                     plural="destinationrules", namespace=namespace, name=destination)
            return JSONResponse(content={'code': 1004, 'msg': res if isinstance(res, dict) else json.loads(res)})
    except ApiException as e:
        return JSONResponse(content={'code': 2998, 'msg': json.loads(e.body)})
    finally:
        os.remove(config_file)


@app.delete("/delVirtualService")
def delVirtualService(params: Params):
    namespace = params.namespace
    virtual_service = params.virtualService

    config_file = init_cluster(params.configString)  # 加载集群认证配置信息

    v1 = client.CustomObjectsApi()
    try:
        ret = getVirtualService(params)
        if ret.status_code == 200:
            res = v1.delete_namespaced_custom_object(group="networking.istio.io", version="v1alpha3",
                                                     plural="virtualservices", namespace=namespace,
                                                     name=virtual_service)
            return JSONResponse(content={'code': 1004, 'msg': json.loads(res)})
    except ApiException as e:
        return JSONResponse(content={'code': 2998, 'msg': json.loads(e.body)})
    finally:
        os.remove(config_file)


@app.delete("/delDeployment")
def delDeployment(params: Params):
    namespace = params.namespace
    deployment = params.deployment

    config_file = init_cluster(params.configString)  # 加载集群认证配置信息

    k8s_apps_v1 = client.AppsV1Api()
    if deployment is None:
        return JSONResponse(content={'code': 2404, 'msg': 'DeploymentName is None'})
    try:
        # ret = getDeployment(params)
        # if ret.status_code == 200:
        res = k8s_apps_v1.delete_namespaced_deployment(name=deployment, namespace=namespace)
        if res.status != 'Success':  # 不知道为什么在容器中res.status拿到的值都是None
            return JSONResponse(content={'code': 1004, 'msg': 'Success'})
        else:
            return JSONResponse(content={'code': 1004, 'msg': res.status})
    except ApiException as e:
        return JSONResponse(content={'code': 2998, 'msg': json.loads(e.body)})
    finally:
        os.remove(config_file)


@app.delete("/delService")
def delService(params: Params):
    namespace = params.namespace
    service = params.service

    config_file = init_cluster(params.configString)  # 加载集群认证配置信息

    k8s_core_v1 = client.CoreV1Api()
    if service is None:
        return JSONResponse(content={'code': 2404, 'msg': 'ServiceName is None'})
    try:
        # ret = getService(params)
        # if ret.status_code == 200:
        res = k8s_core_v1.delete_namespaced_service(name=service, namespace=namespace)
        if res.status != 'Success':  # 不知道为什么在容器中res.status拿到的值都是None
            return JSONResponse(content={'code': 1004, 'msg': 'Success'})
        else:
            return JSONResponse(content={'code': 1004, 'msg': res.status})
    except ApiException as e:
        return JSONResponse(content={'code': 2998, 'msg': json.loads(e.body)})
    finally:
        os.remove(config_file)


@app.post("/modifyDeployment")
def modifyDeployment(params: Params):
    replicas_body = {'spec': {'replicas': params.replicas}}
    namespace = params.namespace
    deployment = params.deployment

    config_file = init_cluster(params.configString)  # 加载集群认证配置信息

    k8s_apps_v1 = client.AppsV1Api()
    try:
        ret = k8s_apps_v1.patch_namespaced_deployment_scale(name=deployment, namespace=namespace, body=replicas_body)
        return JSONResponse(content={'code': 1001, 'msg': 'Modify succeed!!!',
                                     'data': {'name': deployment, 'replicas': ret.spec.replicas}})
    except ApiException as e:
        return JSONResponse(content={'code': 2998, 'msg': json.loads(e.body)})
    finally:
        os.remove(config_file)


def init_cluster(configstring):
    config_file = create_temp_file(configstring)
    config.load_kube_config(config_file=config_file)

    return config_file


def create_temp_file(content=""):
    handler, name = tempfile.mkstemp()

    os.write(handler, str.encode(content))
    os.close(handler)

    return name
