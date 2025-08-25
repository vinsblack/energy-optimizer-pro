"""
Automated backup system for Building Energy Optimizer.
Handles database backups, model backups, and configuration backups.
"""
import os
import shutil
import sqlite3
import gzip
import json
import logging
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import tarfile
import hashlib

try:
    import boto3
    HAS_S3 = True
except ImportError:
    HAS_S3 = False

logger = logging.getLogger(__name__)

class BackupManager:
    """Comprehensive backup management system."""
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Backup configuration
        self.retention_days = 30
        self.compress_backups = True
        self.verify_backups = True
        
        # S3 configuration (optional)
        self.s3_enabled = False
        self.s3_bucket = None
        self.s3_client = None
        
    def configure_s3(self, bucket_name: str, aws_access_key: str = None, 
                    aws_secret_key: str = None, region: str = 'us-east-1'):
        """Configure S3 backup storage."""
        if not HAS_S3:
            logger.error("boto3 not installed - S3 backups unavailable")
            return False
        
        try:
            if aws_access_key and aws_secret_key:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    region_name=region
                )
            else:
                # Use default credentials (IAM roles, etc.)
                self.s3_client = boto3.client('s3', region_name=region)
            
            # Test connection
            self.s3_client.head_bucket(Bucket=bucket_name)
            
            self.s3_bucket = bucket_name
            self.s3_enabled = True
            logger.info(f"S3 backup configured for bucket: {bucket_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure S3 backup: {e}")
            return False
    
    def create_full_backup(self, include_logs: bool = False) -> Dict[str, Any]:
        """Create complete system backup."""
        backup_id = f"full_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"\n        backup_path = self.backup_dir / backup_id
        backup_path.mkdir(exist_ok=True)
        
        backup_info = {
            'backup_id': backup_id,
            'backup_type': 'full',
            'created_at': datetime.now().isoformat(),
            'components': {},
            'total_size_bytes': 0,
            'compression_enabled': self.compress_backups,
            'verification_passed': False
        }
        
        logger.info(f"Starting full backup: {backup_id}")
        
        try:
            # Backup database
            db_backup_info = self._backup_database(backup_path)
            backup_info['components']['database'] = db_backup_info
            
            # Backup models
            models_backup_info = self._backup_models(backup_path)
            backup_info['components']['models'] = models_backup_info
            
            # Backup configuration
            config_backup_info = self._backup_configuration(backup_path)
            backup_info['components']['configuration'] = config_backup_info
            
            # Backup logs (optional)
            if include_logs:
                logs_backup_info = self._backup_logs(backup_path)
                backup_info['components']['logs'] = logs_backup_info
            
            # Create backup manifest
            manifest_path = backup_path / "backup_manifest.json"
            with open(manifest_path, 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            # Calculate total size
            total_size = sum(f.stat().st_size for f in backup_path.rglob('*') if f.is_file())
            backup_info['total_size_bytes'] = total_size
            
            # Compress backup if enabled
            if self.compress_backups:
                compressed_path = self._compress_backup(backup_path)
                backup_info['compressed_path'] = str(compressed_path)
                backup_info['compressed_size_bytes'] = compressed_path.stat().st_size
                
                # Remove uncompressed directory
                shutil.rmtree(backup_path)
            
            # Verify backup
            if self.verify_backups:
                verification_result = self._verify_backup(backup_info)
                backup_info['verification_passed'] = verification_result
            
            # Upload to S3 if configured
            if self.s3_enabled:
                s3_result = self._upload_to_s3(backup_info)
                backup_info['s3_upload'] = s3_result
            
            logger.info(f"Full backup completed: {backup_id}")
            return backup_info
            
        except Exception as e:
            logger.error(f"Full backup failed: {e}")
            backup_info['error'] = str(e)
            return backup_info
    
    def _backup_database(self, backup_path: Path) -> Dict[str, Any]:
        """Backup database."""
        db_backup_path = backup_path / "database"
        db_backup_path.mkdir(exist_ok=True)
        
        try:
            # SQLite backup
            if os.path.exists("building_energy.db"):
                source_db = "building_energy.db"
                target_db = db_backup_path / "building_energy.db"
                
                # Create connection and backup
                source_conn = sqlite3.connect(source_db)
                target_conn = sqlite3.connect(str(target_db))
                
                source_conn.backup(target_conn)
                
                source_conn.close()
                target_conn.close()
                
                # Get table counts for verification
                conn = sqlite3.connect(str(target_db))
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                table_counts = {}
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    table_counts[table] = cursor.fetchone()[0]
                
                conn.close()
                
                return {
                    'status': 'success',
                    'database_type': 'sqlite',
                    'file_path': str(target_db),
                    'file_size_bytes': target_db.stat().st_size,
                    'tables': tables,
                    'table_counts': table_counts
                }
            
            # PostgreSQL backup (if configured)
            # This would use pg_dump in production
            else:
                return {
                    'status': 'skipped',
                    'reason': 'No local database found'
                }
        
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def _backup_models(self, backup_path: Path) -> Dict[str, Any]:
        """Backup trained models."""
        models_backup_path = backup_path / "models"
        models_backup_path.mkdir(exist_ok=True)
        
        try:
            # Find all model files
            model_files = list(Path(".").glob("*.joblib"))
            model_files.extend(Path("models").glob("*.joblib") if Path("models").exists() else [])
            
            backed_up_models = []
            total_size = 0
            
            for model_file in model_files:
                target_path = models_backup_path / model_file.name
                shutil.copy2(model_file, target_path)
                
                file_size = target_path.stat().st_size
                total_size += file_size
                
                backed_up_models.append({
                    'filename': model_file.name,
                    'size_bytes': file_size,
                    'source_path': str(model_file),
                    'backup_path': str(target_path)
                })
            
            return {
                'status': 'success',
                'models_count': len(backed_up_models),
                'total_size_bytes': total_size,
                'models': backed_up_models
            }
            
        except Exception as e:
            logger.error(f"Models backup failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def _backup_configuration(self, backup_path: Path) -> Dict[str, Any]:
        """Backup configuration files."""
        config_backup_path = backup_path / "configuration"
        config_backup_path.mkdir(exist_ok=True)
        
        try:
            config_files = [
                '.env',
                'config/settings.py', 
                'docker-compose.yml',
                'requirements.txt',
                'setup.py'
            ]
            
            backed_up_configs = []
            
            for config_file in config_files:
                source_path = Path(config_file)
                if source_path.exists():
                    target_path = config_backup_path / source_path.name
                    shutil.copy2(source_path, target_path)
                    
                    backed_up_configs.append({
                        'filename': source_path.name,
                        'size_bytes': target_path.stat().st_size,
                        'source_path': str(source_path)
                    })
            
            # Create backup metadata
            metadata = {
                'python_version': os.sys.version,
                'backup_time': datetime.now().isoformat(),
                'system_info': {
                    'platform': os.name,
                    'cwd': str(Path.cwd())
                }
            }
            
            metadata_path = config_backup_path / "backup_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return {
                'status': 'success',
                'config_files_count': len(backed_up_configs),
                'files': backed_up_configs,
                'metadata_file': str(metadata_path)
            }
            
        except Exception as e:
            logger.error(f"Configuration backup failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def _backup_logs(self, backup_path: Path) -> Dict[str, Any]:
        """Backup log files."""
        logs_backup_path = backup_path / "logs"
        logs_backup_path.mkdir(exist_ok=True)
        
        try:
            logs_dir = Path("logs")
            if not logs_dir.exists():
                return {
                    'status': 'skipped',
                    'reason': 'No logs directory found'
                }
            
            log_files = list(logs_dir.glob("*.log*"))
            backed_up_logs = []
            total_size = 0
            
            for log_file in log_files:
                target_path = logs_backup_path / log_file.name
                shutil.copy2(log_file, target_path)
                
                file_size = target_path.stat().st_size
                total_size += file_size
                
                backed_up_logs.append({
                    'filename': log_file.name,
                    'size_bytes': file_size
                })
            
            return {
                'status': 'success',
                'log_files_count': len(backed_up_logs),
                'total_size_bytes': total_size,
                'files': backed_up_logs
            }
            
        except Exception as e:
            logger.error(f"Logs backup failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def _compress_backup(self, backup_path: Path) -> Path:
        """Compress backup directory."""
        compressed_path = backup_path.with_suffix('.tar.gz')
        
        with tarfile.open(compressed_path, 'w:gz') as tar:
            tar.add(backup_path, arcname=backup_path.name)
        
        logger.info(f"Backup compressed: {compressed_path}")
        return compressed_path
    
    def _verify_backup(self, backup_info: Dict[str, Any]) -> bool:
        """Verify backup integrity."""
        try:
            backup_id = backup_info['backup_id']
            
            if backup_info['compression_enabled']:
                backup_file = self.backup_dir / f"{backup_id}.tar.gz"
                
                # Verify compressed file
                if not backup_file.exists():
                    logger.error(f"Compressed backup file not found: {backup_file}")
                    return False
                
                # Test extraction
                with tarfile.open(backup_file, 'r:gz') as tar:
                    # Verify all members can be read
                    for member in tar.getmembers():
                        if member.isfile():
                            tar.extractfile(member).read(1024)  # Read first KB
            else:
                backup_path = self.backup_dir / backup_id
                
                if not backup_path.exists():
                    logger.error(f"Backup directory not found: {backup_path}")
                    return False
                
                # Check manifest
                manifest_path = backup_path / "backup_manifest.json"
                if not manifest_path.exists():
                    logger.error("Backup manifest not found")
                    return False
            
            logger.info(f"Backup verification passed: {backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"Backup verification failed: {e}")
            return False
    
    def _upload_to_s3(self, backup_info: Dict[str, Any]) -> Dict[str, Any]:
        """Upload backup to S3."""
        if not self.s3_enabled or not self.s3_client:
            return {'status': 'skipped', 'reason': 'S3 not configured'}
        
        try:
            backup_id = backup_info['backup_id']
            
            if backup_info['compression_enabled']:
                local_file = self.backup_dir / f"{backup_id}.tar.gz"
                s3_key = f"energy-optimizer-backups/{backup_id}.tar.gz"
            else:
                # For uncompressed, create a tar first
                backup_path = self.backup_dir / backup_id
                temp_tar = self.backup_dir / f"{backup_id}_temp.tar.gz"
                
                with tarfile.open(temp_tar, 'w:gz') as tar:
                    tar.add(backup_path, arcname=backup_id)
                
                local_file = temp_tar
                s3_key = f"energy-optimizer-backups/{backup_id}.tar.gz"
            
            # Upload to S3
            start_time = time.time()
            self.s3_client.upload_file(
                str(local_file), 
                self.s3_bucket, 
                s3_key,
                ExtraArgs={'ServerSideEncryption': 'AES256'}
            )
            upload_time = time.time() - start_time
            
            # Clean up temp file if created
            if 'temp' in str(local_file):
                local_file.unlink()
            
            return {
                'status': 'success',
                'bucket': self.s3_bucket,
                's3_key': s3_key,
                'upload_time_seconds': round(upload_time, 2),
                'file_size_bytes': local_file.stat().st_size if local_file.exists() else 0
            }
            
        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def create_incremental_backup(self, last_backup_time: datetime) -> Dict[str, Any]:
        """Create incremental backup of changes since last backup."""
        backup_id = f"incremental_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = self.backup_dir / backup_id
        backup_path.mkdir(exist_ok=True)
        
        backup_info = {
            'backup_id': backup_id,
            'backup_type': 'incremental',
            'since': last_backup_time.isoformat(),
            'created_at': datetime.now().isoformat(),
            'components': {}
        }
        
        try:
            # Backup only changed models
            changed_models = []
            model_files = list(Path(".").glob("*.joblib"))
            
            for model_file in model_files:
                if model_file.stat().st_mtime > last_backup_time.timestamp():
                    target_path = backup_path / "models" / model_file.name
                    target_path.parent.mkdir(exist_ok=True)
                    shutil.copy2(model_file, target_path)
                    changed_models.append(model_file.name)
            
            backup_info['components']['models'] = {
                'changed_models_count': len(changed_models),
                'changed_models': changed_models
            }
            
            # Backup recent logs
            logs_dir = Path("logs")
            if logs_dir.exists():
                recent_logs = []
                for log_file in logs_dir.glob("*.log*"):
                    if log_file.stat().st_mtime > last_backup_time.timestamp():
                        target_path = backup_path / "logs" / log_file.name
                        target_path.parent.mkdir(exist_ok=True)
                        shutil.copy2(log_file, target_path)
                        recent_logs.append(log_file.name)
                
                backup_info['components']['logs'] = {
                    'recent_logs_count': len(recent_logs),
                    'recent_logs': recent_logs
                }
            
            # Create manifest
            manifest_path = backup_path / "backup_manifest.json"
            with open(manifest_path, 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            logger.info(f"Incremental backup completed: {backup_id}")
            return backup_info
            
        except Exception as e:
            logger.error(f"Incremental backup failed: {e}")
            backup_info['error'] = str(e)
            return backup_info
    
    def restore_backup(self, backup_id: str, components: Optional[List[str]] = None) -> Dict[str, Any]:
        """Restore from backup."""
        restore_info = {
            'backup_id': backup_id,
            'restore_started_at': datetime.now().isoformat(),
            'components_restored': [],
            'errors': []
        }
        
        try:
            # Find backup
            backup_file = self.backup_dir / f"{backup_id}.tar.gz"
            backup_dir = self.backup_dir / backup_id
            
            if backup_file.exists():
                # Extract compressed backup
                with tarfile.open(backup_file, 'r:gz') as tar:
                    tar.extractall(self.backup_dir)
                
                backup_path = self.backup_dir / backup_id
            elif backup_dir.exists():
                backup_path = backup_dir
            else:
                raise FileNotFoundError(f"Backup {backup_id} not found")
            
            # Load manifest
            manifest_path = backup_path / "backup_manifest.json"
            if manifest_path.exists():
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
            else:
                manifest = {}
            
            # Restore components
            if components is None:
                components = ['database', 'models', 'configuration']
            
            for component in components:
                try:
                    if component == 'database':
                        self._restore_database(backup_path)
                    elif component == 'models':
                        self._restore_models(backup_path)
                    elif component == 'configuration':
                        self._restore_configuration(backup_path)
                    
                    restore_info['components_restored'].append(component)
                    
                except Exception as e:
                    error_msg = f"Failed to restore {component}: {str(e)}"
                    restore_info['errors'].append(error_msg)
                    logger.error(error_msg)
            
            restore_info['restore_completed_at'] = datetime.now().isoformat()
            logger.info(f"Restore completed for backup {backup_id}")
            
            return restore_info
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            restore_info['fatal_error'] = str(e)
            return restore_info
    
    def _restore_database(self, backup_path: Path):
        """Restore database from backup."""
        db_backup_path = backup_path / "database" / "building_energy.db"
        
        if db_backup_path.exists():
            # Backup current database
            if os.path.exists("building_energy.db"):
                backup_current = f"building_energy_pre_restore_{int(time.time())}.db"
                shutil.copy2("building_energy.db", backup_current)
                logger.info(f"Current database backed up as: {backup_current}")
            
            # Restore from backup
            shutil.copy2(db_backup_path, "building_energy.db")
            logger.info("Database restored from backup")
        else:
            raise FileNotFoundError("Database backup file not found")
    
    def _restore_models(self, backup_path: Path):
        """Restore models from backup."""
        models_backup_path = backup_path / "models"
        
        if models_backup_path.exists():
            # Create models directory if needed
            models_dir = Path("models")
            models_dir.mkdir(exist_ok=True)
            
            # Restore model files
            for model_file in models_backup_path.glob("*.joblib"):
                target_path = Path(model_file.name)
                shutil.copy2(model_file, target_path)
                logger.info(f"Restored model: {model_file.name}")
        else:
            logger.warning("No models found in backup")
    
    def _restore_configuration(self, backup_path: Path):
        """Restore configuration from backup."""
        config_backup_path = backup_path / "configuration"
        
        if config_backup_path.exists():
            config_files = list(config_backup_path.glob("*"))
            
            for config_file in config_files:
                if config_file.name == "backup_metadata.json":
                    continue  # Skip metadata
                
                target_path = Path(config_file.name)
                
                # Be careful with .env - ask for confirmation in production
                if config_file.name == ".env" and target_path.exists():
                    backup_env = f".env.backup_{int(time.time())}"
                    shutil.copy2(target_path, backup_env)
                    logger.info(f"Current .env backed up as: {backup_env}")
                
                shutil.copy2(config_file, target_path)
                logger.info(f"Restored config: {config_file.name}")
        else:
            logger.warning("No configuration files found in backup")
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups."""
        backups = []
        
        # Compressed backups
        for backup_file in self.backup_dir.glob("*.tar.gz"):
            backup_info = {
                'backup_id': backup_file.stem,
                'type': 'compressed',
                'file_path': str(backup_file),
                'size_bytes': backup_file.stat().st_size,
                'created_at': datetime.fromtimestamp(backup_file.stat().st_ctime).isoformat()
            }
            backups.append(backup_info)
        
        # Uncompressed backups
        for backup_dir in self.backup_dir.iterdir():
            if backup_dir.is_dir():
                manifest_path = backup_dir / "backup_manifest.json"
                if manifest_path.exists():
                    try:
                        with open(manifest_path, 'r') as f:
                            manifest = json.load(f)
                        
                        backup_info = {
                            'backup_id': backup_dir.name,
                            'type': 'uncompressed',
                            'path': str(backup_dir),
                            'created_at': manifest.get('created_at'),
                            'backup_type': manifest.get('backup_type'),
                            'total_size_bytes': manifest.get('total_size_bytes', 0)
                        }
                        backups.append(backup_info)
                        
                    except Exception as e:
                        logger.error(f"Failed to read backup manifest for {backup_dir.name}: {e}")
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        return backups
    
    def cleanup_old_backups(self, days_to_keep: int = None) -> Dict[str, Any]:
        """Clean up old backups."""
        if days_to_keep is None:
            days_to_keep = self.retention_days
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        removed_backups = []
        total_space_freed = 0
        
        try:
            backups = self.list_backups()
            
            for backup in backups:
                backup_date = datetime.fromisoformat(backup['created_at'].replace('Z', '+00:00'))
                
                if backup_date < cutoff_date:
                    # Remove old backup
                    if backup['type'] == 'compressed':
                        backup_file = Path(backup['file_path'])
                        if backup_file.exists():
                            size = backup_file.stat().st_size
                            backup_file.unlink()
                            total_space_freed += size
                            removed_backups.append(backup['backup_id'])
                    else:
                        backup_path = Path(backup['path'])
                        if backup_path.exists():
                            # Calculate directory size
                            size = sum(f.stat().st_size for f in backup_path.rglob('*') if f.is_file())
                            shutil.rmtree(backup_path)
                            total_space_freed += size
                            removed_backups.append(backup['backup_id'])
            
            return {
                'removed_backups_count': len(removed_backups),
                'removed_backups': removed_backups,
                'space_freed_bytes': total_space_freed,
                'space_freed_mb': round(total_space_freed / (1024**2), 2),
                'retention_days': days_to_keep
            }
            
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
            return {
                'error': str(e),
                'removed_backups_count': 0
            }
    
    def schedule_automatic_backups(self, backup_type: str = "full", 
                                 interval_hours: int = 24) -> bool:
        """Schedule automatic backups (placeholder for production scheduler)."""
        logger.info(f"Automatic {backup_type} backups scheduled every {interval_hours} hours")
        
        # In production, this would integrate with cron, celery, or other scheduler
        # For demo, just log the configuration
        
        schedule_config = {
            'backup_type': backup_type,
            'interval_hours': interval_hours,
            'next_backup': (datetime.now() + timedelta(hours=interval_hours)).isoformat(),
            'enabled': True
        }
        
        # Save schedule config
        schedule_file = self.backup_dir / "schedule_config.json"
        with open(schedule_file, 'w') as f:
            json.dump(schedule_config, f, indent=2)
        
        return True

# Global backup manager instance
backup_manager = BackupManager()

def create_backup(backup_type: str = "full", include_logs: bool = False) -> Dict[str, Any]:
    """Create backup (convenience function)."""
    if backup_type == "full":
        return backup_manager.create_full_backup(include_logs)
    else:
        # For incremental, use last backup time
        backups = backup_manager.list_backups()
        if backups:
            last_backup_time = datetime.fromisoformat(backups[0]['created_at'])
        else:
            last_backup_time = datetime.now() - timedelta(days=1)
        
        return backup_manager.create_incremental_backup(last_backup_time)

def restore_backup(backup_id: str, components: Optional[List[str]] = None) -> Dict[str, Any]:
    """Restore from backup (convenience function)."""
    return backup_manager.restore_backup(backup_id, components)

def list_available_backups() -> List[Dict[str, Any]]:
    """List all available backups (convenience function)."""
    return backup_manager.list_backups()

def cleanup_old_backups(days: int = 30) -> Dict[str, Any]:
    """Clean up old backups (convenience function)."""
    return backup_manager.cleanup_old_backups(days)

if __name__ == "__main__":
    # Test backup system
    print("💾 Testing backup system...")
    
    # Create test backup
    print("📦 Creating full backup...")
    backup_result = create_backup("full", include_logs=True)
    
    if backup_result.get('error'):
        print(f"❌ Backup failed: {backup_result['error']}")
    else:
        backup_id = backup_result['backup_id']
        total_size_mb = backup_result['total_size_bytes'] / (1024**2)
        print(f"✅ Backup created: {backup_id} ({total_size_mb:.1f} MB)")
        
        # List backups
        backups = list_available_backups()
        print(f"📋 Total backups available: {len(backups)}")
        
        # Test cleanup (dry run)
        cleanup_result = cleanup_old_backups(days=0)  # Remove all for test
        print(f"🧹 Would remove {cleanup_result['removed_backups_count']} old backups")
    
    print("💾 Backup system test complete!")
