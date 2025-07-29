# isaac_sim_mcp_server.py
import time
from mcp.server.fastmcp import FastMCP, Context, Image
import socket
import json
import asyncio
import logging
from dataclasses import dataclass
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any, List
import os
from pathlib import Path
import base64
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("IsaacMCPServer")

# Global variables for duplicate detection
_recent_commands = []
_max_duplicate_attempts = 3

def is_duplicate_command(command_type: str, params: Dict[str, Any]) -> bool:
    """Check if this is a duplicate command"""
    command_key = f"{command_type}:{json.dumps(params, sort_keys=True)}"
    
    # Count how many times this exact command appears in recent history
    count = _recent_commands.count(command_key)
    
    # Add to history
    _recent_commands.append(command_key)
    
    # Keep only last 10 commands
    if len(_recent_commands) > 10:
        _recent_commands.pop(0)
    
    # If this exact command has been called 3+ times, it's a duplicate
    if count >= _max_duplicate_attempts:
        logger.warning(f"Duplicate command detected: {command_type} (attempt #{count + 1})")
        return True
    
    return False

@dataclass
class IsaacConnection:
    host: str
    port: int
    sock: socket.socket = None  # Changed from 'socket' to 'sock' to avoid naming conflict
    
    def connect(self) -> bool:
        """Connect to the Isaac addon socket server"""
        if self.sock:
            return True
            
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            logger.info(f"Connected to Isaac at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Isaac: {str(e)}")
            self.sock = None
            return False
    
    def disconnect(self):
        """Disconnect from the Isaac addon"""
        if self.sock:
            try:
                self.sock.close()
            except Exception as e:
                logger.error(f"Error disconnecting from Isaac: {str(e)}")
            finally:
                self.sock = None

    def receive_full_response(self, sock, buffer_size=16384):
        """Receive the complete response, potentially in multiple chunks"""
        chunks = []
        # Use a consistent timeout value that matches the addon's timeout
        sock.settimeout(300.0)  # Match the extension's timeout
        
        try:
            while True:
                try:
                    logger.info("Waiting for data from Isaac")
                    #time.sleep(0.5)
                    chunk = sock.recv(buffer_size)
                    if not chunk:
                        # If we get an empty chunk, the connection might be closed
                        if not chunks:  # If we haven't received anything yet, this is an error
                            raise Exception("Connection closed before receiving any data")
                        break
                    
                    chunks.append(chunk)
                    
                    # Check if we've received a complete JSON object
                    try:
                        data = b''.join(chunks)
                        json.loads(data.decode('utf-8'))
                        # If we get here, it parsed successfully
                        logger.info(f"Received complete response ({len(data)} bytes)")
                        return data
                    except json.JSONDecodeError:
                        # Incomplete JSON, continue receiving
                        continue
                except socket.timeout:
                    # If we hit a timeout during receiving, break the loop and try to use what we have
                    logger.warning("Socket timeout during chunked receive")
                    break
                except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
                    logger.error(f"Socket connection error during receive: {str(e)}")
                    raise  # Re-raise to be handled by the caller
        except socket.timeout:
            logger.warning("Socket timeout during chunked receive")
        except Exception as e:
            logger.error(f"Error during receive: {str(e)}")
            raise
            
        # If we get here, we either timed out or broke out of the loop
        # Try to use what we have
        if chunks:
            data = b''.join(chunks)
            logger.info(f"Returning data after receive completion ({len(data)} bytes)")
            try:
                # Try to parse what we have
                json.loads(data.decode('utf-8'))
                return data
            except json.JSONDecodeError:
                # If we can't parse it, it's incomplete
                raise Exception("Incomplete JSON response received")
        else:
            raise Exception("No data received")

    def send_command(self, command_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a command to Isaac and return the response"""
        if not self.sock and not self.connect():
            raise ConnectionError("Not connected to Isaac")
        
        command = {
            "type": command_type,
            "params": params or {}
        }
        
        try:
            # Log the command being sent
            logger.info(f"Sending command: {command_type} with params: {params}")
            
            # Send the command
            self.sock.sendall(json.dumps(command).encode('utf-8'))
            logger.info(f"Command sent, waiting for response...")
            
            # Set a timeout for receiving - use the same timeout as in receive_full_response
            self.sock.settimeout(300.0)  # Match the extension's timeout
            
            # Receive the response using the improved receive_full_response method
            response_data = self.receive_full_response(self.sock)
            logger.info(f"Received {len(response_data)} bytes of data")
            
            response = json.loads(response_data.decode('utf-8'))
            logger.info(f"Response parsed, status: {response.get('status', 'unknown')}")
            
            if response.get("status") == "error":
                logger.error(f"Isaac error: {response.get('message')}")
                raise Exception(response.get("message", "Unknown error from Isaac"))
            
            # Return the entire response, not just the result field
            return response
        except socket.timeout:
            logger.error("Socket timeout while waiting for response from Isaac")
            # Don't try to reconnect here - let the get_isaac_connection handle reconnection
            # Just invalidate the current socket so it will be recreated next time
            self.sock = None
            raise Exception("Timeout waiting for Isaac response - try simplifying your request")
        except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
            logger.error(f"Socket connection error: {str(e)}")
            self.sock = None
            raise Exception(f"Connection to Isaac lost: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Isaac: {str(e)}")
            # Try to log what was received
            if 'response_data' in locals() and response_data:
                logger.error(f"Raw response (first 200 bytes): {response_data[:200]}")
            raise Exception(f"Invalid response from Isaac: {str(e)}")
        except Exception as e:
            logger.error(f"Error communicating with Isaac: {str(e)}")
            # Don't try to reconnect here - let the get_isaac_connection handle reconnection
            self.sock = None
            raise Exception(f"Communication error with Isaac: {str(e)}")

@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Manage server startup and shutdown lifecycle"""
    # We don't need to create a connection here since we're using the global connection
    # for resources and tools
    
    try:
        # Just log that we're starting up
        logger.info("IsaacMCP server starting up")
        
        # Try to connect to Isaac on startup to verify it's available
        try:
            # This will initialize the global connection if needed
            isaac = get_isaac_connection()
            logger.info("Successfully connected to Isaac on startup")
        except Exception as e:
            logger.warning(f"Could not connect to Isaac on startup: {str(e)}")
            logger.warning("Make sure the Isaac addon is running before using Isaac resources or tools")
        
        # Return an empty context - we're using the global connection
        yield {}
    finally:
        # Clean up the global connection on shutdown
        global _isaac_connection
        if _isaac_connection:
            logger.info("Disconnecting from Isaac Sim on shutdown")
            _isaac_connection.disconnect()
            _isaac_connection = None
        logger.info("Isaac SimMCP server shut down")

# Create the MCP server with lifespan support
mcp = FastMCP(
    "IsaacSimMCP",
    description="Isaac Sim integration through the Model Context Protocol",
    lifespan=server_lifespan
)

# Resource endpoints

# Global connection for resources (since resources can't access context)
_isaac_connection = None
# _polyhaven_enabled = False  # Add this global variable

def get_isaac_connection():
    """Get or create a persistent Isaac connection"""
    global _isaac_connection
    
    # If we have an existing connection, check if it's still valid
    if _isaac_connection is not None:
        try:
            return _isaac_connection
        except Exception as e:
            # Connection is dead, close it and create a new one
            logger.warning(f"Existing connection is no longer valid: {str(e)}")
            try:
                _isaac_connection.disconnect()
            except:
                pass
            _isaac_connection = None
    
    # Create a new connection if needed
    if _isaac_connection is None:
        _isaac_connection = IsaacConnection(host="localhost", port=8766)
        if not _isaac_connection.connect():
            logger.error("Failed to connect to Isaac")
            _isaac_connection = None
            raise Exception("Could not connect to Isaac. Make sure the Isaac addon is running.")
        logger.info("Created new persistent connection to Isaac")
    
    return _isaac_connection


@mcp.tool("odyssey-get_scene_info")
def get_scene_info(ctx: Context) -> str:
    """Ping status of Isaac Sim Extension Server"""
    try:
        isaac = get_isaac_connection()
        result = isaac.send_command("get_scene_info")
        print("result: ", result)
        
        # Just return the JSON representation of what Isaac sent us
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting scene info from Isaac: {str(e)}")
        return json.dumps({"status": "error", "error": str(e), "message": "Error getting scene info"})

@mcp.tool("odyssey-create_physics_scene")
def create_physics_scene(
    objects: List[Dict[str, Any]] = [],
    floor: bool = True,
    gravity: List[float] = [0,  -0.981, 0],
    scene_name: str = "physics_scene"
) -> str:
    """Create a complete physics simulation scene with floor, gravity and multiple objects.
    
    ⚠️ WARNING: This tool is for creating PHYSICS SCENES, NOT for creating single objects!
    For creating single shapes like cubes, use omni_kit_command instead.
    
    Args:
        objects: List of objects to create in the physics scene. Each object should have at least 'type' and 'position'. 
        objects  = [
        {"path": "/World/Cube", "type": "Cube", "size": 20, "position": [0, 100, 0]},
        {"path": "/World/Sphere", "type": "Sphere", "radius": 5, "position": [5, 200, 0]},
        {"path": "/World/Cone", "type": "Cone", "height": 8, "radius": 3, "position": [-5, 150, 0]}
         ]
        floor: Whether to create a floor. default is True
        gravity: The gravity vector. Default is [0, 0, -981.0] (cm/s^2).
        scene_name: The name of the scene. default is "physics_scene"
        
    Returns:
        String with result information.
    """
    params = {"objects": objects, "floor": floor}
    
    if gravity is not None:
        params["gravity"] = gravity
    if scene_name is not None:
        params["scene_name"] = scene_name
    
    # Check for duplicate commands
    if is_duplicate_command("create_physics_scene", params):
        return "Physics scene creation already attempted multiple times. The scene should already be created."
    
    try:
        isaac = get_isaac_connection()
        result = isaac.send_command("create_physics_scene", params)
        
        # Check status at top level
        if result.get("status") == "success":
            return f"Successfully created physics scene: {result.get('message', 'Physics scene created')}"
        else:
            return f"Error creating physics scene: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error create_physics_scene: {str(e)}")
        return f"Error creating physics scene: {str(e)}"
    
