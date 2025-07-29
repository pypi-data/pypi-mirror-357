from nrp_k8s_utils import PodManager
from typing import Dict

import yaml
import tempfile
import os


class PytorchDDLController(PodManager):

    def __init__(
            self, 
            group_name: str,
            central_pvc_name: str,
            local_model_path: str,
            num_workers: int,
            base_container: Dict,
            spec_modifiers: Dict = {},
            pvc_mount_path: str = '/ddl_pvc_mount',  
            pvc_work_dir_path: str = 'ddl_pvc_work_dir',
            controller_port: int = 12345,
            debug_mode: bool = False
        ):

        self.group_name: str = group_name
        self.central_pvc_name: str = central_pvc_name
        self.num_workers: int = num_workers
        self.base_container: Dict = base_container
        self.spec_modifiers: Dict = spec_modifiers
        self.pvc_mount_path: str = pvc_mount_path
        self.pvc_work_dir_path: str = pvc_work_dir_path
        self.local_model_path: str = local_model_path

    
        self._validate_paths()

        self._build_support_manifest()
        super().__init__(
            manifest=self.support_manifest_path, 
            debug_mode=debug_mode,
        )

        self.service_address = f"{self.group_name}-svc"
        self.service_port_name = "ddp-svc-port"
        self.controller_port: int = controller_port  
        self._create_service_manifest()
        
        self._build_stateful_set_manifest()
 
# --------------------------------------------------------------------------------
# Service Methods
# --------------------------------------------------------------------------------

    def _create_service_manifest(self) -> None:
        service_manifest = {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {'name': self.service_address},
            'spec': {
                'clusterIP': 'None',
                'selector': {'app': self.group_name},
                'ports': [{
                        'name': self.service_port_name,
                        'port': self.controller_port,
                        'targetPort': self.controller_port
        }]}}

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as temp_file:
            yaml.dump(service_manifest, temp_file)
            self.service_manifest_path = temp_file.name
    
    def _create_service(self) -> None:
        super().run_kubectl_cmd(['create', '-f', self.service_manifest_path], verbose=False)  

    def _service_exists(self) -> bool:
        result = super().run_kubectl_cmd(
            ['get', 'service', self.service_address], 
            check=False, 
            verbose=False
        )
        return result.returncode == 0

    def _stop_service(self) -> None:
        super().run_kubectl_cmd(['delete', 'service', self.service_address], verbose=False)

#---------------------------------------------------------------------------------
# Support Pod Methods
# --------------------------------------------------------------------------------

    def _build_support_manifest(self) -> None:
        self.support_manifest = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'name': f"{self.group_name}-s"
            },
            'spec': {
                'containers': [{
                    'name': 'busybox',
                    'image': 'busybox',
                    'resources': {
                        'limits':{ 'cpu': '500m', 'memory': '128Mi'},
                        'requests': { 'cpu': '250m', 'memory': '64Mi'},
                    },
                    'volumeMounts': [{
                        'name': 'main',
                        'mountPath': self.pvc_mount_path,
                    }],
                    'command': ['sh', '-c', 'while true; do sleep 3600; done'],
                }],
                'volumes' : [{
                    'name': 'main',
                    'persistentVolumeClaim': {"claimName": self.central_pvc_name}
                }],
            }
        }
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as temp_file:
            yaml.dump(self.support_manifest, temp_file)
            self.support_manifest_path = temp_file.name

    def _start_support(self) -> None: 
        super().start_pod()

    def _stop_support(self) -> None:
        super().stop_pod()

    def _support_exists(self) -> bool:
        return super().run_kubectl_cmd(
            ['get', 'pod', f"{self.group_name}-a"],
            check=False,
            verbose=False
        ).returncode == 0

    def _transfer_model(self) -> None:
        super().run_container_cmd(
            ['mkdir', '-p', f'{self.pvc_work_dir_path}/model'],
            container_name='busybox',
            verbose=False
        )

        super().kubectl_copy(
            container_name='busybox',
            src_path=self.local_model_path,
            dest_path=self.pvc_work_dir_path
        )

    def _delete_model(self) -> None:
        super().run_container_cmd(
            ['rm', '-rf', f'{self.pvc_work_dir_path}/model'], 
            container_name='busybox',
            verbose=False
        )

