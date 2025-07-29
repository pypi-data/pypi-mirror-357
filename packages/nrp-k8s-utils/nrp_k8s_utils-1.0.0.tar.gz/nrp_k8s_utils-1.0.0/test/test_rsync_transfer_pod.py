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

from nrp_k8s_utils.rsync_transfer_pod import RsyncTransferPod

@pytest.fixture(scope="module")
def test_manifest():
    """Fixture that provides a test manifest."""
    return {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": "test-rsync-pod"
        },
        "spec": {
            "containers": [
                {
                    "name": "main",
                    "image": "ubuntu:22.04",
                    "command": ["sleep", "infinity"]
                }
            ],
            "volumes": [
                {
                    "name": "main",
                    "persistentVolumeClaim": {
                        "claimName": "mdsmlvol"
                    }
                }
            ],
            "restartPolicy": "Never"
        }
    }

@pytest.fixture(scope="module")
def random_content():
    """Generate random content for test file."""
    size = random.randint(1024, 10240)
    return ''.join(random.choices(string.ascii_letters + string.digits, k=size))

@pytest.fixture(scope="module")
def rsync_pod(test_manifest):
    """Fixture that provides a running rsync pod instance."""
    pod = RsyncTransferPod(
        manifest=test_manifest,
        volume="main",
        ssh_port=2222
    )
    try:
        pod.start_pod()
        print("RSYNC POD START PASS")
        yield pod
    finally:
        try:
            print("\nCleaning up rsync pod...")
            pod.stop_pod()
            print("RSYNC POD STOP PASS")
        except Exception as e:
            print(f"Error during rsync pod cleanup: {e}")

def assert_pod_running(pod):
    """Helper function to verify pod is running."""
    status = pod.get_pod_status()
    assert status == "Running", f"Pod is not running. Current status: {status}"
    print(f"Verified pod is running (status: {status})")

def test_pod_creation_and_key_generation(rsync_pod):
    """Test pod creation and SSH key generation."""
    assert_pod_running(rsync_pod)
    assert rsync_pod.name.startswith("test-rsync-pod")
    assert rsync_pod.volume == "main"
    assert rsync_pod.ssh_port == 2222
    assert rsync_pod.private_key is not None
    assert rsync_pod.public_key is not None
    assert rsync_pod.private_key_path is not None
    print("POD CREATION AND KEY GENERATION PASS")

def test_port_forwarding(rsync_pod):
    """Test port forwarding functionality."""
    assert_pod_running(rsync_pod)
    port = rsync_pod.ssh_port
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

def test_ssh_connection(rsync_pod):
    """Test SSH connection to the rsync sidecar."""
    assert_pod_running(rsync_pod)
    
    # Get the SSH command
    ssh_command = rsync_pod.print_ssh_command()
    
    # Test SSH connection
    test_command = f"{ssh_command} 'echo hello'"
    result = subprocess.run(test_command, shell=True, capture_output=True, text=True)
    
    assert result.returncode == 0, f"SSH connection failed: {result.stderr}"
    assert "hello" in result.stdout, "SSH command did not return expected output"
    print("SSH CONNECTION PASS")

def test_file_transfer(rsync_pod, random_content):
    """Test file transfer functionality."""
    assert_pod_running(rsync_pod)
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
        temp_file_path = temp_file.name
        temp_file.write(random_content)
        print(f"Created temporary file: {temp_file_path} with size {len(random_content)} bytes")
    
    try:
        remote_path = "/data/test_transfer.txt"
        rsync_pod.transfer_files(src_path=temp_file_path, dest_path=remote_path)
        print("FILE TRANSFER PASS")
        
        assert_pod_running(rsync_pod)
        cat_output = rsync_pod.run_container_cmd(
            command=["cat", remote_path],
            container_name="rsync-sidecar",
        )
        
        assert cat_output == random_content, "File content mismatch after transfer"
        print("FILE VERIFICATION PASS")
        
        # Clean up test file
        rsync_pod.run_container_cmd(
            command=["rm", "-f", remote_path],
            container_name="rsync-sidecar"
        )
    finally:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
            print(f"Cleaned up temporary file: {temp_file_path}")

def test_directory_transfer(rsync_pod, random_content):
    """Test directory transfer functionality."""
    assert_pod_running(rsync_pod)
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create multiple files
        for i in range(3):
            with open(os.path.join(temp_dir, f"test_{i}.txt"), 'w') as f:
                f.write(random_content)
        
        # Transfer directory
        rsync_pod.transfer_files(src_path=temp_dir + '/', dest_path="/data/test_dir")
        
        # Verify directory contents
        ls_output = rsync_pod.run_container_cmd(
            command=["ls", "-1", "/data/test_dir"],
            container_name="rsync-sidecar"
        )
        files = ls_output.splitlines()
        assert len(files) == 3
        
        # Verify content of each file
        for i in range(3):
            content = rsync_pod.run_container_cmd(
                command=["cat", f"/data/test_dir/test_{i}.txt"],
                container_name="rsync-sidecar"
            )
            assert content == random_content

        # Clean up test directory
        rsync_pod.run_container_cmd(
            command=["rm", "-rf", "/data/test_dir"],
            container_name="rsync-sidecar"
        )

@pytest.mark.slow
def test_large_file_transfer(rsync_pod):
    """Test transfer of a large file (100MB)."""
    assert_pod_running(rsync_pod)
    # Create a 100MB file with random content
    size_mb = 100
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as temp_file:
        temp_file.write(os.urandom(size_mb * 1024 * 1024))
        temp_file_path = temp_file.name
    
    try:
        # Transfer large file
        rsync_pod.transfer_files(
            src_path=temp_file_path,
            dest_path="/data/large_file_test"
        )
        
        # Verify file size using Linux stat command
        size_check = rsync_pod.run_container_cmd(
            command=["stat", "--format=%s", "/data/large_file_test"],
            container_name="rsync-sidecar"
        )
        assert int(size_check) == size_mb * 1024 * 1024

        # Clean up large file
        rsync_pod.run_container_cmd(
            command=["rm", "-f", "/data/large_file_test"],
            container_name="rsync-sidecar"
        )
    finally:
        os.unlink(temp_file_path)

if __name__ == '__main__':
    pytest.main([__file__, '-v']) 