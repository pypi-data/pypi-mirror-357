"""
Dravik CLI Agent
An AI agent that provides a streamlit-based chat interface for interacting with Dravik CLI
"""
import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from pathlib import Path

# Add parent directory to path to allow importing from other Dravik modules
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import Dravik CLI components
from cli.commands.benchmark.command import BenchmarkCommands
from cli.commands.dataset.command import DatasetCommands
from cli.notification.email_service import EmailNotificationService
from cli.dravik_cli import DravikCLI
from db_handler import DravikDB

# Import Rich components for pretty console output
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress
from rich.live import Live

class DravikAgent:
    """Agent for interacting with Dravik CLI through natural language"""
    
    def __init__(self, db=None, api_key=None):
        """Initialize the agent with a database connection"""
        self.db = db
        self.console = Console(width=100)
        self.benchmark_commands = None
        self.dataset_commands = None
        self.running_task = None
        self.task_results = {}
        
        # Try to get API key
        if api_key:
            self.api_key = api_key
        else:
            # Try to get from ApiKeyManager first
            try:
                from utils.api_key_manager import get_api_key_manager
                api_manager = get_api_key_manager()
                self.api_key = api_manager.get_key("gemini")
            except ImportError:
                # Fall back to environment variable
                self.api_key = os.environ.get("GOOGLE_API_KEY")
        
        # Initialize Gemini if API key is available
        self.gemini_enabled = False
        self.gemini_model = None
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                
                # Initialize model - use try/except to handle any initialization errors
                try:
                    self.gemini_model = genai.GenerativeModel('gemini-pro')
                    self.gemini_enabled = True
                    print("Gemini API initialized successfully.")
                except Exception as e:
                    print(f"Error initializing Gemini model: {e}")
            except ImportError:
                print("Gemini API not available (google-generativeai package not installed)")
        else:
            print("No Google API key found, disabling Gemini integration")
        
        # Initialize components if DB is available
        if self.db:
            try:
                self.benchmark_commands = BenchmarkCommands(db=self.db, config={})
                self.dataset_commands = DatasetCommands(db=self.db)
            except Exception as e:
                print(f"Error initializing commands: {str(e)}")
    
    def handle_message(self, message: str) -> Dict[str, Any]:
        """
        Process a user message and determine the appropriate action
        
        Args:
            message: The user's message
            
        Returns:
            Dict with response and any action details
        """
        # Always try to use Gemini for intent recognition first
        if self.gemini_enabled and self.gemini_model:
            try:
                return self._handle_with_gemini(message)
            except Exception as e:
                print(f"Error using Gemini for intent recognition: {str(e)}")
                # Only disable Gemini for persistent critical errors
                if "not found" in str(e) or "not supported" in str(e):
                    self.gemini_enabled = False
                    print("Gemini API encountered a critical error. Disabling Gemini integration.")
        
        # Create a more detailed response for fallback case
        return {
            "type": "text",
            "content": "I'm having trouble understanding your request. Please try rephrasing or provide more details about what you'd like to do with Dravik CLI. You can run static or conversation red teaming benchmarks, manage custom models, view results, or configure scheduled benchmarks."
        }
    
    def _handle_with_gemini(self, message: str) -> Dict[str, Any]:
        """
        Process a user message using Gemini AI for intent recognition
        
        Args:
            message: The user's message
            
        Returns:
            Dict with response and any action details
        """
        try:
            # Import here to ensure it's only used when needed
            import google.generativeai as genai
            import re
            
            # Define the system prompt with context about available intents and CLI flows
            system_prompt = """
            You are an NLP intent classifier for the Dravik CLI application. Your job is to understand user requests and map them to the appropriate CLI actions. The Dravik CLI offers these main features:

            1. Perform Red Teaming - Benchmark models with adversarial prompts
               - Select models (OpenAI, Gemini, or custom models)
               - Choose prompt generation method (static or markov)
               - Set number of prompts
               - View and save results

            2. Conversation Red Teaming - Test models in dialogue settings
               - Select models 
               - Choose attack vectors (jailbreak, harmful content, personal info, illegal activity, hate speech)
               - Set number of conversation attempts
               - View and save results

            3. Custom Model Management
               - Register new models (currently supports Ollama models)
               - List existing custom models
               - Delete custom models

            4. Results Management
               - View benchmark results (filter by type)
               - View detailed result information
               - Export results

            5. Scheduled Benchmarks
               - Configure scheduled benchmarks
               - List scheduled benchmarks
               - Delete scheduled benchmarks

            Analyze the user message and identify the primary intent with these categories:
            - static_red_teaming: Messages about static benchmarking, adversarial prompts
            - conversation_red_teaming: Messages about conversation testing, dialogue testing
            - custom_model: Messages about registering, listing or deleting models
            - results: Messages about viewing, analyzing, or exporting benchmark results
            - scheduled: Messages about scheduled benchmarks (configuring, listing, deleting)
            - help: Messages asking for help or information

            For each intent, extract as many parameters as possible. For example:
            
            For static_red_teaming, look for:
            - models: List of model names mentioned (e.g., "GPT-4", "Gemini Pro", "Claude") 
            - dataset_source: Where to get datasets from ("internal" or "public")
            - dataset_type: Type of dataset ("static" or "from existing")
            - num_prompts: Number of prompts to generate (any number mentioned)
            - generation_method: Generation method ("jailbreak", "static", "markov")
            
            For conversation_red_teaming, look for:
            - models: List of model names mentioned
            - attack_vectors: Types of attacks mentioned ("jailbreak", "harmful_content", "personal_information", "illegal_activity", "hate_speech")
            - num_attempts: Number of conversation attempts (any number mentioned)
            
            For view_results, look for:
            - result_type: Type of results to view ("static", "conversation", "all")
            - format: Export format if mentioned ("csv", "json", "excel")
            
            For custom_model operations, look for:
            - operation: What to do with models ("register", "list", "delete")
            - model_name: Name of the model, if mentioned
            - model_type: Type of model, if mentioned ("openai", "gemini", "ollama")
            
            Respond with a JSON object including the intent and all detected parameters. Add a field called "skip_wizard" with value true if you have enough parameters to proceed directly without asking the user for more information.
            
            Example:
            {
                "intent": "static_red_teaming",
                "parameters": {
                    "models": ["gpt-4", "gemini-pro"],
                    "num_prompts": 30,
                    "generation_method": "jailbreak"
                },
                "skip_wizard": true
            }
            """
            
            # Prepare the chat history with system prompt
            chat = self.gemini_model.start_chat(history=[
                {"role": "user", "parts": [system_prompt]},
                {"role": "model", "parts": ["I'll classify the user intent and return a JSON object with the intent and parameters."]}
            ])
            
            # Send the user message to Gemini
            response = chat.send_message(f"User message: {message}")
            response_text = response.text
            
            # Extract the JSON part from the response
            json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
            if json_match:
                json_string = json_match.group(1)
            else:
                # Try to find a JSON object without markdown formatting
                json_match = re.search(r'({.*})', response_text, re.DOTALL)
                if json_match:
                    json_string = json_match.group(1)
                else:
                    # Assume the entire response is a JSON string
                    json_string = response_text
            
            try:
                intent_data = json.loads(json_string)
            except json.JSONDecodeError:
                print(f"Error parsing Gemini response as JSON: {response_text}")
                # Attempt to parse it again with a more lenient approach
                try:
                    # Try to extract any JSON-like content
                    pattern = r'(\{[^{}]*\})'
                    matches = re.findall(pattern, response_text)
                    if matches:
                        intent_data = json.loads(matches[0])
                    else:
                        raise ValueError("No valid JSON found")
                except:
                    # If all parsing fails, make a best guess based on the text
                    intent_data = self._extract_intent_from_text(response_text)
            
            # Process the intent data
            intent = intent_data.get("intent", "unknown")
            parameters = intent_data.get("parameters", {})
            skip_wizard = intent_data.get("skip_wizard", False)
            
            # Map Gemini intent to specific handlers with parameters
            if intent in ["static_red_teaming", "static", "benchmark"]:
                result = self._handle_red_teaming_intent(message, parameters, skip_wizard)
                result["parameters"] = parameters
                return result
            elif intent in ["conversation_red_teaming", "conversation", "chat", "dialogue"]:
                result = self._handle_conversation_intent(message, parameters, skip_wizard)
                result["parameters"] = parameters
                return result
            elif intent in ["results", "view_results", "view", "export_results"]:
                result = self._handle_results_intent(message, parameters, skip_wizard)
                result["parameters"] = parameters
                return result
            elif intent in ["custom_model", "register_model", "model", "models"]:
                result = self._handle_custom_model_intent(message, parameters, skip_wizard)
                result["parameters"] = parameters
                return result
            elif intent in ["scheduled", "scheduled_benchmark"]:
                result = self._handle_scheduled_intent(message, parameters, skip_wizard)
                result["parameters"] = parameters
                return result
            elif intent in ["help", "information", "assistance"]:
                return self._provide_help()
            else:
                # Use Gemini to generate a helpful response for unrecognized intents
                clarification_prompt = f"""
                The user said: "{message}"
                
                I couldn't determine a specific action to take. Please generate a helpful response asking for clarification
                about what they want to do with Dravik CLI. Mention the main features (red teaming, model management, results viewing)
                and ask them to provide more details about what they'd like to do.
                Keep it brief and direct.
                """
                
                clarification = self.gemini_model.generate_content(clarification_prompt)
                return {
                    "type": "text",
                    "content": clarification.text
                }
                
        except Exception as e:
            print(f"Error using Gemini for intent recognition: {str(e)}")
            # Provide a helpful error message
            return {
                "type": "text",
                "content": "I'm having trouble understanding your request. Please try rephrasing or provide more details about what you'd like to do with Dravik CLI. You can run static or conversation red teaming benchmarks, manage custom models, view results, or configure scheduled benchmarks."
            }
    
    def _extract_intent_from_text(self, text: str) -> Dict[str, Any]:
        """Extract intent from text when JSON parsing fails"""
        text = text.lower()
        
        # Look for keywords to determine intent
        if any(word in text for word in ["static", "benchmark", "adversarial", "prompt"]):
            return {"intent": "static_red_teaming"}
        elif any(word in text for word in ["conversation", "chat", "dialogue"]):
            return {"intent": "conversation_red_teaming"}
        elif any(word in text for word in ["result", "view", "export"]):
            return {"intent": "results"}
        elif any(word in text for word in ["model", "register", "custom"]):
            return {"intent": "custom_model"}
        elif any(word in text for word in ["schedule", "scheduled"]):
            return {"intent": "scheduled"}
        elif any(word in text for word in ["help", "info", "information"]):
            return {"intent": "help"}
        else:
            return {"intent": "unknown"}
    
    def _handle_red_teaming_intent(self, message: str, parameters: Dict[str, Any], skip_wizard: bool) -> Dict[str, Any]:
        """Handle static red teaming intent"""
        # If we have sufficient parameters and skip_wizard is true, directly prepare for benchmark
        models = parameters.get("models", [])
        num_prompts = parameters.get("num_prompts", 20)
        generation_method = parameters.get("generation_method", "jailbreak")
        dataset_source = parameters.get("dataset_source", "internal")
        dataset_type = parameters.get("dataset_type", "static")
        
        # Check if we have models specified and can skip the wizard
        if skip_wizard and models:
            # Prepare a direct benchmark run with parameters from NLP
            normalized_models = []
            for model in models:
                if isinstance(model, str):
                    model = model.lower()
                    # Add provider prefix if needed
                    if ":" not in model:
                        if model.startswith("gpt"):
                            model = f"openai:{model}"
                        elif model.startswith("gemini"):
                            model = f"gemini:{model}"
                        elif model.startswith("claude"):
                            model = f"anthropic:{model}"
                        else:
                            model = f"custom:{model}"
                    normalized_models.append(model)
            
            # Set up response with detected parameters
            response_content = f"Starting static red teaming benchmark with:\n\n"
            response_content += f"- Models: {', '.join(normalized_models)}\n"
            response_content += f"- Dataset source: {dataset_source}\n"
            response_content += f"- Dataset type: {dataset_type}\n"
            response_content += f"- Number of prompts: {num_prompts}\n"
            response_content += f"- Generation method: {generation_method}"
            
            return {
                "type": "red_teaming_static",
                "content": response_content,
                "models": normalized_models,
                "num_prompts": num_prompts,
                "generation_method": generation_method,
                "dataset_source": dataset_source,
                "dataset_type": dataset_type,
                "skip_wizard": True
            }
        
        # Use Gemini to determine if the message is about static or conversation red teaming
        if self.gemini_enabled and self.gemini_model:
            try:
                prompt = f"""
                Analyze this user message and determine if they're asking about static red teaming or conversation red teaming:
                "{message}"
                
                Respond with just one of these exact options:
                1. static
                2. conversation
                3. unclear
                """
                
                response = self.gemini_model.generate_content(prompt)
                choice = response.text.strip().lower()
                
                if "static" in choice:
                    return {
                        "type": "red_teaming_static",
                        "content": "I'll help you set up a static red teaming benchmark. Let's configure this together.",
                        "next_step": "select_models"
                    }
                elif "conversation" in choice:
                    return {
                        "type": "red_teaming_conversation",
                        "content": "I'll help you set up a conversation red teaming benchmark. Let's configure this together.",
                        "next_step": "select_models"
                    }
            except:
                # Fall through to keyword matching if Gemini fails
                pass
        
        # Fallback to keyword matching
        if "static" in message.lower() or "benchmark" in message.lower():
            return {
                "type": "red_teaming_static",
                "content": "I'll help you set up a static red teaming benchmark. Let's configure this together.",
                "next_step": "select_models"
            }
        elif "conversation" in message.lower() or "chat" in message.lower():
            return {
                "type": "red_teaming_conversation",
                "content": "I'll help you set up a conversation red teaming benchmark. Let's configure this together.",
                "next_step": "select_models"
            }
        else:
            return {
                "type": "clarification",
                "content": "Would you like to run a red teaming benchmark or a conversation red teaming benchmark?",
                "options": ["Static Red Teaming", "Conversation Red Teaming"]
            }
    
    def _handle_conversation_intent(self, message: str, parameters: Dict[str, Any], skip_wizard: bool) -> Dict[str, Any]:
        """Handle conversation red teaming intent"""
        # If we have sufficient parameters and skip_wizard is true, directly prepare for benchmark
        models = parameters.get("models", [])
        attack_vectors = parameters.get("attack_vectors", ["jailbreak"])
        num_attempts = parameters.get("num_attempts", 3)
        
        # Check if we have models specified and can skip the wizard
        if skip_wizard and models:
            # Prepare a direct benchmark run with parameters from NLP
            normalized_models = []
            for model in models:
                if isinstance(model, str):
                    model = model.lower()
                    # Add provider prefix if needed
                    if ":" not in model:
                        if model.startswith("gpt"):
                            model = f"openai:{model}"
                        elif model.startswith("gemini"):
                            model = f"gemini:{model}"
                        elif model.startswith("claude"):
                            model = f"anthropic:{model}"
                        else:
                            model = f"custom:{model}"
                    normalized_models.append(model)
            
            # Normalize attack vectors
            normalized_attack_vectors = []
            for vector in attack_vectors:
                if isinstance(vector, str):
                    vector = vector.lower()
                    if vector in ["jailbreak", "harmful_content", "personal_information", "illegal_activity", "hate_speech"]:
                        normalized_attack_vectors.append(vector)
            
            if not normalized_attack_vectors:
                normalized_attack_vectors = ["jailbreak"]
                
            # Set up response with detected parameters
            response_content = f"Starting conversation red teaming benchmark with:\n\n"
            response_content += f"- Models: {', '.join(normalized_models)}\n"
            response_content += f"- Attack vectors: {', '.join(normalized_attack_vectors)}\n"
            response_content += f"- Attempts per model: {num_attempts}"
            
            return {
                "type": "red_teaming_conversation",
                "content": response_content,
                "models": normalized_models,
                "attack_vectors": normalized_attack_vectors,
                "num_attempts": num_attempts,
                "skip_wizard": True
            }
        
        # Default wizard flow
        return {
            "type": "red_teaming_conversation",
            "content": "I'll help you set up a conversation red teaming benchmark. Let's configure this together.",
            "next_step": "select_models"
        }
    
    def _handle_results_intent(self, message: str, parameters: Dict[str, Any], skip_wizard: bool) -> Dict[str, Any]:
        """Handle results viewing intent"""
        return {
            "type": "view_results",
            "content": "I'll help you view benchmark results. Would you like to see all results or filter by a specific type?",
            "options": ["All Results", "Static Red Teaming Results", "Conversation Red Teaming Results", "Export Results"]
        }
    
    def _handle_custom_model_intent(self, message: str, parameters: Dict[str, Any], skip_wizard: bool) -> Dict[str, Any]:
        """Handle custom model management intent"""
        # Use Gemini to determine what action to take with custom models
        if self.gemini_enabled and self.gemini_model:
            try:
                prompt = f"""
                Analyze this user message about custom models:
                "{message}"
                
                Determine what specifically they want to do with custom models. Respond with just one of these exact options:
                1. register (if they want to add a new model)
                2. list (if they want to see existing models)
                3. delete (if they want to remove a model)
                4. unclear (if it's not specific)
                """
                
                response = self.gemini_model.generate_content(prompt)
                choice = response.text.strip().lower()
                
                if "register" in choice:
                    return {
                        "type": "register_model",
                        "content": "I'll help you register a custom model. What type of model would you like to register?",
                        "options": ["Ollama Model", "Custom API Model"]
                    }
                elif "list" in choice:
                    return {
                        "type": "list_models",
                        "content": "I'll show you the list of registered custom models.",
                        "action": "list_custom_models"
                    }
                elif "delete" in choice:
                    return {
                        "type": "delete_model",
                        "content": "I'll help you delete a custom model. Which model would you like to remove?",
                        "action": "prepare_delete_model"
                    }
            except:
                # Fall through to keyword matching if Gemini fails
                pass
        
        # Fallback to keyword matching
        if "register" in message.lower() or "add" in message.lower() or "new" in message.lower():
            return {
                "type": "register_model",
                "content": "I'll help you register a custom model. What type of model would you like to register?",
                "options": ["Ollama Model", "Custom API Model"]
            }
        elif "list" in message.lower() or "view" in message.lower() or "show" in message.lower():
            return {
                "type": "list_models",
                "content": "I'll show you the list of registered custom models.",
                "action": "list_custom_models"
            }
        elif "delete" in message.lower() or "remove" in message.lower():
            return {
                "type": "delete_model",
                "content": "I'll help you delete a custom model. Which model would you like to remove?",
                "action": "prepare_delete_model"
            }
        else:
            return {
                "type": "clarification",
                "content": "What would you like to do with custom models?",
                "options": ["Register a new model", "List registered models", "Delete a model"]
            }
    
    def _handle_scheduled_intent(self, message: str, parameters: Dict[str, Any], skip_wizard: bool) -> Dict[str, Any]:
        """Handle scheduled benchmarks intent"""
        if "configure" in message.lower() or "create" in message.lower() or "add" in message.lower() or "new" in message.lower():
            return {
                "type": "configure_scheduled",
                "content": "I'll help you configure a scheduled benchmark. Let's set this up together.",
                "next_step": "select_models"
            }
        elif "list" in message.lower() or "view" in message.lower() or "show" in message.lower():
            return {
                "type": "list_scheduled",
                "content": "I'll show you the list of scheduled benchmarks.",
                "action": "list_scheduled_benchmarks"
            }
        elif "delete" in message.lower() or "remove" in message.lower():
            return {
                "type": "delete_scheduled",
                "content": "I'll help you delete a scheduled benchmark. Which one would you like to remove?",
                "action": "prepare_delete_scheduled"
            }
        else:
            return {
                "type": "clarification",
                "content": "What would you like to do with scheduled benchmarks?",
                "options": ["Configure a new scheduled benchmark", "List scheduled benchmarks", "Delete a scheduled benchmark"]
            }
    
    def _provide_help(self) -> Dict[str, Any]:
        """Provide help information"""
        return {
            "type": "help",
            "content": """
            I'm an agent for the Dravik CLI. Here's what I can help you with:
            
            1. **Red Teaming** - Run static or conversation-based red teaming benchmarks
            2. **View Results** - View and analyze benchmark results
            3. **Custom Models** - Register, list, or delete custom models
            4. **Scheduled Benchmarks** - Configure, list, or delete scheduled benchmarks
            
            Just tell me what you'd like to do, and I'll guide you through the process!
            """
        }
    
    def run_static_red_teaming(self, models, generation_method, prompt_count):
        """
        Run a static red teaming benchmark
        
        Args:
            models: List of models to benchmark
            generation_method: Method for generating prompts (static or markov)
            prompt_count: Number of prompts to generate
            
        Returns:
            Benchmark results
        """
        try:
            # Prepare the dataset based on generation method
            if generation_method == "static":
                # Use advanced templates with markov generation
                try:
                    from benchmarks.templates.markov_jailbreak_generator import generate_diverse_adversarial_prompts
                    
                    # Generate diverse prompts
                    diverse_prompts_data = generate_diverse_adversarial_prompts(count=prompt_count)
                    
                    # Create the dataset structure
                    dataset = {
                        "name": "Advanced Adversarial Templates with Markov Generation",
                        "description": "Dynamic adversarial prompts generated using Markov chains and advanced jailbreak templates",
                        "examples": [],
                        "metadata": {
                            "generation_method": "markov",
                            "generation_time": datetime.now().isoformat(),
                            "count": len(diverse_prompts_data)
                        }
                    }
                    
                    # Process the generated prompts
                    for i, prompt_data in enumerate(diverse_prompts_data):
                        dataset["examples"].append({
                            "id": f"advanced_prompt_{i+1}",
                            "prompt": prompt_data["prompt"],
                            "technique": prompt_data["technique"],
                            "adversarial_technique": prompt_data["technique"],
                            "base_goal": prompt_data["base_goal"],
                            "category": "general",
                            "harmful_goal": "general"
                        })
                except Exception as e:
                    # Fallback to advanced templates directly
                    from benchmarks.templates.advanced_jailbreak_templates import generate_adversarial_prompts
                    prompts = generate_adversarial_prompts(count=prompt_count)
                    dataset = {
                        "name": "Advanced Templates",
                        "description": "Standard advanced templates",
                        "examples": [{"prompt": p, "technique": "advanced"} for p in prompts],
                        "metadata": {
                            "generation_method": "advanced_templates",
                            "generation_time": datetime.now().isoformat(),
                            "count": len(prompts)
                        }
                    }
            else:  # markov
                dataset = self.benchmark_commands._generate_markov_templates(
                    prompt_count=prompt_count,
                    use_gemini_augmentation=True  # Use augmentation for agent requests
                )
            
            # Use the provided models directly instead of prompting for selection
            # Configure the benchmark
            config = {
                "models": models,
                "dataset": dataset
            }
            
            # Run the benchmark (overriding the default model selection)
            print(f"Starting red teaming benchmark with models: {models}")
            results = self.benchmark_commands._run_api_benchmark(config=config, dataset=dataset, provided_models=models)
            return results
        except Exception as e:
            error_message = f"Error running static red teaming: {str(e)}"
            print(error_message)
            return {"error": error_message}
    
    def run_conversation_red_teaming(self, models, attack_vectors, num_attempts):
        """
        Run a conversation red teaming benchmark with the specified parameters
        
        Args:
            models: List of models to benchmark
            attack_vectors: List of attack vectors to test
            num_attempts: Number of conversation attempts per model
            
        Returns:
            Benchmark results
        """
        try:
            # Configure the attack
            attack_config = {
                "attack_vectors": attack_vectors,
                "num_attempts": num_attempts,
                "use_cache": True,
                "timestamp": datetime.now().isoformat()
            }
            
            # Run the benchmark
            results = self.benchmark_commands.run_conversation_red_teaming(models, attack_config)
            return results
        except Exception as e:
            error_message = f"Error running conversation red teaming: {str(e)}"
            print(error_message)
            return {"error": error_message}
    
    def get_benchmark_results(self, result_type=None):
        """
        Get benchmark results optionally filtered by type
        
        Args:
            result_type: Optional type to filter results
            
        Returns:
            List of benchmark results
        """
        try:
            results = self.benchmark_commands._get_available_benchmark_results()
            
            if result_type and results:
                # Filter results by type
                if result_type == "static":
                    results = [r for r in results if r.get("type") == "benchmark"]
                elif result_type == "conversation":
                    results = [r for r in results if r.get("type") == "conversation_redteam"]
                
            return results
        except Exception as e:
            error_message = f"Error getting benchmark results: {str(e)}"
            print(error_message)
            return {"error": error_message}
    
    def register_ollama_model(self, model_name, ollama_model_id, ollama_url="http://localhost:11434"):
        """
        Register an Ollama model
        
        Args:
            model_name: Name for the custom model
            ollama_model_id: ID of the Ollama model
            ollama_url: URL of the Ollama API
            
        Returns:
            Result of the registration
        """
        try:
            config = {
                "type": "ollama",
                "model_id": ollama_model_id,
                "base_url": ollama_url
            }
            
            from benchmarks.models.model_loader import ModelLoader
            model_loader = ModelLoader()
            model_loader.register_custom_model(model_name, config)
            
            return {"success": True, "message": f"Successfully registered Ollama model '{model_name}'"}
        except Exception as e:
            error_message = f"Error registering Ollama model: {str(e)}"
            print(error_message)
            return {"error": error_message}
    
    def list_custom_models(self):
        """
        List registered custom models
        
        Returns:
            Dictionary of custom models or error message
        """
        try:
            from benchmarks.models.model_loader import ModelLoader
            model_loader = ModelLoader()
            # Get the list of custom model names
            custom_model_names = model_loader.list_custom_models()
            
            # If we got a list of model names, convert it to a dictionary by loading each config
            if isinstance(custom_model_names, list):
                custom_models_dict = {}
                for model_name in custom_model_names:
                    config = model_loader.get_custom_model_config(model_name)
                    if config:
                        custom_models_dict[model_name] = config
                    else:
                        # If we can't get config, at least include the name
                        custom_models_dict[model_name] = {"type": "unknown", "name": model_name}
                return custom_models_dict
            
            # Otherwise just return what we got (which should be a dict)
            return custom_model_names
        except Exception as e:
            error_message = f"Error listing custom models: {str(e)}"
            print(error_message)
            return {"error": error_message}
    
    def delete_custom_model(self, model_name):
        """
        Delete a custom model
        
        Args:
            model_name: Name of the model to delete
            
        Returns:
            Result of the deletion
        """
        try:
            from benchmarks.models.model_loader import ModelLoader
            model_loader = ModelLoader()
            success = model_loader.delete_custom_model(model_name)
            
            if success:
                return {"success": True, "message": f"Successfully deleted model '{model_name}'"}
            else:
                return {"error": f"Failed to delete model '{model_name}'"}
        except Exception as e:
            error_message = f"Error deleting custom model: {str(e)}"
            print(error_message)
            return {"error": error_message}
            
    def generate_task_steps(self, task_description):
        """
        Use Gemini to generate a plan for completing a complex task
        
        Args:
            task_description: Description of the task to plan
            
        Returns:
            List of steps to complete the task
        """
        if not self.gemini_enabled or not self.gemini_model:
            return {
                "success": False,
                "message": "Gemini AI is not available. Please configure a valid API key."
            }
            
        try:
            # Import here to ensure it's only used when needed
            import google.generativeai as genai
            import re
            
            prompt = f"""
            You are planning the steps for completing the following task in the Dravik CLI:
            
            TASK: {task_description}
            
            Based on what you know about the Dravik CLI capabilities, break this down into actionable steps.
            Focus on these capabilities:
            - Running static red teaming benchmarks
            - Running conversation red teaming benchmarks
            - Viewing and analyzing benchmark results
            - Managing custom models (registering, listing, deleting)
            - Configuring scheduled benchmarks
            
            Provide a JSON array of steps with the following structure:
            [
                {{
                    "step": "Step 1 description",
                    "action": "The specific action to take (e.g., 'run_static_red_teaming')",
                    "parameters": {{
                        "param1": "value1",
                        "param2": "value2"
                    }}
                }},
                ...
            ]
            """
            
            response = self.gemini_model.generate_content(prompt)
            response_text = response.text
            
            # Extract the JSON part from the response
            json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
            if json_match:
                json_string = json_match.group(1)
            else:
                # Try to find a JSON array without markdown formatting
                json_match = re.search(r'(\[.*\])', response_text, re.DOTALL)
                if json_match:
                    json_string = json_match.group(1)
                else:
                    # Assume the entire response is a JSON string
                    json_string = response_text
            
            try:
                steps = json.loads(json_string)
                return {
                    "success": True,
                    "steps": steps
                }
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "message": f"Could not parse task steps from Gemini response."
                }
                
        except Exception as e:
            error_message = f"Error generating task steps with Gemini: {str(e)}"
            print(error_message)
            return {
                "success": False,
                "message": error_message
            }
