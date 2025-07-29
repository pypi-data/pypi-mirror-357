from pydantic import BaseModel, Field
from functools import wraps
from fastapi import APIRouter
import json
import requests
from typing import Dict, Any
import threading
        
class PyMicroservicesConfig(BaseModel):
    service_name: str
    discovery_server_address: str 
    gateway_address: str
    heartbeat_rate: int = Field(default=60)

    @classmethod
    def load(cls, path: str) -> "PyMicroservicesConfig":
        with open(path, 'r') as f:
            data = json.load(f)
        return cls(**data)

class PyMicroservice:
    def __init__(self, config_file: str):
        self.config = PyMicroservicesConfig.load(config_file)
        self.address = None
        self.port = None
        self._heartbeat_thread = None
        self._stop_event = threading.Event()

    def start(self, address: str, port: int):
        self.address = address
        self.port = port
        print(f"Starting service {self.config.service_name} at {self.config.discovery_server_address} with heartbeat rate {self.config.heartbeat_rate} seconds.")

        self._stop_event.clear()
        self._heartbeat_thread = threading.Thread(target=self._run_heartbeat, daemon=True)
        self._heartbeat_thread.start()

    def _run_heartbeat(self):
        while not self._stop_event.is_set():
            self._notify_discovery_server()
            self._stop_event.wait(self.config.heartbeat_rate)

    def _notify_discovery_server(self):
        try:     
            requests.post(f"{self.config.discovery_server_address}/register?address={self.address}:{self.port}&service_name={self.config.service_name}")
        except requests.RequestException as e:
            pass
    
    def stop(self):
        
        try:
            self._stop_event.set()
            if self._heartbeat_thread is not None:
                self._heartbeat_thread.join()
            print(f"Stopping service {self.config.service_name} at {self.config.discovery_server_address}.")
            requests.post(f"{self.config.discovery_server_address}/deregister?address={self.address}:{self.port}&service_name={self.config.service_name}")
        except requests.RequestException as e:
            pass


def get(path: str):
    def decorator(func):
        func._route_info = ("GET", path)
        return func
    return decorator

def post(path: str):
    def decorator(func):
        func._route_info = ("POST", path)
        return func
    return decorator

def put(path: str):
    def decorator(func):
        func._route_info = ("PUT", path)
        return func
    return decorator

def delete(path: str):
    def decorator(func):
        func._route_info = ("DELETE", path)
        return func
    return decorator


class PyMicroserviceRouter:
    _router: APIRouter = None

    def __init__(self, service):
        self._service = service
        self._register_routes()

    @classmethod
    def use_router(cls, router: APIRouter):
        cls._router = router
        return cls

    def get_router(self) -> APIRouter:
        if not self._router:
            raise RuntimeError("Router not set.")
        return self._router
    
    def get_from_microservice(self, service_name: str, path: str, params: Dict[str, any] = None) -> Any:
        if path.startswith("/"):
            path = path[1:]
        response = requests.get(f"{self._service.config.gateway_address}/{service_name}/{path}", params=params)
        if response.status_code == 200:
            return response.json()
        

    def post_to_microservice(self, service_name: str, path: str, params: Dict[str, any] = None, data: Dict[str, any] = None) -> Any:
        if path.startswith("/"):
            path = path[1:]
        response = requests.post(f"{self._service.config.gateway_address}/{service_name}/{path}", params=params, json=data)
        if response.status_code == 200:
            return response.json()
        
    def put_to_microservice(self, service_name: str, path: str, params: Dict[str, any] = None, data: Dict[str, any] = None) -> Any:
        if path.startswith("/"):
            path = path[1:]
        response = requests.put(f"{self._service.config.gateway_address}/{service_name}/{path}", params=params, json=data)
        if response.status_code == 200:
            return response.json()
        
    def delete_from_microservice(self, service_name: str, path: str, params: Dict[str, any] = None) -> Any:
        if path.startswith("/"):
            path = path[1:]
        response = requests.delete(f"{self._service.config.gateway_address}/{service_name}/{path}", params=params)
        if response.status_code == 200:
            return response.json()


    def _register_routes(self):
        for attr_name in dir(self):
            method = getattr(self, attr_name)
            if not callable(method) or not hasattr(method, "_route_info"):
                continue

            http_method, path = method._route_info

            # Generate an endpoint that does NOT expose self
            endpoint = self._create_endpoint(method)

            self._router.add_api_route(path, endpoint, methods=[http_method])

    def _create_endpoint(self, method):
        """
        Wrap instance method in a function that captures `self` via closure
        and exposes no `self` argument to FastAPI.
        """
        @wraps(method)
        async def endpoint(*args, **kwargs):
            return await method(*args, **kwargs)

        # Do NOT call inspect.signature on bound methods
        return endpoint
