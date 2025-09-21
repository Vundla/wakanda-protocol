"""
Drones Service - Simulation + Telemetry Ingestion
Manages drone fleet operations, simulations, and telemetry data processing.
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import logging
import random
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Drones Service",
    description="Drone fleet management, simulation, and telemetry processing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class DroneSpecs(BaseModel):
    max_altitude_m: float = Field(..., gt=0)
    max_speed_ms: float = Field(..., gt=0)
    battery_capacity_mah: int = Field(..., gt=0)
    payload_capacity_kg: float = Field(..., ge=0)
    camera_resolution: str
    sensors: List[str]

class Drone(BaseModel):
    drone_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    model: str
    specs: DroneSpecs
    status: str = Field(default="offline", description="offline, standby, active, maintenance")
    current_mission_id: Optional[str] = None
    location: Dict[str, float] = Field(default_factory=dict)  # lat, lon, altitude
    battery_level: float = Field(default=100.0, ge=0, le=100)
    last_seen: datetime = Field(default_factory=datetime.now)

class Mission(BaseModel):
    mission_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    mission_type: str = Field(..., description="survey, delivery, inspection, emergency")
    assigned_drone_ids: List[str]
    waypoints: List[Dict[str, float]]  # List of lat, lon, altitude coordinates
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str = Field(default="planned", description="planned, active, completed, failed")
    priority: int = Field(default=1, ge=1, le=5)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TelemetryData(BaseModel):
    drone_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    location: Dict[str, float]  # lat, lon, altitude
    velocity: Dict[str, float]  # x, y, z components in m/s
    orientation: Dict[str, float]  # roll, pitch, yaw in degrees
    battery_level: float = Field(..., ge=0, le=100)
    signal_strength: float = Field(..., ge=-100, le=0)  # dBm
    temperature_c: float
    sensor_data: Dict[str, Any] = Field(default_factory=dict)

class FlightPlan(BaseModel):
    drone_id: str
    waypoints: List[Dict[str, float]]
    estimated_duration_minutes: float
    max_altitude_m: float
    speed_ms: float = Field(default=10.0)

class SimulationConfig(BaseModel):
    simulation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    duration_minutes: float = Field(..., gt=0)
    drone_ids: List[str]
    scenario_type: str = Field(..., description="training, mission_rehearsal, emergency_response")
    environment: Dict[str, Any] = Field(default_factory=dict)  # weather, obstacles, etc.
    real_time_factor: float = Field(default=1.0, gt=0)  # 1.0 = real-time, 2.0 = 2x speed

# Global data stores (in production, these would be databases)
drones_store = {}
missions_store = {}
telemetry_store = {}
simulations_store = {}
active_websockets = {}

# Drone simulation class
class DroneSimulator:
    def __init__(self):
        self.running_simulations = {}
    
    async def start_simulation(self, config: SimulationConfig):
        """Start a drone simulation"""
        if config.simulation_id in self.running_simulations:
            raise HTTPException(status_code=400, detail="Simulation already running")
        
        # Validate drones exist
        for drone_id in config.drone_ids:
            if drone_id not in drones_store:
                raise HTTPException(status_code=404, detail=f"Drone {drone_id} not found")
        
        # Create simulation state
        sim_state = {
            "config": config,
            "start_time": datetime.now(),
            "status": "running",
            "drone_states": {}
        }
        
        # Initialize drone states
        for drone_id in config.drone_ids:
            drone = drones_store[drone_id]
            sim_state["drone_states"][drone_id] = {
                "location": drone.location.copy(),
                "battery": drone.battery_level,
                "velocity": {"x": 0, "y": 0, "z": 0},
                "orientation": {"roll": 0, "pitch": 0, "yaw": 0}
            }
        
        self.running_simulations[config.simulation_id] = sim_state
        
        # Start simulation loop
        asyncio.create_task(self._simulation_loop(config.simulation_id))
        
        return config.simulation_id
    
    async def _simulation_loop(self, simulation_id: str):
        """Main simulation loop"""
        try:
            sim_state = self.running_simulations[simulation_id]
            config = sim_state["config"]
            
            start_time = sim_state["start_time"]
            duration = timedelta(minutes=config.duration_minutes)
            
            while datetime.now() < start_time + duration:
                if simulation_id not in self.running_simulations:
                    break  # Simulation was stopped
                
                # Update drone states
                for drone_id in config.drone_ids:
                    await self._update_drone_state(simulation_id, drone_id)
                
                # Send telemetry updates via WebSocket
                await self._broadcast_telemetry(simulation_id)
                
                # Sleep based on real-time factor
                await asyncio.sleep(1.0 / config.real_time_factor)
            
            # Mark simulation as completed
            if simulation_id in self.running_simulations:
                self.running_simulations[simulation_id]["status"] = "completed"
                
        except Exception as e:
            logger.error(f"Simulation {simulation_id} failed: {e}")
            if simulation_id in self.running_simulations:
                self.running_simulations[simulation_id]["status"] = "failed"
    
    async def _update_drone_state(self, simulation_id: str, drone_id: str):
        """Update drone state in simulation"""
        sim_state = self.running_simulations[simulation_id]
        drone_state = sim_state["drone_states"][drone_id]
        
        # Simulate movement (simplified)
        drone_state["location"]["lat"] += random.uniform(-0.001, 0.001)
        drone_state["location"]["lon"] += random.uniform(-0.001, 0.001)
        drone_state["location"]["altitude"] = max(0, drone_state["location"].get("altitude", 100) + random.uniform(-5, 5))
        
        # Simulate battery drain
        drone_state["battery"] = max(0, drone_state["battery"] - 0.1)
        
        # Update velocity and orientation
        drone_state["velocity"] = {
            "x": random.uniform(-10, 10),
            "y": random.uniform(-10, 10),
            "z": random.uniform(-2, 2)
        }
        
        drone_state["orientation"] = {
            "roll": random.uniform(-10, 10),
            "pitch": random.uniform(-10, 10),
            "yaw": random.uniform(0, 360)
        }
        
        # Create telemetry data
        telemetry = TelemetryData(
            drone_id=drone_id,
            location=drone_state["location"],
            velocity=drone_state["velocity"],
            orientation=drone_state["orientation"],
            battery_level=drone_state["battery"],
            signal_strength=random.uniform(-80, -20),
            temperature_c=random.uniform(15, 35),
            sensor_data={
                "gps_satellites": random.randint(4, 12),
                "magnetic_heading": random.uniform(0, 360),
                "barometric_pressure": random.uniform(1000, 1020)
            }
        )
        
        # Store telemetry
        if drone_id not in telemetry_store:
            telemetry_store[drone_id] = []
        telemetry_store[drone_id].append(telemetry.dict())
    
    async def _broadcast_telemetry(self, simulation_id: str):
        """Broadcast telemetry data via WebSocket"""
        if simulation_id in active_websockets:
            sim_state = self.running_simulations[simulation_id]
            
            for drone_id, drone_state in sim_state["drone_states"].items():
                telemetry_data = {
                    "type": "telemetry",
                    "simulation_id": simulation_id,
                    "drone_id": drone_id,
                    "data": drone_state,
                    "timestamp": datetime.now().isoformat()
                }
                
                websocket = active_websockets[simulation_id]
                try:
                    await websocket.send_text(json.dumps(telemetry_data))
                except:
                    # WebSocket disconnected
                    del active_websockets[simulation_id]
                    break

# Global simulator instance
simulator = DroneSimulator()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"service": "Drones Service", "status": "healthy", "version": "1.0.0"}

@app.post("/drones", response_model=Drone)
async def register_drone(drone: Drone):
    """Register a new drone"""
    if drone.drone_id in drones_store:
        raise HTTPException(status_code=400, detail="Drone already exists")
    
    drones_store[drone.drone_id] = drone
    return drone

@app.get("/drones", response_model=List[Drone])
async def list_drones(status: Optional[str] = None):
    """List all drones, optionally filtered by status"""
    drones = list(drones_store.values())
    if status:
        drones = [d for d in drones if d.status == status]
    return drones

@app.get("/drones/{drone_id}", response_model=Drone)
async def get_drone(drone_id: str):
    """Get specific drone information"""
    if drone_id not in drones_store:
        raise HTTPException(status_code=404, detail="Drone not found")
    return drones_store[drone_id]

@app.put("/drones/{drone_id}/status")
async def update_drone_status(drone_id: str, status: str):
    """Update drone status"""
    if drone_id not in drones_store:
        raise HTTPException(status_code=404, detail="Drone not found")
    
    valid_statuses = ["offline", "standby", "active", "maintenance"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    drones_store[drone_id].status = status
    drones_store[drone_id].last_seen = datetime.now()
    
    return {"message": "Status updated successfully"}

@app.post("/missions", response_model=Mission)
async def create_mission(mission: Mission):
    """Create a new mission"""
    # Validate assigned drones exist
    for drone_id in mission.assigned_drone_ids:
        if drone_id not in drones_store:
            raise HTTPException(status_code=404, detail=f"Drone {drone_id} not found")
    
    missions_store[mission.mission_id] = mission
    return mission

@app.get("/missions", response_model=List[Mission])
async def list_missions(status: Optional[str] = None):
    """List all missions, optionally filtered by status"""
    missions = list(missions_store.values())
    if status:
        missions = [m for m in missions if m.status == status]
    return missions

@app.put("/missions/{mission_id}/start")
async def start_mission(mission_id: str):
    """Start a mission"""
    if mission_id not in missions_store:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    mission = missions_store[mission_id]
    mission.status = "active"
    mission.start_time = datetime.now()
    
    # Update assigned drones status
    for drone_id in mission.assigned_drone_ids:
        if drone_id in drones_store:
            drones_store[drone_id].status = "active"
            drones_store[drone_id].current_mission_id = mission_id
    
    return {"message": "Mission started successfully"}

@app.post("/telemetry/ingest")
async def ingest_telemetry(telemetry: TelemetryData):
    """Ingest telemetry data from drones"""
    # Validate drone exists
    if telemetry.drone_id not in drones_store:
        raise HTTPException(status_code=404, detail="Drone not found")
    
    # Update drone location and battery
    drone = drones_store[telemetry.drone_id]
    drone.location = telemetry.location
    drone.battery_level = telemetry.battery_level
    drone.last_seen = telemetry.timestamp
    
    # Store telemetry data
    if telemetry.drone_id not in telemetry_store:
        telemetry_store[telemetry.drone_id] = []
    
    telemetry_store[telemetry.drone_id].append(telemetry.dict())
    
    # Keep only last 1000 records per drone
    if len(telemetry_store[telemetry.drone_id]) > 1000:
        telemetry_store[telemetry.drone_id] = telemetry_store[telemetry.drone_id][-1000:]
    
    return {"message": "Telemetry ingested successfully"}

@app.get("/telemetry/{drone_id}")
async def get_telemetry(
    drone_id: str,
    limit: int = 100,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
):
    """Get telemetry data for a specific drone"""
    if drone_id not in telemetry_store:
        return {"drone_id": drone_id, "telemetry": []}
    
    telemetry_data = telemetry_store[drone_id]
    
    # Apply time filters if provided
    if start_time or end_time:
        filtered_data = []
        for record in telemetry_data:
            record_time = datetime.fromisoformat(record["timestamp"])
            if start_time and record_time < start_time:
                continue
            if end_time and record_time > end_time:
                continue
            filtered_data.append(record)
        telemetry_data = filtered_data
    
    # Apply limit
    telemetry_data = telemetry_data[-limit:]
    
    return {"drone_id": drone_id, "telemetry": telemetry_data}

@app.post("/simulations", response_model=dict)
async def start_simulation(config: SimulationConfig):
    """Start a drone simulation"""
    simulation_id = await simulator.start_simulation(config)
    simulations_store[simulation_id] = config
    
    return {
        "simulation_id": simulation_id,
        "message": "Simulation started successfully",
        "status": "running"
    }

@app.get("/simulations")
async def list_simulations():
    """List all simulations"""
    return {
        "running": list(simulator.running_simulations.keys()),
        "stored": list(simulations_store.keys())
    }

@app.delete("/simulations/{simulation_id}")
async def stop_simulation(simulation_id: str):
    """Stop a running simulation"""
    if simulation_id not in simulator.running_simulations:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    simulator.running_simulations[simulation_id]["status"] = "stopped"
    del simulator.running_simulations[simulation_id]
    
    # Close WebSocket if connected
    if simulation_id in active_websockets:
        del active_websockets[simulation_id]
    
    return {"message": "Simulation stopped successfully"}

@app.websocket("/ws/telemetry/{simulation_id}")
async def websocket_telemetry(websocket: WebSocket, simulation_id: str):
    """WebSocket endpoint for real-time telemetry data"""
    await websocket.accept()
    active_websockets[simulation_id] = websocket
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        if simulation_id in active_websockets:
            del active_websockets[simulation_id]

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "service": "Drones Service",
        "status": "healthy",
        "active_drones": len([d for d in drones_store.values() if d.status == "active"]),
        "total_drones": len(drones_store),
        "active_missions": len([m for m in missions_store.values() if m.status == "active"]),
        "running_simulations": len(simulator.running_simulations),
        "timestamp": datetime.now(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)