@mcp.tool("odyssey-create_robot")
def create_robot(robot_type: str = "g1", position: List[float] = [0, 0, 0]) -> str:
    """Create a robot in the Isaac scene. Directly create robot prim in stage at the right position. For any creation of robot, you need to call create_physics_scene() first. call create_robot() as first attempt before call execute_script().
    
    Args:
        robot_type: The type of robot to create. Available options:
            - "franka": Franka Emika Panda robot
            - "jetbot": NVIDIA JetBot robot
            - "carter": Carter delivery robot
            - "g1": Unitree G1 quadruped robot (default)
            - "go1": Unitree Go1 quadruped robot
        
    Returns:
        String with result information.
    """
    params = {"robot_type": robot_type, "position": position}
    
    # Check for duplicate commands
    if is_duplicate_command("create_robot", params):
        return f"Robot {robot_type} creation already attempted multiple times. The robot should already be created."
    
    try:
        isaac = get_isaac_connection()
        result = isaac.send_command("create_robot", params)
        
        if result.get("status") == "success":
            return f"Successfully created robot: {result.get('message', 'Robot created')}"
        else:
            return f"Error creating robot: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error creating robot: {str(e)}")
        return f"Error creating robot: {str(e)}"

@mcp.tool("odyssey-omni_kit_command")
def omni_kit_command(
    command: str = "CreatePrim", 
    prim_type: str = "Sphere", 
    prim_path: str = None,
    batch: List[Dict[str, Any]] = None
) -> str:
    """Execute an Omni Kit command - supports both single and batch operations.
    
    FOR SINGLE OBJECT:
    1. First: omni_kit_command(command="CreatePrim", prim_type="Cube", prim_path="/World/MyCube")
    2. Then: transform(prim_path="/World/MyCube", scale=[10, 10, 10])
    
    FOR BATCH CREATION (much faster for multiple objects):
    omni_kit_command(
        command="CreatePrim",
        prim_type="Sphere", 
        batch=[
            {"prim_path": "/World/Sphere_0", "position": [20, 0, 0], "scale": [10, 10, 10]},
            {"prim_path": "/World/Sphere_1", "position": [16.18, 11.76, 0], "scale": [10, 10, 10]},
            {"prim_path": "/World/Sphere_2", "position": [6.18, 19.02, 0], "scale": [10, 10, 10]}
        ]
    )
    
    Args:
        command: The Omni Kit command to execute (default: "CreatePrim")
        prim_type: The primitive type for the command (default: "Sphere")
        prim_path: Path for single object creation (ignored if batch is provided)
        batch: List of objects to create, each dict can contain:
            - prim_path: Path for the prim (required)
            - position: [x, y, z] position (optional, default: [0, 0, 0])
            - scale: [x, y, z] scale (optional, default: [1, 1, 1])
            - rotation: [x, y, z, w] quaternion (optional)
            - additional params as needed
        
    Returns:
        String with result information.
    """
    
    # Handle batch operations
    if batch and isinstance(batch, list) and len(batch) > 0:
        # Build batch command parameters
        batch_params = {
            "command": command,
            "prim_type": prim_type,
            "batch_operations": []
        }
        
        # Process each item in the batch
        created_paths = []
        for idx, item in enumerate(batch):
            if not isinstance(item, dict):
                return f"Error: Batch item {idx} must be a dictionary"
            
            if "prim_path" not in item:
                return f"Error: Batch item {idx} missing required 'prim_path'"
            
            # Build operation for this item
            operation = {
                "prim_path": item["prim_path"],
                "position": item.get("position", [0, 0, 0]),
                "scale": item.get("scale", [1, 1, 1])
            }
            
            # Add optional parameters
            if "rotation" in item:
                operation["rotation"] = item["rotation"]
            
            # Add any additional custom parameters
            for key, value in item.items():
                if key not in ["prim_path", "position", "scale", "rotation"]:
                    operation[key] = value
            
            batch_params["batch_operations"].append(operation)
            created_paths.append(item["prim_path"])
        
        # Check for duplicate batch command (entire batch)
        batch_key = f"batch_{command}_{prim_type}_{len(batch)}"
        if is_duplicate_command(batch_key, batch_params):
            paths_str = ", ".join(created_paths[:3])
            if len(created_paths) > 3:
                paths_str += f" and {len(created_paths) - 3} more"
            return f"Batch creation of {len(batch)} {prim_type} objects already attempted. Objects should exist at: {paths_str}"
        
        try:
            # Get the global connection
            isaac = get_isaac_connection()
            
            # Send batch command to Isaac
            logger.info(f"Sending batch command to create {len(batch)} objects")
            result = isaac.send_command("omni_kit_batch_command", batch_params)
            
            # Check status
            if result.get("status") == "success":
                created_count = result.get("created_count", len(batch))
                failed_count = result.get("failed_count", 0)
                
                if failed_count > 0:
                    failed_paths = result.get("failed_paths", [])
                    return (f"Batch operation completed with warnings: "
                           f"{created_count} objects created successfully, "
                           f"{failed_count} failed. Failed paths: {', '.join(failed_paths[:5])}")
                else:
                    paths_preview = ", ".join(created_paths[:3])
                    if len(created_paths) > 3:
                        paths_preview += f" and {len(created_paths) - 3} more"
                    
                    return (f"Successfully created {created_count} {prim_type} objects in batch mode. "
                           f"Created at: {paths_preview}. "
                           f"This is {len(batch)}x faster than individual creation!")
            else:
                error_msg = result.get('message', 'Unknown error')
                
                # Fall back to individual creation if batch is not supported
                if "not supported" in error_msg.lower() or "not implemented" in error_msg.lower():
                    logger.warning("Batch command not supported by Isaac addon, falling back to individual creation")
                    return _fallback_individual_creation(command, prim_type, batch)
                else:
                    return f"Error executing batch command: {error_msg}"
                    
        except Exception as e:
            logger.error(f"Error executing batch command: {str(e)}")
            
            # Attempt fallback to individual creation
            if "batch" in str(e).lower() or "not supported" in str(e).lower():
                logger.info("Attempting fallback to individual creation")
                return _fallback_individual_creation(command, prim_type, batch)
            else:
                return f"Error executing batch command: {str(e)}"
    
    # Original single object creation logic
    else:
        # Build parameters
        params = {
            "command": command,
            "prim_type": prim_type
        }
        
        # Add prim_path if provided
        if prim_path:
            params["prim_path"] = prim_path
        
        # Check for duplicate commands
        if is_duplicate_command("omni_kit_command", params):
            return (f"Object {prim_type} at {prim_path if prim_path else 'auto-generated path'} "
                   f"has already been created. Skipping duplicate creation. "
                   f"Use transform tool to modify it if needed.")
        
        try:
            isaac = get_isaac_connection()
            result = isaac.send_command("omni_kit_command", params)
            
            if result.get("status") == "success":
                actual_prim_path = result.get('prim_path', prim_path)
                prim_path_info = f" at path: {actual_prim_path}" if actual_prim_path else ""
                
                if command == "CreatePrim":
                    return (f"Successfully created {prim_type}{prim_path_info}. "
                           f"Default size is 1x1x1. "
                           f"To scale it, use: transform(prim_path=\"{actual_prim_path}\", "
                           f"scale=[desired_x, desired_y, desired_z])")
                else:
                    return f"Omni Kit command '{command}' executed successfully: {result.get('message', '')}{prim_path_info}"
            else:
                error_msg = result.get('message', 'Unknown error')
                
                if "already exists" in error_msg.lower():
                    return (f"Object already exists at {prim_path}. "
                           f"To modify it, use transform tool. "
                           f"To create a new one, use a different prim_path.")
                else:
                    return f"Error executing Omni Kit command: {error_msg}"
                    
        except Exception as e:
            logger.error(f"Error executing Omni Kit command: {str(e)}")
            
            if "Connection" in str(e):
                return "Error: Lost connection to Isaac Sim. Please ensure Isaac Sim is running and try again."
            elif "Timeout" in str(e):
                return "Error: Command timed out. The operation might be too complex or Isaac Sim might be busy."
            else:
                return f"Error executing Omni Kit command: {str(e)}"