#---------------------------------------------------------------------------------
# Worker Methods
# --------------------------------------------------------------------------------

    def _build_stateful_set_manifest(self) -> Dict:
        namespace = super().get_current_namespace()
        master_addr = f"{self.group_name}-0.{self.service_address}.{namespace}.svc.cluster.local"

        self.stateful_set_manifest = {
            'apiVersion': 'apps/v1',
            'kind': 'StatefulSet',
            'metadata': {'name': self.group_name},
            'spec': {
                'serviceName': self.service_address,
                'podManagementPolicy': 'Parallel',
                'replicas': self.num_workers,
                'selector': {
                    'matchLabels': {
                        'app': self.group_name
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {'app': self.group_name}
                    },
                    'spec': {
                        **self.spec_modifiers,
                        'containers': [{
                            **self.base_container,
                            'name': self.group_name,
                            'volumeMounts': [{
                                'name': 'main-volume',
                                'mountPath': self.pvc_mount_path,
                            }],
                            'env': [
                                {'name': 'GLOBAL_RANK', 'valueFrom': {'fieldRef': {'fieldPath': 'metadata.name'}}},
                                {'name': 'RDZV_ENDPOINT', 'value': f'{master_addr}:{self.controller_port}'},
                            ],
                            'ports': [{'containerPort': self.controller_port}]
                        }],
                        'volumes': [{
                            'name': 'main-volume',
                            'persistentVolumeClaim': {"claimName": self.central_pvc_name}
                        }]
                    }
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as temp_file:
            yaml.dump(self.stateful_set_manifest, temp_file)
            self.stateful_set_manifest_path = temp_file.name

    def _stateful_set_exists(self) -> bool:
        return super().run_kubectl_cmd(
            ['get', 'statefulset', f"{self.group_name}"],
            check=False,
            verbose=False
        ).returncode == 0

    def _start_stateful_set(self) -> None:
        super().run_kubectl_cmd(['create', '-f', self.stateful_set_manifest_path], verbose=False)

    def _stop_stateful_set(self) -> None:
        super().run_kubectl_cmd(['delete', 'statefulset', f"{self.group_name}"], verbose=False)

# --------------------------------------------------------------------------------
# Lifecycle Methods
# --------------------------------------------------------------------------------

    def _validate_paths(self) -> None:
        if self.pvc_mount_path[-1] == '/':
            self.pvc_mount_path = self.pvc_mount_path[:-1]
        if self.pvc_mount_path[0] != '/':
            raise ValueError('PVC mount path must start with /')
        self.pvc_mount_path: str = self.pvc_mount_path

        if self.pvc_work_dir_path[-1] == '/':
            self.pvc_work_dir_path = self.pvc_work_dir_path[:-1]
        if self.pvc_work_dir_path[0] == '/':
            self.pvc_work_dir_path = self.pvc_work_dir_path[1:]
        self.pvc_work_dir_path: str = f'{self.pvc_mount_path}/{self.pvc_work_dir_path}'

    def start_pod_group(self) -> None:
        if not self._support_exists():
            self._start_support()
        self._transfer_model()
        self._stop_support()

        if not self._service_exists():
            self._create_service()
        self._start_stateful_set()

    def stop_pod_group(self) -> None:
        if self._stateful_set_exists():
            self._stop_stateful_set()
        if self._service_exists():
            self._stop_service()
        self._start_support()
        self._delete_model()
        self._stop_support()

        os.remove(self.service_manifest_path)
        os.remove(self.stateful_set_manifest_path)
        os.remove(self.support_manifest_path)

# --------------------------------------------------------------------------------
# Logging Methods
# --------------------------------------------------------------------------------

    def ls_work_dir(self) -> None:
        super().run_container_cmd(
            command=['ls', '-a', self.pvc_work_dir_path], 
            container_name='busybox',
            verbose=False
        )


        
        
    