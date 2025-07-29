import logging
import subprocess
import time
import socket

from typing import List, Union

class PortForwardProcessManager():
    """
    Manage port forwarding processes for Kubernetes pods.
    """

    def __init__(
            self,
            local_port: Union[List[int], int], 
            pod_port: int,
            pod_name: str,
            namespace: str,
            context: str,
            logger: logging.Logger = None):
        
        if isinstance(local_port, int):
            self.local_port = [local_port]
        else:
            self.local_port = local_port
        
        self.logger = logger
        self.pod_port = pod_port
        self.pod_name = pod_name

        self.namespace = namespace
        self.context = context

        self.port_forward_process = None


    def attempt_port_forwarding(self) -> bool:
            """
            Attempt to set up port forwarding using a list of candidate local_port.
            :return: True if port forwarding starts successfully, False otherwise.
            """

            self.logger.debug(f"Attempting to set up port forwarding for pod {self.pod_name} using local_port: {self.local_port}")
            for port in self.local_port:
                if self._port_forward(local_port=port, pod_port=self.pod_port):
                    self.local_port = port 
                    self.logger.debug(f"Port forwarding established on local port {port}")
                    return True
            self.logger.error("Failed to establish port forwarding on any of the candidate local_port.")
            return False

    def _port_forward(self, local_port: int, pod_port: int) -> bool:
        """
        Set up port forwarding from a pod's container to the local machine.
        :param local_port: Local machine port to forward traffic to.
        :param pod_port: Port in the pod to forward traffic from.
        :return: True if port forwarding starts successfully, False otherwise.
        """
        self.logger.debug(
            f"Setting up port forwarding from local port {local_port} to pod {self.pod_name} on port {pod_port}"
        )
        try:
            self.port_forward_process = subprocess.Popen(
                [
                    "kubectl",
                    "--context", self.context,
                    "--namespace", self.namespace,
                    "port-forward", self.pod_name,
                    f"{local_port}:{pod_port}"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            for _ in range(10):
                if self._is_port_active(local_port):
                    self.logger.debug(f"Port forwarding is active and ready on port {local_port}.")
                    return True
                time.sleep(1) 

            self.logger.error(f"Port forwarding process started, but port {local_port} is not active.")
            self.port_forward_process.terminate()
            self.port_forward_process = None
            return False

        except Exception as e:
            self.logger.error(f"Failed to set up port forwarding: {e}")
            self.port_forward_process = None
            return False

    def _is_port_active(self, port: int) -> bool:
        """
        Check if a local port is active and listening.

        :param port: Port number to check.
        :return: True if the port is active, False otherwise.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            return result == 0

    def stop_port_forward(self):
        """
        Terminate the port-forwarding process.
        """
        if self.port_forward_process:
            self.logger.debug("Terminating port forwarding process.")
            self.port_forward_process.terminate()
            self.port_forward_process = None
        else:
            self.logger.warning("No active port-forwarding process to terminate.")
