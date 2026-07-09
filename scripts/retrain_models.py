"""
Automated model retraining script.

This script is designed to be run periodically to:
1. Evaluate model performance
2. Detect data drift
3. Trigger retraining when needed
4. Update baseline metrics

Usage:
    python scripts/retrain_models.py [--force] [--model MODEL_NAME] [--notify]
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from models.model_monitor import ModelMonitor, ModelRetrainingPipeline
from utils.logger import get_logger


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Automated model retraining script')
    parser.add_argument('--force', action='store_true',
                       help='Force retrain all models regardless of performance')
    parser.add_argument('--model', type=str,
                       help='Specific model to retrain (if not provided, checks all)')
    parser.add_argument('--notify', action='store_true',
                       help='Send notifications after completion')
    parser.add_argument('--dry-run', action='store_true',
                       help='Check what would be done without actually retraining')
    parser.add_argument('--config', type=str, default='config/model_config.json',
                       help='Path to model configuration file')
    
    return parser.parse_args()


def load_model_config(config_path: str) -> dict:
    """Load model configuration."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception:
        # Default configuration if file doesn't exist
        return {
            "models": [
                "xgb_model_updated",
                "rf_model_updated", 
                "linear_reg_model_updated"
            ],
            "thresholds": {
                "mae_threshold": 500000,
                "rmse_threshold": 1000000,
                "r2_threshold": 0.7,
                "performance_degradation": 0.1
            },
            "notifications": {
                "enabled": True,
                "channels": ["email", "slack"]
            }
        }


def send_notification(results: dict, config: dict):
    """Send notification about retraining results."""
    if not config.get("notifications", {}).get("enabled", False):
        return
    
    logger = get_logger(__name__)
    
    try:
        # Create notification message
        message = f"""
Model Retraining Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Summary:
- Models checked: {len(results.get('models_checked', []))}
- Models retrained: {len(results.get('models_retrained', []))}
- Errors: {len(results.get('errors', []))}

Details:
"""
        
        # Add model check details
        for check in results.get('models_checked', []):
            status = "✅ Good" if not check['should_retrain'] else "⚠️ Needs Retraining"
            message += f"- {check['model_name']}: {status} - {check['reason']}\n"
        
        # Add retraining results
        if results.get('models_retrained'):
            message += "\nRetraining Results:\n"
            for retrain in results['models_retrained']:
                status = "✅ Success" if retrain.get('success') else "❌ Failed"
                message += f"- {retrain['model_name']}: {status}"
                if not retrain.get('success'):
                    message += f" - {retrain.get('error')}"
                message += "\n"
        
        # Add errors
        if results.get('errors'):
            message += "\nErrors:\n"
            for error in results['errors']:
                message += f"- ❌ {error}\n"
        
        logger.info("Notification prepared (actual sending would be implemented based on your notification system)")
        logger.info(f"Notification message:\n{message}")
        
        # TODO: Implement actual notification sending
        # Examples:
        # - Send email using SMTP
        # - Send Slack message using webhook
        # - Send Teams message
        # - Create GitHub issue
        
    except Exception as e:
        logger.error(f"Error sending notification: {e}")


def main():
    """Main function for automated model retraining."""
    args = parse_arguments()
    logger = get_logger(__name__)
    
    logger.info("Starting automated model retraining process")
    logger.info(f"Arguments: {vars(args)}")
    
    try:
        # Load configuration
        config = load_model_config(args.config)
        logger.info(f"Loaded configuration: {config}")
        
        # Initialize pipeline
        pipeline = ModelRetrainingPipeline()
        monitor = ModelMonitor()
        
        # Update thresholds from config
        if 'thresholds' in config:
            monitor.performance_thresholds.update(config['thresholds'])
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'models_checked': [],
            'models_retrained': [],
            'errors': [],
            'dry_run': args.dry_run
        }
        
        # Determine which models to check
        models_to_check = [args.model] if args.model else config.get('models', [])
        
        logger.info(f"Checking models: {models_to_check}")
        
        # Check each model
        for model_name in models_to_check:
            try:
                logger.info(f"Checking model: {model_name}")
                
                # Check if retraining is needed
                should_retrain, reason = pipeline.should_retrain(model_name)
                
                check_result = {
                    'model_name': model_name,
                    'should_retrain': should_retrain,
                    'reason': reason,
                    'forced': args.force
                }
                results['models_checked'].append(check_result)
                
                logger.info(f"{model_name}: {reason}")
                
                # Decide whether to retrain
                if args.force or should_retrain:
                    if args.dry_run:
                        logger.info(f"DRY RUN: Would retrain {model_name}")
                        results['models_retrained'].append({
                            'model_name': model_name,
                            'success': True,
                            'dry_run': True,
                            'reason': 'Would be retrained'
                        })
                    else:
                        logger.info(f"Retraining {model_name}")
                        retrain_result = pipeline.trigger_retraining(model_name)
                        results['models_retrained'].append(retrain_result)
                        
                        if retrain_result.get('success'):
                            logger.info(f"Successfully retrained {model_name}")
                        else:
                            logger.error(f"Failed to retrain {model_name}: {retrain_result.get('error')}")
                
            except Exception as e:
                error_msg = f"Error processing {model_name}: {e}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
        
        # Save results
        results_file = Path('monitoring') / f"retraining_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        results_file.parent.mkdir(exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Results saved to {results_file}")
        
        # Send notification if requested
        if args.notify:
            send_notification(results, config)
        
        # Print summary
        print("\n" + "="*50)
        print("RETRAINING SUMMARY")
        print("="*50)
        print(f"Models checked: {len(results['models_checked'])}")
        print(f"Models retrained: {len(results['models_retrained'])}")
        print(f"Errors: {len(results['errors'])}")
        
        if args.dry_run:
            print("\n⚠️  This was a DRY RUN - no actual retraining was performed")
        
        # Exit with error code if there were errors
        if results['errors']:
            logger.error("Process completed with errors")
            sys.exit(1)
        else:
            logger.info("Process completed successfully")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Fatal error in retraining process: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
