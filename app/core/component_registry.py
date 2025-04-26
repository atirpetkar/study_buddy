# app/core/component_registry.py
from typing import Dict, Any, Optional, Type, Callable
import inspect
import importlib
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComponentRegistry:
    """
    Registry for all Study Buddy components to ensure proper integration
    and dependency management.
    """
    
    def __init__(self):
        self.components = {}
        self.factories = {}
        self.initialized = False
        
    def register_component(self, name: str, component: Any) -> None:
        """
        Register a component in the registry
        
        Args:
            name: Unique name for the component
            component: The component instance
        """
        if name in self.components:
            logger.warning(f"Component '{name}' already registered, overwriting.")
            
        self.components[name] = component
        logger.info(f"Component '{name}' registered successfully.")
        
    def register_factory(self, name: str, factory: Callable) -> None:
        """
        Register a factory function for lazy component initialization
        
        Args:
            name: Unique name for the component
            factory: Factory function that returns a component instance
        """
        self.factories[name] = factory
        logger.info(f"Factory for component '{name}' registered.")
        
    def get_component(self, name: str) -> Any:
        """
        Get a component from the registry, initializing it if necessary
        
        Args:
            name: Name of the component to retrieve
            
        Returns:
            The component instance
        """
        # Check if already initialized
        if name in self.components:
            return self.components[name]
            
        # Check if we have a factory for it
        if name in self.factories:
            logger.info(f"Initializing component '{name}'")
            component = self.factories[name]()
            self.components[name] = component
            return component
            
        raise KeyError(f"Component '{name}' not found in registry.")
        
    def initialize_all(self) -> None:
        """Initialize all registered components using their factories"""
        if self.initialized:
            logger.warning("Components already initialized.")
            return
            
        for name, factory in self.factories.items():
            if name not in self.components:
                logger.info(f"Initializing component '{name}'")
                self.components[name] = factory()
                
        self.initialized = True
        logger.info(f"All components initialized. Total: {len(self.components)}")
        
    def reset(self) -> None:
        """Reset the registry, clearing all components"""
        self.components = {}
        self.initialized = False
        logger.info("Component registry reset.")
        
    def get_dependency_graph(self) -> Dict[str, Any]:
        """
        Build a dependency graph of all registered components
        
        Returns:
            Dictionary representing component dependencies
        """
        graph = {}
        
        for name, component in self.components.items():
            dependencies = []
            
            # Inspect the component to find dependencies
            if hasattr(component, "__init__"):
                try:
                    # Get init signature
                    sig = inspect.signature(component.__class__.__init__)
                    for param_name, param in sig.parameters.items():
                        if param_name not in ["self", "args", "kwargs"]:
                            dependencies.append(param_name)
                except (ValueError, TypeError):
                    pass
                    
            graph[name] = {
                "component": component.__class__.__name__,
                "dependencies": dependencies
            }
            
        return graph

# Create singleton instance
_registry = ComponentRegistry()

def get_registry() -> ComponentRegistry:
    """Get the singleton component registry"""
    return _registry

# Function to set up standard components
def setup_standard_components():
    """Register standard Study Buddy components with the registry"""
    registry = get_registry()
    
    # Register vector store
    registry.register_factory("vector_store_client", lambda: importlib.import_module("app.core.vector_store").get_vector_store_client())
    
    # Register message processor
    registry.register_factory("message_processor", lambda: importlib.import_module("app.core.agent").get_message_processor())
    
    # Register quiz generator
    registry.register_factory("quiz_generator", lambda: importlib.import_module("app.core.quiz_generator").QuizGenerator())
    
    # Register flashcard generator
    registry.register_factory("flashcard_generator", lambda: importlib.import_module("app.core.flashcard_generator").FlashcardGenerator())
    
    # Register personalization engine
    registry.register_factory("personalization_engine", lambda: importlib.import_module("app.core.personalization_engine").PersonalizationEngine())
    
    # Register tutor
    registry.register_factory("tutoring_manager", lambda: importlib.import_module("app.core.tutoring").TutoringSessionManager())
    
    # Register study planner
    registry.register_factory("study_planner", lambda: importlib.import_module("app.core.study_planner").StudyPlanGenerator())
    
    # Register advanced study planner
    registry.register_factory("advanced_study_planner", lambda: importlib.import_module("app.core.advanced_study_planner").AdvancedStudyPlanGenerator())
    
    # Register spaced repetition scheduler
    registry.register_factory("spaced_repetition", lambda: importlib.import_module("app.core.spaced_repetition").SpacedRepetitionScheduler())
    
    # Register optimization tools
    registry.register_factory("embedding_cache", lambda: importlib.import_module("app.utils.optimization").embedding_cache)
    registry.register_factory("results_deduplicator", lambda: importlib.import_module("app.utils.optimization").results_deduplicator)
    registry.register_factory("response_time_monitor", lambda: importlib.import_module("app.utils.optimization").response_time_monitor)
    
    logger.info("Standard components registered successfully.")
    
    return registry