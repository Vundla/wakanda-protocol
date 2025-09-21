# Wakanda Protocol

A comprehensive microservices platform for AI-powered knowledge management, financial services, mineral analysis, and drone operations.

## Architecture

```
wakanda-protocol/
├─ services/
│  ├─ knowledge_hub/  (FastAPI + OpenRouter)
│  ├─ finance/        (FastAPI + Mastercard integration)
│  ├─ minerals/       (predictor model service)
│  └─ drones/         (simulation + telemetry ingestion)
├─ infra/
│  ├─ docker/         (Docker Compose setup)
│  ├─ k8s/            (Kubernetes manifests)
│  └─ terraform/      (AWS infrastructure)
└─ scripts/
   └─ deploy.py       (Deployment automation)
```

## Services

### 🧠 Knowledge Hub Service
- **Port**: 8001
- **Technology**: FastAPI + OpenRouter
- **Features**: AI-powered knowledge management and retrieval
- **Endpoints**: 
  - `POST /query` - Query knowledge base using AI
  - `POST /knowledge` - Add knowledge items
  - `GET /knowledge` - List knowledge items

### 💰 Finance Service
- **Port**: 8002
- **Technology**: FastAPI + Mastercard API
- **Features**: Payment processing and financial services
- **Endpoints**:
  - `POST /payments` - Process payments
  - `GET /transactions` - List transactions
  - `GET /accounts/{id}/balance` - Check account balance

### ⛏️ Minerals Service
- **Port**: 8003
- **Technology**: FastAPI + Machine Learning
- **Features**: Mineral analysis and prediction
- **Endpoints**:
  - `POST /predict` - Predict mineral types and extraction feasibility
  - `POST /analyze-batch` - Batch analysis from CSV
  - `GET /models` - List available ML models

### 🚁 Drones Service
- **Port**: 8004
- **Technology**: FastAPI + WebSockets
- **Features**: Drone fleet management and simulation
- **Endpoints**:
  - `POST /drones` - Register drones
  - `POST /missions` - Create missions
  - `POST /simulations` - Start simulations
  - `WS /ws/telemetry/{id}` - Real-time telemetry

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- kubectl (for Kubernetes deployment)
- Terraform (for AWS deployment)

### 1. Check Prerequisites
```bash
python3 scripts/deploy.py check
```

### 2. Install Dependencies
```bash
python3 scripts/deploy.py install
```

### 3. Build & Deploy (Docker Compose)
```bash
python3 scripts/deploy.py all
```

### 4. Access Services
- **API Gateway**: http://localhost/
- **Knowledge Hub**: http://localhost:8001/
- **Finance**: http://localhost:8002/
- **Minerals**: http://localhost:8003/
- **Drones**: http://localhost:8004/
- **Grafana**: http://localhost:3000/ (admin/admin)
- **Prometheus**: http://localhost:9090/

## Configuration

### Environment Variables
Create `.env` file in `infra/docker/`:
```bash
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
```

## Deployment Options

### Docker Compose (Development)
```bash
cd infra/docker
docker-compose up -d
```

### Kubernetes (Production)
```bash
# Apply Kubernetes manifests
kubectl apply -f infra/k8s/

# Or use deploy script
python3 scripts/deploy.py deploy-k8s
```

### AWS (Cloud Infrastructure)
```bash
cd infra/terraform
terraform init
terraform plan
terraform apply

# Or use deploy script
python3 scripts/deploy.py deploy-terraform
```

## API Examples

### Knowledge Hub
```bash
# Query the AI knowledge base
curl -X POST "http://localhost:8001/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the best practices for mineral extraction?"}'

# Add knowledge item
curl -X POST "http://localhost:8001/knowledge" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "item1",
    "title": "Mining Safety Guidelines",
    "content": "Safety protocols for mining operations...",
    "category": "safety",
    "tags": ["mining", "safety", "guidelines"]
  }'
```

### Finance
```bash
# Process payment
curl -X POST "http://localhost:8002/payments" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100.00,
    "currency": "USD",
    "card_number": "4111111111111111",
    "expiry_month": 12,
    "expiry_year": 2025,
    "cvv": "123",
    "merchant_id": "merchant123"
  }'
```

### Minerals
```bash
# Predict mineral type
curl -X POST "http://localhost:8003/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "samples": [{
      "sample_id": "sample1",
      "location": {"lat": 40.7128, "lon": -74.0060},
      "depth_meters": 50.0,
      "soil_ph": 7.2,
      "moisture_content": 25.5,
      "temperature_celsius": 18.0,
      "elemental_composition": {"Fe": 45.2, "Cu": 12.8, "Au": 0.05}
    }],
    "prediction_type": "mineral_type"
  }'
```

### Drones
```bash
# Register drone
curl -X POST "http://localhost:8004/drones" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Survey Drone 1",
    "model": "DJI Phantom 4",
    "specs": {
      "max_altitude_m": 500,
      "max_speed_ms": 20,
      "battery_capacity_mah": 5870,
      "payload_capacity_kg": 2.0,
      "camera_resolution": "4K",
      "sensors": ["GPS", "IMU", "Barometer", "Camera"]
    },
    "location": {"lat": 40.7128, "lon": -74.0060, "altitude": 0}
  }'

# Start simulation
curl -X POST "http://localhost:8004/simulations" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mining Survey Simulation",
    "duration_minutes": 30,
    "drone_ids": ["drone-id-here"],
    "scenario_type": "training"
  }'
```

## Monitoring

### Prometheus Metrics
- Service health endpoints: `/health`
- Custom metrics for each service
- Infrastructure monitoring

### Grafana Dashboards
- Service performance dashboards
- Infrastructure monitoring
- Business metrics

## Development

### Running Individual Services
```bash
# Knowledge Hub
cd services/knowledge_hub
pip install -r requirements.txt
python main.py

# Finance
cd services/finance
pip install -r requirements.txt
python main.py

# Minerals
cd services/minerals
pip install -r requirements.txt
python main.py

# Drones
cd services/drones
pip install -r requirements.txt
python main.py
```

### Testing
```bash
# Test all services
python3 scripts/deploy.py test

# Run individual service tests (if available)
cd services/knowledge_hub
python -m pytest tests/
```

## Security

- API rate limiting via NGINX
- OAuth 2.0 for external integrations
- TLS encryption for production deployments
- Kubernetes RBAC for access control
- AWS IAM roles for cloud resources

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in each service directory
- Review the deployment logs for troubleshooting