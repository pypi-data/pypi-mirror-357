import inquirer
from typing import Optional, List, Tuple, Dict, Any

class PromptManager:
    """Handle user prompts and menu interactions"""
    
    def show_main_menu(self) -> str:
        """Show main menu and get user selection"""
        questions = [
            inquirer.List('choice',
                message='What would you like to do?',
                choices=[
                    ('1. Download Dataset', 'download'),
                    ('2. Format & Structure Dataset', 'format'),
                    ('3. List & View Structured Datasets', 'list_view'),
                    ('4. Start Fine-tuning', 'finetune'),
                    ('5. Run Benchmarks', 'benchmark'),
                    ('6. View Configuration', 'config'),
                    ('7. Exit', 'exit')
                ])
        ]
        answers = inquirer.prompt(questions)
        return answers['choice'] if answers else 'exit'

    def get_dataset_name(self, default: str = 'jacpetro/Jailbreak_Complete_DS_labeled') -> Optional[str]:
        """Get dataset name from user"""
        questions = [
            inquirer.Text(
                'dataset_name',
                message="Enter the dataset name",
                default=default
            )
        ]
        answers = inquirer.prompt(questions)
        return answers['dataset_name'].strip() if answers else None

    def confirm_action(self, message: str, default: bool = True) -> bool:
        """Get confirmation from user"""
        return inquirer.confirm(message=message, default=default)

    def select_dataset(self, datasets: List[Tuple[str, Any]], message: str) -> Optional[Tuple[str, Any]]:
        """Have user select a dataset"""
        if not datasets:
            return None
            
        questions = [
            inquirer.List(
                'dataset',
                message=message,
                choices=datasets
            )
        ]
        answers = inquirer.prompt(questions)
        return answers['dataset'] if answers else None

    def select_benchmark_type(self) -> Optional[str]:
        """Get benchmark type selection"""
        questions = [
            inquirer.List(
                'benchmark_type',
                message="Select benchmark type",
                choices=[
                    ('API Bypass Testing', 'api'),
                    ('Performance Benchmark', 'performance'),
                    ('Comparative Benchmark', 'comparative')
                ]
            )
        ]
        answers = inquirer.prompt(questions)
        return answers['benchmark_type'] if answers else None