def _fallback_individual_creation(command: str, prim_type: str, batch: List[Dict[str, Any]]) -> str:
    """Fallback function to create objects individually when batch is not supported"""
    logger.info(f"Starting fallback individual creation for {len(batch)} objects")
    
    try:
        isaac = get_isaac_connection()
        success_count = 0
        failed_count = 0
        failed_paths = []
        
        for idx, item in enumerate(batch):
            try:
                # Create the object
                create_params = {
                    "command": command,
                    "prim_type": prim_type,
                    "prim_path": item["prim_path"]
                }
                
                create_result = isaac.send_command("omni_kit_command", create_params)
                
                if create_result.get("status") == "success":
                    # Apply transform if position or scale is specified
                    if "position" in item or "scale" in item:
                        transform_params = {
                            "prim_path": item["prim_path"],
                            "position": item.get("position", [0, 0, 0]),
                            "scale": item.get("scale", [1, 1, 1])
                        }
                        
                        if "rotation" in item:
                            transform_params["rotation"] = item["rotation"]
                        
                        transform_result = isaac.send_command("transform", transform_params)
                        
                        if transform_result.get("status") == "success":
                            success_count += 1
                        else:
                            failed_count += 1
                            failed_paths.append(item["prim_path"])
                    else:
                        success_count += 1
                else:
                    failed_count += 1
                    failed_paths.append(item["prim_path"])
                    
            except Exception as e:
                logger.error(f"Error creating object {idx}: {str(e)}")
                failed_count += 1
                failed_paths.append(item.get("prim_path", f"index_{idx}"))
        
        # Return summary
        if failed_count == 0:
            return (f"Successfully created {success_count} {prim_type} objects using fallback method. "
                   f"Note: Batch operations would be {len(batch)}x faster if supported.")
        else:
            return (f"Fallback creation completed with mixed results: "
                   f"{success_count} succeeded, {failed_count} failed. "
                   f"Failed paths: {', '.join(failed_paths[:5])}")
                   
    except Exception as e:
        logger.error(f"Error in fallback creation: {str(e)}")
        return f"Error in fallback creation: {str(e)}"      

