#!/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

f = open('./app/kube_config', mode='r', encoding='utf-8')

public_data = {
    "namespace": "test",
    "configString": f.read(),
}

app_virtualService_data = {
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

app_destination_data = {
    "destination": "business-hs-user-web-test",
    "content": {
        "apiVersion": "networking.istio.io/v1beta1",
        "kind": "DestinationRule",
        "metadata": {
            "name": "business-hs-user-web-test",
            "namespace": "test"
        },
        "spec": {
            "host": "business-hs-user-web",
            "subsets": [
                {
                    "labels": {
                        "version": "green"
                    },
                    "name": "green"
                },
                {
                    "labels": {
                        "version": "blue"
                    },
                    "name": "blue"
                }
            ],
            "trafficPolicy": {
                "loadBalancer": {
                    "simple": "RANDOM"
                }
            }
        }
    }
}


app_deployment_data = {
    "deployment": "business-hs-user-web-test",
    "content": {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "labels": {
                "app": "business-hs-user-web-test",
                "sidecar.jaegertracing.io/injected": "simplest",
                "tier": "backend"
            },
            "name": "business-hs-user-web-test",
            "namespace": "test"
        },
        "spec": {
            "minReadySeconds": 20,
            "progressDeadlineSeconds": 600,
            "replicas": 1,
            "revisionHistoryLimit": 10,
            "selector": {
                "matchLabels": {
                    "app": "business-hs-user-web-test",
                    "tier": "backend"
                }
            },
            "strategy": {
                "rollingUpdate": {
                    "maxSurge": "25%",
                    "maxUnavailable": 0
                },
                "type": "RollingUpdate"
            },
            "template": {
                "metadata": {
                    "labels": {
                        "app": "business-hs-user-web-test",
                        "istio.io/rev": "1-10-3",
                        "tier": "backend"
                    }
                },
                "spec": {
                    "containers": [
                        {
                            "env": [
                                {
                                    "name": "LANG",
                                    "value": "en_US.UTF-8"
                                },
                                {
                                    "name": "TZ",
                                    "value": "Asia/Shanghai"
                                },
                                {
                                    "name": "JAVA_OPTS",
                                    "value": "-Xms2048m -Xmx2048m"
                                },
                                {
                                    "name": "ENV",
                                    "value": "k8s"
                                },
                                {
                                    "name": "app.id",
                                    "value": "business-hs-user-web"
                                },
                                {
                                    "name": "spring.application.name",
                                    "value": "business-hs-user-web"
                                },
                                {
                                    "name": "management.metrics.export.statsd.host",
                                    "value": "tm-ts-telegraf"
                                },
                                {
                                    "name": "management.endpoint.health.show-details",
                                    "value": "always"
                                },
                                {
                                    "name": "qmq.app-code",
                                    "value": "business-hs-user-web"
                                },
                                {
                                    "name": "server.shutdown",
                                    "value": "graceful"
                                },
                                {
                                    "name": "spring.lifecycle.timeout-per-shutdown-phase",
                                    "value": "10s"
                                },
                                {
                                    "name": "spring.profiles.active",
                                    "value": "k8s"
                                },
                                {
                                    "name": "aliyun_logs_prod-log-stdout",
                                    "value": "stdout"
                                },
                                {
                                    "name": "traffic.group",
                                    "value": "blue"
                                },
                                {
                                    "name": "SW_AGENT_NAME",
                                    "value": "business-hs-user-web"
                                },
                                {
                                    "name": "MY_NODE_IP",
                                    "valueFrom": {
                                        "fieldRef": {
                                            "apiVersion": "v1",
                                            "fieldPath": "status.hostIP"
                                        }
                                    }
                                },
                                {
                                    "name": "JAEGER_SERVICE_NAME",
                                    "value": "business-hs-user-web.test"
                                },
                                {
                                    "name": "JAEGER_PROPAGATION",
                                    "value": "jaeger,b3,w3c"
                                }
                            ],
                            "envFrom": [
                                {
                                    "configMapRef": {
                                        "name": "hs-config"
                                    }
                                },
                                {
                                    "secretRef": {
                                        "name": "hs-secret"
                                    }
                                }
                            ],
                            "image": "hs-pro-image.tencentcloudcr.com/zeus/business-hs-user-web:k8s-beta-15c98974-74060",
                            "imagePullPolicy": "Always",
                            "lifecycle": {
                                "preStop": {
                                    "exec": {
                                        "command": [
                                            "/bin/sh",
                                            "-c",
                                            "sleep 30"
                                        ]
                                    }
                                }
                            },
                            "livenessProbe": {
                                "failureThreshold": 10,
                                "httpGet": {
                                    "path": "/actuator/health",
                                    "port": 9905,
                                    "scheme": "HTTP"
                                },
                                "initialDelaySeconds": 20,
                                "periodSeconds": 10,
                                "successThreshold": 1,
                                "timeoutSeconds": 10
                            },
                            "name": "business-hs-user-web",
                            "ports": [
                                {
                                    "containerPort": 9905,
                                    "name": "default",
                                    "protocol": "TCP"
                                }
                            ],
                            "readinessProbe": {
                                "failureThreshold": 10,
                                "httpGet": {
                                    "path": "/actuator/health",
                                    "port": 9905,
                                    "scheme": "HTTP"
                                },
                                "initialDelaySeconds": 20,
                                "periodSeconds": 10,
                                "successThreshold": 1,
                                "timeoutSeconds": 3
                            },
                            "resources": {},
                            "startupProbe": {
                                "failureThreshold": 40,
                                "httpGet": {
                                    "path": "/actuator/health",
                                    "port": 9905,
                                    "scheme": "HTTP"
                                },
                                "initialDelaySeconds": 35,
                                "periodSeconds": 10,
                                "successThreshold": 1,
                                "timeoutSeconds": 3
                            },
                            "terminationMessagePath": "/dev/termination-log",
                            "terminationMessagePolicy": "File",
                            "volumeMounts": [
                                {
                                    "mountPath": "/data/logs",
                                    "name": "logs"
                                }
                            ]
                        }
                    ],
                    "dnsPolicy": "ClusterFirst",
                    "hostAliases": [
                        {
                            "hostnames": [
                                "hsxt-test-01"
                            ],
                            "ip": "172.31.120.7"
                        }
                    ],
                    "imagePullSecrets": [
                        {
                            "name": "tcr-secret"
                        }
                    ],
                    "nodeSelector": {
                        "test": "test"
                    },
                    "restartPolicy": "Always",
                    "schedulerName": "default-scheduler",
                    "securityContext": {},
                    "terminationGracePeriodSeconds": 60,
                    "volumes": [
                        {
                            "hostPath": {
                                "path": "/data/logs/business-hs-user-web",
                                "type": "DirectoryOrCreate"
                            },
                            "name": "logs"
                        }
                    ]
                }
            }
        }
    }
}

app_service_data = {
    "service": "business-hs-user-web-test",
    "content": {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "labels": {
                "app": "business-hs-user-web",
                "tier": "backend"
            },
            "name": "business-hs-user-web-test",
            "namespace": "test"
        },
        "spec": {
            "ports": [
                {
                    "name": "default",
                    "port": 9905,
                    "protocol": "TCP",
                    "targetPort": 9905
                }
            ],
            "selector": {
                "app": "business-hs-user-web",
                "tier": "backend"
            },
            "sessionAffinity": "None",
            "type": "ClusterIP"
        }
    }
}

get_destination_data = {
    "destination": "business-hs-user-web"
}

get_virtualService_data = {
    "virtualService": "business-hs-user-web"
}

data = {**app_virtualService_data, **public_data}

print(json.dumps(data), '\n')


res = requests.post(url='http://127.0.0.1:8000/applyVirtualService', data=json.dumps(data))
print(res.text)