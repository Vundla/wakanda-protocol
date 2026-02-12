#!/usr/bin/env python3
"""
Wakanda Protocol Deployment Script
Automates deployment of all services and infrastructure components.
"""

import os
import sys
import subprocess
import argparse
import json
import time
from pathlib import Path
from typing import Dict, List, Optional

class Colors:
    """ANSI color codes for terminal output"""
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_info(message: str):
    print(f"{Colors.BLUE}ℹ {message}{Colors.ENDC}")

def print_success(message: str):
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.ENDC}")

def print_error(message: str):
    print(f"{Colors.RED}✗ {message}{Colors.ENDC}")

def run_command(command: List[str], cwd: Optional[str] = None, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result"""
    print_info(f"Running: {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {e}")
        if e.stderr:
            print_error(f"Error output: {e.stderr}")
        if check:
            sys.exit(1)
        return e

class WakandaDeployer:
    """Main deployment orchestrator"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.services_dir = project_root / "services"
        self.infra_dir = project_root / "infra"
        
    def check_prerequisites(self) -> bool:
        """Check if required tools are installed"""
        print_info("Checking prerequisites...")
        
        required_tools = {
            "docker": ["docker", "--version"],
            "docker-compose": ["docker-compose", "--version"],
            "kubectl": ["kubectl", "version", "--client"],
            "terraform": ["terraform", "--version"],
            "python": ["python3", "--version"],
            "pip": ["pip3", "--version"]
        }
        
        missing_tools = []
        
        for tool, command in required_tools.items():
            try:
                result = run_command(command, check=False)
                if result.returncode == 0:
                    print_success(f"{tool} is available")
                else:
                    missing_tools.append(tool)
                    print_error(f"{tool} is not available")
            except FileNotFoundError:
                missing_tools.append(tool)
                print_error(f"{tool} is not installed")
        
        if missing_tools:
            print_error(f"Missing required tools: {', '.join(missing_tools)}")
            return False
        
        print_success("All prerequisites are satisfied")
        return True
    
    def install_dependencies(self):
        """Install Python dependencies for all services"""
        print_info("Installing Python dependencies...")
        
        services = ["knowledge_hub", "finance", "minerals", "drones"]
        
        for service in services:
            service_dir = self.services_dir / service
            requirements_file = service_dir / "requirements.txt"
            
            if requirements_file.exists():
                print_info(f"Installing dependencies for {service}")
                run_command([
                    "pip3", "install", "-r", str(requirements_file)
                ])
                print_success(f"Dependencies installed for {service}")
            else:
                print_warning(f"No requirements.txt found for {service}")
    
    def test_services(self):
        """Run basic tests on services"""
        print_info("Running service tests...")
        
        services = [
            ("knowledge_hub", 8001),
            ("finance", 8002),
            ("minerals", 8003),
            ("drones", 8004)
        ]
        
        for service, port in services:
            service_dir = self.services_dir / service
            main_file = service_dir / "main.py"
            
            if main_file.exists():
                print_info(f"Testing {service} service")
                # Basic syntax check
                result = run_command([
                    "python3", "-m", "py_compile", str(main_file)
                ], check=False)
                
                if result.returncode == 0:
                    print_success(f"{service} syntax check passed")
                else:
                    print_error(f"{service} syntax check failed")
            else:
                print_warning(f"No main.py found for {service}")
    
    def build_docker_images(self):
        """Build Docker images for all services"""
        print_info("Building Docker images...")
        
        services = ["knowledge_hub", "finance", "minerals", "drones"]
        
        for service in services:
            service_dir = self.services_dir / service
            dockerfile = service_dir / "Dockerfile"
            
            if dockerfile.exists():
                print_info(f"Building Docker image for {service}")
                run_command([
                    "docker", "build", "-t", f"wakanda/{service}:latest", "."
                ], cwd=str(service_dir))
                print_success(f"Docker image built for {service}")
            else:
                print_warning(f"No Dockerfile found for {service}")
    
    def deploy_with_docker_compose(self):
        """Deploy using Docker Compose"""
        print_info("Deploying with Docker Compose...")
        
        docker_compose_file = self.infra_dir / "docker" / "docker-compose.yml"
        
        if docker_compose_file.exists():
            # Check if .env file exists
            env_file = docker_compose_file.parent / ".env"
            if not env_file.exists():
                print_warning("No .env file found, creating template...")
                self._create_env_template(env_file)
            
            print_info("Starting services with Docker Compose...")
            run_command([
                "docker-compose", "-f", str(docker_compose_file), "up", "-d"
            ])
            print_success("Services deployed with Docker Compose")
            
            # Wait a moment for services to start
            time.sleep(10)
            
            # Check service health
            self._check_service_health()
            
        else:
            print_error("Docker Compose file not found")
    
    def deploy_terraform_infrastructure(self):
        """Deploy infrastructure using Terraform"""
        print_info("Deploying infrastructure with Terraform...")
        
        terraform_dir = self.infra_dir / "terraform"
        
        if terraform_dir.exists():
            # Initialize Terraform
            print_info("Initializing Terraform...")
            run_command(["terraform", "init"], cwd=str(terraform_dir))
            
            # Plan deployment
            print_info("Planning Terraform deployment...")
            run_command(["terraform", "plan"], cwd=str(terraform_dir))
            
            # Ask for confirmation
            response = input(f"{Colors.YELLOW}Do you want to apply the Terraform configuration? (y/N): {Colors.ENDC}")
            if response.lower() == 'y':
                print_info("Applying Terraform configuration...")
                run_command(["terraform", "apply", "-auto-approve"], cwd=str(terraform_dir))
                print_success("Infrastructure deployed with Terraform")
            else:
                print_info("Terraform deployment skipped")
        else:
            print_error("Terraform directory not found")
    
    def deploy_to_kubernetes(self):
        """Deploy to Kubernetes"""
        print_info("Deploying to Kubernetes...")
        
        k8s_dir = self.infra_dir / "k8s"
        
        if k8s_dir.exists():
            # Apply Kubernetes manifests
            for manifest_file in k8s_dir.glob("*.yaml"):
                print_info(f"Applying {manifest_file.name}")
                run_command(["kubectl", "apply", "-f", str(manifest_file)])
            
            print_success("Kubernetes manifests applied")
            
            # Wait for deployments to be ready
            print_info("Waiting for deployments to be ready...")
            run_command([
                "kubectl", "wait", "--for=condition=available", 
                "--timeout=300s", "deployment", "--all", 
                "-n", "wakanda-protocol"
            ], check=False)
            
        else:
            print_error("Kubernetes directory not found")
    
    def _create_env_template(self, env_file: Path):
        """Create environment file template"""
        env_content = """# Wakanda Protocol Environment Variables
# Copy this file to .env and fill in the actual values

# OpenRouter API Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Mastercard API Configuration
MASTERCARD_API_URL=https://sandbox.api.mastercard.com
MASTERCARD_CONSUMER_KEY=your_mastercard_consumer_key_here
MASTERCARD_PRIVATE_KEY=your_mastercard_private_key_here

# Database Configuration
POSTGRES_PASSWORD=secure_password_change_me

# Monitoring Configuration
GRAFANA_PASSWORD=admin_password_change_me
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print_success(f"Environment template created at {env_file}")
        print_warning("Please edit the .env file with your actual API keys and passwords")
    
    def _check_service_health(self):
        """Check if services are healthy"""
        print_info("Checking service health...")
        
        services = [
            ("Knowledge Hub", "http://localhost:8001/"),
            ("Finance", "http://localhost:8002/"),
            ("Minerals", "http://localhost:8003/"),
            ("Drones", "http://localhost:8004/"),
            ("API Gateway", "http://localhost/")
        ]
        
        for service_name, url in services:
            try:
                import requests
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print_success(f"{service_name} is healthy")
                else:
                    print_warning(f"{service_name} returned status {response.status_code}")
            except ImportError:
                print_warning("requests library not available, skipping health checks")
                break
            except Exception as e:
                print_warning(f"{service_name} health check failed: {e}")
    
    def show_status(self):
        """Show deployment status"""
        print_info("Deployment Status:")
        print()
        
        # Docker containers
        print_info("Docker Containers:")
        result = run_command(["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"], check=False)
        print()
        
        # Kubernetes pods (if available)
        print_info("Kubernetes Pods:")
        result = run_command([
            "kubectl", "get", "pods", "-n", "wakanda-protocol", 
            "--no-headers"
        ], check=False)
        if result.returncode != 0:
            print("Kubernetes not available or no wakanda-protocol namespace found")
        print()
        
        # Service endpoints
        print_info("Service Endpoints:")
        endpoints = [
            "Knowledge Hub: http://localhost:8001/",
            "Finance: http://localhost:8002/",
            "Minerals: http://localhost:8003/",
            "Drones: http://localhost:8004/",
            "API Gateway: http://localhost/",
            "Grafana: http://localhost:3000/ (admin/admin)",
            "Prometheus: http://localhost:9090/"
        ]
        
        for endpoint in endpoints:
            print(f"  • {endpoint}")
        print()

def main():
    parser = argparse.ArgumentParser(description="Wakanda Protocol Deployment Script")
    parser.add_argument(
        "action",
        choices=["check", "install", "test", "build", "deploy", "deploy-k8s", "deploy-terraform", "status", "all"],
        help="Action to perform"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Project root directory"
    )
    
    args = parser.parse_args()
    
    deployer = WakandaDeployer(args.project_root)
    
    print(f"{Colors.BOLD}Wakanda Protocol Deployment Script{Colors.ENDC}")
    print(f"Project root: {args.project_root}")
    print()
    
    if args.action == "check":
        if not deployer.check_prerequisites():
            sys.exit(1)
    elif args.action == "install":
        deployer.install_dependencies()
    elif args.action == "test":
        deployer.test_services()
    elif args.action == "build":
        deployer.build_docker_images()
    elif args.action == "deploy":
        deployer.deploy_with_docker_compose()
    elif args.action == "deploy-k8s":
        deployer.deploy_to_kubernetes()
    elif args.action == "deploy-terraform":
        deployer.deploy_terraform_infrastructure()
    elif args.action == "status":
        deployer.show_status()
    elif args.action == "all":
        if not deployer.check_prerequisites():
            sys.exit(1)
        deployer.install_dependencies()
        deployer.test_services()
        deployer.build_docker_images()
        deployer.deploy_with_docker_compose()
        deployer.show_status()
    
    print_success("Deployment script completed!")

if __name__ == "__main__":
    main()