@mcp.tool()
def execute_script(ctx: Context, code: str) -> str:
    """
    Before execute script pls check prompt from asset_creation_strategy() to ensure the scene is properly initialized.
    Execute arbitrary Python code in Isaac Sim. Before executing any code, first verify if get_scene_info() has been called to ensure the scene is properly initialized. Always print the formatted code into chat to confirm before execution to confirm its correctness. 
    Before execute script pls check if create_physics_scene() has been called to ensure the physics scene is properly initialized.
    When working with robots, always try using the create_robot() function first before resorting to execute_script(). The create_robot() function provides a simpler, more reliable way to add robots to your scene with proper initialization and positioning. Only use execute_script() for robot creation when you need custom configurations or behaviors not supported by create_robot().
    
    For physics simulation, avoid using simulation_context to run simulations in the main thread as this can cause blocking. Instead, use the World class with async methods for initializing physics and running simulations. For example, use my_world = World(physics_dt=1.0/60.0) and my_world.step_async() in a loop, which allows for better performance and responsiveness. If you need to wait for physics to stabilize, consider using my_world.play() followed by multiple step_async() calls.
    
    Parameters:
    - code: The Python code to execute
    """
    try:
        isaac = get_isaac_connection()
        print("code: ", code)
        
        result = isaac.send_command("execute_script", {"code": code})
        print("result: ", result)
        
        # Return the result as JSON string
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Error executing code: {str(e)}")
        return json.dumps({"status": "error", "error": str(e), "message": "Error executing code"})
                
