import pytest
import tempfile
import os
import sys
import socket
import time
import subprocess
import random
import string

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from nrp_k8s_utils.jupyter_pod import JupyterPod

@pytest.fixture(scope="module")
def test_manifest():
    """Fixture that provides a test manifest."""
    return {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": "test-jupyter-pod"
        },
        "spec": {
            "containers": [
                {
                    "name": "jupyter",
                    "image": "jupyter/datascience-notebook:latest",
                    "ports": [{
                        "containerPort": 8888
                    }],
                    "resources": {
                        "requests": {
                            "memory": "2Gi",
                            "cpu": "1"
                        },
                        "limits": {
                            "memory": "4Gi",
                            "cpu": "2"
                        }
                    },
                    "command": [
                        "start-notebook.sh",
                        "--NotebookApp.token=''",
                        "--NotebookApp.password=''",
                        "--port=8888"
                    ]
                }
            ],
            "volumes": [
                {
                    "name": "data",
                    "persistentVolumeClaim": {
                        "claimName": "mdsmlvol"
                    }
                }
            ],
            "restartPolicy": "Never"
        }
    }

@pytest.fixture(scope="module")
def jupyter_pod(test_manifest):
    """Fixture that provides a running Jupyter pod instance."""
    pod = JupyterPod(
        volume="mdsmlvol",
        image="jupyter/datascience-notebook:latest",
        local_port=8888,
        remote_port=8888,
        context=None,
        debug_mode=True
    )
    try:
        pod.start_notebook()
        print("JUPYTER POD START PASS")
        yield pod
    finally:
        try:
            print("\nCleaning up Jupyter pod...")
            pod.stop_notebook()
            print("JUPYTER POD STOP PASS")
        except Exception as e:
            print(f"Error during Jupyter pod cleanup: {e}")

def assert_pod_running(pod):
    """Helper function to verify pod is running."""
    status = pod.get_pod_status()
    assert status == "Running", f"Pod is not running. Current status: {status}"
    print(f"Verified pod is running (status: {status})")

def test_pod_creation_and_configuration(jupyter_pod):
    """Test pod creation and configuration."""
    assert_pod_running(jupyter_pod)
    assert jupyter_pod.name.startswith("jupyter-notebook-")
    assert jupyter_pod.volume == "mdsmlvol"
    assert jupyter_pod.image == "jupyter/datascience-notebook:latest"
    assert jupyter_pod.local_port == 8888
    assert jupyter_pod.remote_port == 8888
    print("POD CONFIGURATION PASS")

def test_port_forwarding(jupyter_pod):
    """Test port forwarding functionality."""
    assert_pod_running(jupyter_pod)
    port = jupyter_pod.local_port
    host = 'localhost'
    max_retries = 10
    retry_delay = 1

    for attempt in range(max_retries):
        print(f"Checking if port {port} is active (Attempt {attempt + 1}/{max_retries})...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        try:
            result = sock.connect_ex((host, port))
            if result == 0:
                print(f"PORT FORWARD PASS: Port {port} is active and ready.")
                break
            print(f"Port {port} is not active yet. Error code: {result}")
        except Exception as e:
            print(f"Error checking port {port}: {e}")
        finally:
            sock.close()
        
        if attempt == max_retries - 1:
            raise RuntimeError(f"Port {port} is not active after {max_retries} retries.")
        time.sleep(retry_delay)

def test_jupyter_http_connection(jupyter_pod):
    """Test HTTP connection to Jupyter notebook."""
    assert_pod_running(jupyter_pod)
    port = jupyter_pod.local_port
    
    # Use curl to check if Jupyter is responding
    curl_command = f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:{port}"
    result = subprocess.run(curl_command, shell=True, text=True, capture_output=True)
    
    print(f"Curl output: {result.stdout.strip()}")
    print(f"Curl error: {result.stderr.strip()}")
    
    # Jupyter should return a 200 status code
    assert result.stdout.strip() == "200", f"Jupyter HTTP connection failed: {result.stderr}"
    print("JUPYTER HTTP CONNECTION PASS")

def test_volume_mount(jupyter_pod):
    """Test volume mounting functionality."""
    assert_pod_running(jupyter_pod)
    
    # Create a test file in the mounted volume
    test_content = "test content"
    test_file = "/mnt/test_file.txt"
    
    # Write to the mounted volume
    jupyter_pod.run_container_cmd(
        command=["bash", "-c", f"echo '{test_content}' > {test_file}"],
        container_name="jupyter"
    )
    
    # Verify the file was created
    ls_output = jupyter_pod.run_container_cmd(
        command=["ls", "-l", "/mnt"],
        container_name="jupyter"
    )
    assert "test_file.txt" in ls_output
    print("FILE CREATION PASS")
    
    # Verify the content
    cat_output = jupyter_pod.run_container_cmd(
        command=["cat", test_file],
        container_name="jupyter"
    )
    assert cat_output.strip() == test_content
    print("FILE CONTENT VERIFICATION PASS")
    
    # Clean up
    jupyter_pod.run_container_cmd(
        command=["rm", "-f", test_file],
        container_name="jupyter"
    )

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
