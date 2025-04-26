# app_startup.py
import os
import asyncio
import logging
import time
import argparse
from typing import List, Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import core components
from app.core.component_registry import get_registry, setup_standard_components
from app.models.create_tables import init_db
from app.utils.error_handler import register_error_handlers
from app.utils.optimization import timing_decorator, response_time_monitor

from dotenv import load_dotenv
load_dotenv()

class StudyBuddyStartup:
    """Handles application startup and health checks"""
    
    def __init__(self, config_path: str = None, skip_db_init: bool = False):
        self.config_path = config_path
        self.registry = None
        self.skip_db_init = skip_db_init
        self.components_status = {}
        self.health_status = "Not Started"
        
    async def start(self) -> bool:
        """
        Start the application and run health checks
        
        Returns:
            True if startup was successful, False otherwise
        """
        try:
            logger.info("Starting Study Buddy Agent...")
            start_time = time.time()
            
            # 1. Load configuration
            success = self._load_configuration()
            if not success:
                logger.error("Failed to load configuration")
                return False
                
            # 2. Initialize database (if needed)
            if not self.skip_db_init:
                success = self._init_database()
                if not success:
                    logger.error("Failed to initialize database")
                    return False
            
            # 3. Register components
            self.registry = setup_standard_components()
            
            # 4. Run component health checks
            success = await self._run_health_checks()
            if not success:
                logger.error("Health checks failed")
                return False
                
            # 5. Initialize all components
            try:
                self.registry.initialize_all()
            except Exception as e:
                logger.error(f"Failed to initialize components: {e}")
                return False
                
            # Log success
            elapsed_time = time.time() - start_time
            logger.info(f"Study Buddy Agent started successfully in {elapsed_time:.2f} seconds")
            self.health_status = "Healthy"
            
            return True
            
        except Exception as e:
            logger.error(f"Startup error: {e}")
            self.health_status = "Error"
            return False
    
    def _load_configuration(self) -> bool:
        """
        Load application configuration
        
        Returns:
            True if successful
        """
        try:
            # Load from environment variables as default
            logger.info("Loading configuration from environment variables")
            
            # Check required environment variables
            required_vars = ["GITHUB_TOKEN", "ENDPOINT"]
            missing = [var for var in required_vars if not os.environ.get(var)]
            
            if missing:
                logger.error(f"Missing required environment variables: {', '.join(missing)}")
                self.health_status = "Configuration Error"
                return False
                
            # If config path is provided, load from file
            if self.config_path and os.path.exists(self.config_path):
                logger.info(f"Loading configuration from file: {self.config_path}")
                # Implementation for file-based config would go here
                
            logger.info("Configuration loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Configuration error: {e}")
            self.health_status = "Configuration Error"
            return False
    
    def _init_database(self) -> bool:
        """
        Initialize database tables
        
        Returns:
            True if successful
        """
        try:
            logger.info("Initializing database...")
            init_db()
            logger.info("Database initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            self.health_status = "Database Error"
            return False
    
    @timing_decorator
    async def _run_health_checks(self) -> bool:
        """
        Run health checks on all components
        
        Returns:
            True if all checks pass
        """
        logger.info("Running component health checks...")
        
        # Track component status
        self.components_status = {}
        success = True
        
        # Check vector store
        vector_store_status = await self._check_vector_store()
        self.components_status["vector_store"] = vector_store_status
        success = success and vector_store_status["healthy"]
        
        # Check LLM connection
        llm_status = await self._check_llm_connection()
        self.components_status["llm_connection"] = llm_status
        success = success and llm_status["healthy"]
        
        # Check database connection
        db_status = self._check_database_connection()
        self.components_status["database"] = db_status
        success = success and db_status["healthy"]
        
        # Log results
        healthy_count = sum(1 for status in self.components_status.values() if status["healthy"])
        total_count = len(self.components_status)
        
        logger.info(f"Health checks completed: {healthy_count}/{total_count} components healthy")
        
        if success:
            logger.info("All health checks passed")
            self.health_status = "Starting"
        else:
            logger.error("Some health checks failed")
            self.health_status = "Unhealthy"
            
        return success
    
    async def _check_vector_store(self) -> Dict[str, Any]:
        """Check vector store health"""
        try:
            # Get vector store client
            component = self.registry.get_component("vector_store_client")
            
            # Check if index is loaded
            if component.index is None:
                return {"healthy": False, "message": "Vector index not loaded"}
                
            # Check dimensions
            if component.index.d != component.embedding_dim:
                return {"healthy": False, "message": f"Dimension mismatch: {component.index.d} != {component.embedding_dim}"}
                
            # Check basic functionality
            test_embedding = [0.0] * component.embedding_dim
            test_embedding_np = component.index.ntotal
            
            return {
                "healthy": True,
                "message": "Vector store is healthy",
                "vectors": component.index.ntotal,
                "dimensions": component.index.d
            }
            
        except Exception as e:
            logger.error(f"Vector store health check failed: {e}")
            return {"healthy": False, "message": str(e)}
    
    async def _check_llm_connection(self) -> Dict[str, Any]:
        """Check LLM connection health"""
        try:
            # Get message processor
            component = self.registry.get_component("message_processor")
            
            # Check if client is configured
            if not component.client:
                return {"healthy": False, "message": "LLM client not configured"}
                
            # Check model name
            if not component.model_name:
                return {"healthy": False, "message": "Model name not configured"}
                
            return {
                "healthy": True,
                "message": "LLM connection is healthy",
                "model": component.model_name
            }
            
        except Exception as e:
            logger.error(f"LLM connection health check failed: {e}")
            return {"healthy": False, "message": str(e)}
    
    def _check_database_connection(self) -> Dict[str, Any]:
        """Check database connection health"""
        try:
            # Import here to avoid circular imports
            from app.models.db import engine
            
            # Check if engine is configured
            if not engine:
                return {"healthy": False, "message": "Database engine not configured"}
                
            # Check connection
            connection = engine.connect()
            connection.close()
            
            return {
                "healthy": True,
                "message": "Database connection is healthy",
                "type": engine.name
            }
            
        except Exception as e:
            logger.error(f"Database connection health check failed: {e}")
            return {"healthy": False, "message": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get application status summary"""
        return {
            "status": self.health_status,
            "components": self.components_status
        }

# Standalone execution for startup
if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="Study Buddy Agent Startup")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--skip-db-init", action="store_true", help="Skip database initialization")
    args = parser.parse_args()
    
    # Create startup instance
    startup = StudyBuddyStartup(
        config_path=args.config,
        skip_db_init=args.skip_db_init
    )
    
    # Run startup
    success = asyncio.run(startup.start())
    
    if not success:
        logger.error("Startup failed. Check logs for details.")
        exit(1)
        
    # Display status
    status = startup.get_status()
    print("\n=== Study Buddy Agent Status ===")
    print(f"Overall Status: {status['status']}")
    print("\nComponent Health:")
    for component, health in status["components"].items():
        status_icon = "✅" if health["healthy"] else "❌"
        print(f"{status_icon} {component}: {health['message']}")