@mcp.prompt("odyssey-asset_creation_strategy")
def asset_creation_strategy() -> str:
    """Defines the preferred strategy for creating assets in Isaac Sim"""
    return """
    # Tool Selection Guidelines
    
    ## IMPORTANT: Choose the right tool for the task:
    - **Single basic shape (cube, sphere, cone, etc.)**: Use `omni_kit_command` with CreatePrim
    - **Single shape with specific size**: Use `omni_kit_command` + `transform` (CreatePrim creates 1x1x1 by default)
    - **Physics simulation scene with multiple objects**: Use `create_physics_scene`
    - **Robot creation**: Always try `create_robot` first, only use `execute_script` for custom configurations
    - **3D model from text/image**: Use `generate_3d_from_text_or_image` or `search_3d_usd_by_text`
    - **Complex custom operations**: Use `execute_script`
    
    ## Step-by-Step Process:
    
    0. **Before anything**, always check the scene from get_scene_info(), retrieve root path of assets through return value of assets_root_path.
    
    1. **Scene Initialization**:
       - If the scene is empty and you need physics simulation, create a physics scene with create_physics_scene()
       - If you just need to create individual objects without physics, use omni_kit_command directly
    
    2. **Error Handling**:
       - If execute_script fails due to communication error, retry maximum 3 times
       - If a tool returns an error, check the error message and try an alternative approach
    
    3. **Creating Basic Shapes**:
       - Use omni_kit_command(command="CreatePrim", prim_type="Cube") for basic shapes
       - Default size is 1x1x1, use transform() to scale to desired size
       - Example: To create a 10x10x10 cube:
         1. omni_kit_command(command="CreatePrim", prim_type="Cube", prim_path="/World/MyCube")
         2. transform(prim_path="/World/MyCube", scale=[10, 10, 10])
    
    4. **Robot Creation and Control**:
       - Always use create_robot() first for supported robots (franka, jetbot, carter, g1, go1)
       - Only use execute_script() when you need custom robot configurations
    
    5. **For Franka robot simulation** (using execute_script):
    ```python
    from omni.isaac.core import SimulationContext
    from omni.isaac.core.utils.prims import create_prim
    from omni.isaac.core.utils.stage import add_reference_to_stage, is_stage_loading
    from omni.isaac.nucleus import get_assets_root_path

    assets_root_path = get_assets_root_path()
    asset_path = assets_root_path + "/Isaac/Robots/Franka/franka_alt_fingers.usd"
    add_reference_to_stage(asset_path, "/Franka")

    # Initialize physics
    simulation_context = SimulationContext()
    simulation_context.initialize_physics()
    simulation_context.play()

    for i in range(1000):
        simulation_context.step(render=True)

    simulation_context.stop()
    ```

    6. **For Franka robot control** (using execute_script):
    ```python
    from omni.isaac.core import SimulationContext, World
    from omni.isaac.core.articulations import Articulation
    from omni.isaac.core.utils.stage import add_reference_to_stage
    from omni.isaac.nucleus import get_assets_root_path
    from pxr import UsdPhysics

    def create_physics_scene(stage, scene_path="/World/PhysicsScene"):
        if not stage.GetPrimAtPath(scene_path):
            UsdPhysics.Scene.Define(stage, scene_path)
        return stage.GetPrimAtPath(scene_path)

    stage = omni.usd.get_context().get_stage()
    physics_scene = create_physics_scene(stage)
    if not physics_scene:
        raise RuntimeError("Failed to create or find physics scene")

    simulation_context = SimulationContext()
    assets_root_path = get_assets_root_path()
    asset_path = assets_root_path + "/Isaac/Robots/Franka/franka_alt_fingers.usd"
    add_reference_to_stage(asset_path, "/Franka")

    # Initialize physics and articulation
    simulation_context.initialize_physics()
    art = Articulation("/Franka")
    art.initialize()
    dof_ptr = art.get_dof_index("panda_joint2")

    simulation_context.play()
    for i in range(1000):
        art.set_joint_positions([-1.5], [dof_ptr])
        simulation_context.step(render=True)

    simulation_context.stop()
    ```

    7. **For Jetbot simulation** (using execute_script):
    ```python
    import carb
    import numpy as np
    from omni.isaac.core import World, SimulationContext
    from omni.isaac.core.utils.prims import create_prim
    from omni.isaac.nucleus import get_assets_root_path
    from omni.isaac.wheeled_robots.controllers.differential_controller import DifferentialController
    from omni.isaac.wheeled_robots.robots import WheeledRobot

    simulation_context = SimulationContext()
    simulation_context.initialize_physics()

    my_world = World(stage_units_in_meters=1.0)

    assets_root_path = get_assets_root_path()
    if assets_root_path is None:
        carb.log_error("Could not find Isaac Sim assets folder")
    jetbot_asset_path = assets_root_path + "/Isaac/Robots/Jetbot/jetbot.usd"
    my_jetbot = my_world.scene.add(
        WheeledRobot(
            prim_path="/World/Jetbot",
            name="my_jetbot",
            wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
            create_robot=True,
            usd_path=jetbot_asset_path,
            position=np.array([0, 0.0, 2.0]),
        )
    )

    create_prim("/DistantLight", "DistantLight")
    my_world.scene.add_default_ground_plane()
    my_controller = DifferentialController(name="simple_control", wheel_radius=0.03, wheel_base=0.1125)
    my_world.reset()

    simulation_context.play()
    for i in range(10):
        simulation_context.step(render=True) 

    i = 0
    reset_needed = False
    while i < 2000:
        my_world.step(render=True)
        if my_world.is_stopped() and not reset_needed:
            reset_needed = True
        if my_world.is_playing():
            if reset_needed:
                my_world.reset()
                my_controller.reset()
                reset_needed = False
            if i >= 0 and i < 1000:
                # forward
                my_jetbot.apply_wheel_actions(my_controller.forward(command=[0.05, 0]))
                print(my_jetbot.get_linear_velocity())
            elif i >= 1000 and i < 1300:
                # rotate
                my_jetbot.apply_wheel_actions(my_controller.forward(command=[0.0, np.pi / 12]))
                print(my_jetbot.get_angular_velocity())
            elif i >= 1300 and i < 2000:
                # forward
                my_jetbot.apply_wheel_actions(my_controller.forward(command=[0.05, 0]))
            elif i == 2000:
                i = 0
            i += 1
    simulation_context.stop()
    ```

    8. **For G1 simulation**: See g1_ok.py for reference implementation

    ## Best Practices:
    - Always verify connection with get_scene_info() before starting
    - Use the simplest tool that accomplishes the task
    - Avoid using execute_script for simple operations that dedicated tools can handle
    - When creating multiple objects, consider whether you need physics simulation or just static objects
    - Remember that omni_kit_command creates objects with default size 1x1x1
    """

