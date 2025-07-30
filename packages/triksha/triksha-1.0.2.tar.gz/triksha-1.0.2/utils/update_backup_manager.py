
# Update backup manager to use absolute paths for benchmark results
import os
from pathlib import Path

def update_backup_manager():
    backup_manager_path = Path("/home/ubuntu/revert/dravik/benchmarks/utils/backup_manager.py")
    
    if not backup_manager_path.exists():
        print(f"Backup manager not found at {backup_manager_path}")
        return False
        
    with open(backup_manager_path, 'r') as f:
        content = f.read()
    
    # Check if already using absolute paths
    if 'Path("/home/ubuntu/revert/dravik/benchmark_results")' in content:
        print("Backup manager already using absolute paths!")
        return True
        
    # Replace relative path with absolute
    modified_content = content.replace(
        'benchmark_dir = Path("benchmark_results")',
        'benchmark_dir = Path("/home/ubuntu/revert/dravik/benchmark_results")'
    )
    
    # Add path creation if not present
    if "benchmark_dir.mkdir(exist_ok=True, parents=True)" not in content:
        modified_content = modified_content.replace(
            'benchmark_dir = Path("/home/ubuntu/revert/dravik/benchmark_results")',
            'benchmark_dir = Path("/home/ubuntu/revert/dravik/benchmark_results")\n        benchmark_dir.mkdir(exist_ok=True, parents=True)'
        )
    
    # Write back the changes
    with open(backup_manager_path, 'w') as f:
        f.write(modified_content)
        
    print(f"Updated {backup_manager_path} to use absolute paths")
    return True

if __name__ == "__main__":
    update_backup_manager()