def _process_bbox(original_bbox: list[float] | list[int] | None) -> list[int] | None:
    if original_bbox is None:
        return None
    if all(isinstance(i, int) for i in original_bbox):
        return original_bbox
    if any(i<=0 for i in original_bbox):
        raise ValueError("Incorrect number range: bbox must be bigger than zero!")
    return [int(float(i) / max(original_bbox) * 100) for i in original_bbox] if original_bbox else None

#@mcp.tool()
def get_beaver3d_status(ctx: Context) -> str:
    """
    TODO: Get the status of Beaver3D.
    """
    return "Beaver3D service is Available"

@mcp.tool("odyssey-generate_3d_from_text_or_image")
def generate_3d_from_text_or_image(
    ctx: Context,
    text_prompt: str = None,
    image_url: str = None,
    position: List[float] = [0, 0, 50],
    scale: List[float] = [10, 10, 10]
) -> str:
    """
    Generate a 3D model from text or image, load it into the scene and transform it.
    
    Args:
        text_prompt (str, optional): Text prompt for 3D generation
        image_url (str, optional): URL of image for 3D generation
        position (list, optional): Position to place the model [x, y, z]
        scale (list, optional): Scale of the model [x, y, z]
        
    Returns:
        String with the task_id and prim_path information
    """
    if not (text_prompt or image_url):
        return "Error: Either text_prompt or image_url must be provided"
    
    try:
        isaac = get_isaac_connection()
        
        result = isaac.send_command("generate_3d_from_text_or_image", {
            "text_prompt": text_prompt,
            "image_url": image_url,
            "position": position,
            "scale": scale
        })
        
        if result.get("status") == "success":
            task_id = result.get("task_id")
            prim_path = result.get("prim_path")
            return f"Successfully generated 3D model with task ID: {task_id}, loaded at prim path: {prim_path}"
        else:
            return f"Error generating 3D model: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error generating 3D model: {str(e)}")
        return f"Error generating 3D model: {str(e)}"
    
@mcp.tool("odyssey-search_3d_usd_by_text")
def search_3d_usd_by_text(
    ctx: Context,
    text_prompt: str = None,
    target_path: str = "/World/my_usd",
    position: List[float] = [0, 0, 50],
    scale: List[float] = [10, 10, 10]
) -> str:
    """
    Search for a 3D model using text prompt in USD libraries, then load and position it in the scene.
    
    Args:
        text_prompt (str): Text description to search for matching 3D models
        target_path (str, optional): Path where the USD model will be placed in the scene
        position (list, optional): Position coordinates [x, y, z] for placing the model
        scale (list, optional): Scale factors [x, y, z] to resize the model
        
    Returns:
        String with search results including task_id and prim_path of the loaded model
    """
    if not text_prompt:
        return "Error: text_prompt must be provided"
    
    try:
        isaac = get_isaac_connection()
        params = {"text_prompt": text_prompt, 
                  "target_path": target_path}
            
        result = isaac.send_command("search_3d_usd_by_text", params)
        if result.get("status") == "success":
            task_id = result.get("task_id")
            prim_path = result.get("prim_path")
            return f"Successfully found and loaded 3D model with task ID: {task_id}, loaded at prim path: {prim_path}"
        else:
            return f"Error searching 3D model: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error searching 3D model: {str(e)}")
        return f"Error searching 3D model: {str(e)}"

@mcp.tool("odyssey-transform")
def transform(
    ctx: Context,
    prim_path: str,
    position: List[float] = [0, 0, 50],
    scale: List[float] = [10, 10, 10]
) -> str:
    """
    Transform a USD model by applying position and scale.
    
    Args:
        prim_path (str): Path to the USD prim to transform
        position (list, optional): The position to set [x, y, z]
        scale (list, optional): The scale to set [x, y, z]
        
    Returns:
        String with transformation result
    """
    try:
        isaac = get_isaac_connection()
        
        result = isaac.send_command("transform", {
            "prim_path": prim_path,
            "position": position,
            "scale": scale
        })
        
        # Check status at top level
        if result.get("status") == "success":
            return f"Successfully transformed model at {prim_path} to position {position} and scale {scale}"
        else:
            return f"Error transforming model: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error transforming model: {str(e)}")
        return f"Error transforming model: {str(e)}"

@mcp.tool("odyssey-create_material")
def create_material(
    ctx: Context,
    material_path: str,
    material_type: str = "preview_surface",
    diffuse_color: List[float] = None,
    emissive_color: List[float] = None,
    metallic: float = None,
    roughness: float = None,
    opacity: float = None,
    texture_file_path: str = None,
    texture_type: str = "diffuse"
) -> str:
    """Create a material with specified properties or texture in Isaac Sim.
    
    This tool creates materials that can be applied to objects for visual appearance.
    Supports both solid color materials and textured materials.
    
    Args:
        material_path: Path where the material will be created (e.g., "/World/Materials/MyMaterial")
        material_type: Type of material - "preview_surface" (default) or "textured"
        diffuse_color: Diffuse color as [r, g, b] values (0-1 range). Example: [1.0, 0.0, 0.0] for red
        emissive_color: Emissive color as [r, g, b] values (0-1 range) for glowing effects
        metallic: Metallic value (0-1). 0 = non-metallic, 1 = fully metallic
        roughness: Roughness value (0-1). 0 = smooth/shiny, 1 = rough/matte
        opacity: Opacity value (0-1). 0 = transparent, 1 = opaque
        texture_file_path: Path to texture file (for textured materials)
        texture_type: Type of texture - "diffuse", "normal", "roughness", "metallic", "opacity"
        
    Examples:
        # Create a red metallic material:
        create_material("/World/Materials/RedMetal", diffuse_color=[1.0, 0.0, 0.0], metallic=0.8, roughness=0.2)
        
        # Create a glowing material:
        create_material("/World/Materials/GlowingGreen", emissive_color=[0.0, 1.0, 0.0])
        
        # Create a textured material:
        create_material("/World/Materials/WoodTexture", material_type="textured", 
                       texture_file_path="/path/to/wood.jpg", texture_type="diffuse")
    
    Returns:
        String with result information
    """
    params = {
        "material_path": material_path,
        "material_type": material_type
    }
    
    # Add optional parameters
    if material_type == "textured" and texture_file_path:
        params["texture_file_path"] = texture_file_path
        params["texture_type"] = texture_type
    else:
        if diffuse_color is not None:
            params["diffuse_color"] = diffuse_color
        if emissive_color is not None:
            params["emissive_color"] = emissive_color
        if metallic is not None:
            params["metallic"] = metallic
        if roughness is not None:
            params["roughness"] = roughness
        if opacity is not None:
            params["opacity"] = opacity
    
    try:
        isaac = get_isaac_connection()
        result = isaac.send_command("create_material", params)
        
        if result.get("status") == "success":
            return f"Successfully created material at {material_path}"
        else:
            return f"Error creating material: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error creating material: {str(e)}")
        return f"Error creating material: {str(e)}"


@mcp.tool("odyssey-assign_material")
def assign_material(
    ctx: Context,
    prim_path: str,
    material_path: str
) -> str:
    """Assign an existing material to a prim (object) in the scene.
    
    Use this after creating a material to apply it to objects.
    
    Args:
        prim_path: Path to the object to apply the material to (e.g., "/World/Sphere_0")
        material_path: Path to the material to apply (e.g., "/World/Materials/MyMaterial")
        
    Example:
        # First create a material
        create_material("/World/Materials/RedMetal", diffuse_color=[1.0, 0.0, 0.0], metallic=0.8)
        
        # Then assign it to an object
        assign_material("/World/Sphere_0", "/World/Materials/RedMetal")
    
    Returns:
        String with result information
    """
    params = {
        "prim_path": prim_path,
        "material_path": material_path
    }
    
    try:
        isaac = get_isaac_connection()
        result = isaac.send_command("assign_material", params)
        
        if result.get("status") == "success":
            return f"Successfully assigned material {material_path} to {prim_path}"
        else:
            return f"Error assigning material: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error assigning material: {str(e)}")
        return f"Error assigning material: {str(e)}"


@mcp.tool("odyssey-update_material")
def update_material(
    ctx: Context,
    material_path: str,
    diffuse_color: List[float] = None,
    emissive_color: List[float] = None,
    metallic: float = None,
    roughness: float = None,
    opacity: float = None
) -> str:
    """Update properties of an existing material.
    
    Only the properties you specify will be updated, others remain unchanged.
    
    Args:
        material_path: Path to the material to update
        diffuse_color: New diffuse color as [r, g, b] (0-1 range)
        emissive_color: New emissive color as [r, g, b] (0-1 range)
        metallic: New metallic value (0-1)
        roughness: New roughness value (0-1)
        opacity: New opacity value (0-1)
        
    Example:
        # Make an existing material more shiny
        update_material("/World/Materials/MyMaterial", roughness=0.1)
        
        # Change color and make it glow
        update_material("/World/Materials/MyMaterial", 
                       diffuse_color=[0.0, 1.0, 0.0], 
                       emissive_color=[0.0, 0.5, 0.0])
    
    Returns:
        String with result information
    """
    params = {"material_path": material_path}
    
    # Add only the properties that need updating
    if diffuse_color is not None:
        params["diffuse_color"] = diffuse_color
    if emissive_color is not None:
        params["emissive_color"] = emissive_color
    if metallic is not None:
        params["metallic"] = metallic
    if roughness is not None:
        params["roughness"] = roughness
    if opacity is not None:
        params["opacity"] = opacity
    
    try:
        isaac = get_isaac_connection()
        result = isaac.send_command("update_material", params)
        
        if result.get("status") == "success":
            updated_props = result.get("updated", {})
            return f"Successfully updated material {material_path}. Updated properties: {updated_props}"
        else:
            return f"Error updating material: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error updating material: {str(e)}")
        return f"Error updating material: {str(e)}"


@mcp.tool("odyssey-batch_assign_materials")
def batch_assign_materials(
    ctx: Context,
    assignments: List[Dict[str, str]]
) -> str:
    """Assign multiple materials to multiple objects in one operation.
    
    This is much more efficient than calling assign_material multiple times.
    
    Args:
        assignments: List of assignment dictionaries, each containing:
            - prim_path: Path to the object
            - material_path: Path to the material
            
    Example:
        # Assign different materials to multiple spheres
        batch_assign_materials([
            {"prim_path": "/World/Sphere_0", "material_path": "/World/Materials/RedMetal"},
            {"prim_path": "/World/Sphere_1", "material_path": "/World/Materials/BluePlastic"},
            {"prim_path": "/World/Sphere_2", "material_path": "/World/Materials/GreenGlow"}
        ])
    
    Returns:
        String with result information
    """
    params = {"assignments": assignments}
    
    try:
        isaac = get_isaac_connection()
        result = isaac.send_command("batch_assign_materials", params)
        
        if result.get("status") == "success":
            success_count = result.get("success_count", len(assignments))
            failed_count = result.get("failed_count", 0)
            
            if failed_count > 0:
                failed_items = result.get("failed_items", [])
                return (f"Batch material assignment completed with warnings: "
                       f"{success_count} succeeded, {failed_count} failed. "
                       f"Failed: {failed_items[:3]}")
            else:
                return f"Successfully assigned {success_count} materials in batch"
        else:
            return f"Error in batch material assignment: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error in batch material assignment: {str(e)}")
        return f"Error in batch material assignment: {str(e)}"


@mcp.tool("odyssey-create_material_library")
def create_material_library(
    ctx: Context,
    library_name: str = "BasicMaterials"
) -> str:
    """Create a library of commonly used materials.
    
    This creates a set of predefined materials that can be used throughout your scene.
    
    Args:
        library_name: Name of the material library (default: "BasicMaterials")
        
    Available materials in the library:
        - Red, Green, Blue, Yellow, Purple, Orange (basic colors)
        - Metal_Chrome, Metal_Gold, Metal_Copper (metallic materials)
        - Plastic_Shiny, Plastic_Matte (plastic materials)
        - Glass, Water (transparent materials)
        - Glow_White, Glow_Neon (emissive materials)
    
    Example:
        # Create the material library
        create_material_library()
        
        # Then use the materials
        assign_material("/World/Sphere_0", "/World/Materials/BasicMaterials/Metal_Gold")
    
    Returns:
        String with result information
    """
    params = {"library_name": library_name}
    
    try:
        isaac = get_isaac_connection()
        result = isaac.send_command("create_material_library", params)
        
        if result.get("status") == "success":
            materials = result.get("created_materials", [])
            return (f"Successfully created material library '{library_name}' with {len(materials)} materials. "
                   f"Available materials: {', '.join(materials[:10])}")
        else:
            return f"Error creating material library: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error creating material library: {str(e)}")
        return f"Error creating material library: {str(e)}"


# 添加一个材质使用指南的prompt
@mcp.prompt("odyssey-material_workflow")
def material_workflow() -> str:
    """Best practices for working with materials in Isaac Sim"""
    return """
    # Material Creation and Assignment Workflow
    
    ## Quick Start Examples:
    
    ### 1. Create and apply a simple colored material:
    ```python
    # Create a red material
    create_material("/World/Materials/RedPlastic", 
                   diffuse_color=[1.0, 0.0, 0.0], 
                   roughness=0.8)
    
    # Apply it to an object
    assign_material("/World/Sphere_0", "/World/Materials/RedPlastic")
    ```
    
    ### 2. Create metallic materials:
    ```python
    # Chrome-like material
    create_material("/World/Materials/Chrome",
                   diffuse_color=[0.8, 0.8, 0.8],
                   metallic=1.0,
                   roughness=0.1)
    
    # Gold material
    create_material("/World/Materials/Gold",
                   diffuse_color=[1.0, 0.843, 0.0],
                   metallic=1.0,
                   roughness=0.3)
    ```
    
    ### 3. Create glowing materials:
    ```python
    # Neon green glow
    create_material("/World/Materials/NeonGreen",
                   diffuse_color=[0.0, 1.0, 0.0],
                   emissive_color=[0.0, 2.0, 0.0])  # Values > 1 for stronger glow
    ```
    
    ### 4. Create transparent materials:
    ```python
    # Glass-like material
    create_material("/World/Materials/Glass",
                   diffuse_color=[0.9, 0.9, 0.9],
                   opacity=0.3,
                   roughness=0.0)
    ```
    
    ## Material Properties Guide:
    
    - **diffuse_color**: Base color [R, G, B] in 0-1 range
    - **metallic**: 0 = dielectric (plastic, wood), 1 = metal
    - **roughness**: 0 = mirror-like, 1 = completely diffuse
    - **emissive_color**: Makes objects glow (can use values > 1)
    - **opacity**: 0 = transparent, 1 = opaque
    
    ## Best Practices:
    
    1. **Organize materials**: Create materials in a dedicated folder like "/World/Materials/"
    2. **Reuse materials**: Create once, assign to multiple objects
    3. **Batch operations**: Use batch_assign_materials for multiple objects
    4. **Material library**: Use create_material_library() for quick access to common materials
    
    ## Performance Tips:
    
    - Create materials once and reuse them
    - Use batch operations when assigning to many objects
    - Avoid creating duplicate materials with the same properties
    """
# Main execution
def main():
    """Run the MCP server"""
    mcp.run(transport="stdio")
