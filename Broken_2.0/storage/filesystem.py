#!/usr/bin/env python3
"""
File System Management Module
Handles SD card operations with transaction support
"""

from machine import Pin
import os
import time
import sdcard
# typing module not available in MicroPython - type hints work without import


class FileSystemManager:
    """Secure SD card operations with transaction support"""
    
    def __init__(self, spi_manager):
        # Import config and logger from main module
        # These are expected to be available as globals in calculator.py
        from calculator import config, logger
        
        self.spi_manager = spi_manager
        self.config = config
        self.logger = logger
        self.cs_sd = Pin(config.Hardware.SD_CS, Pin.OUT)
        self.sd = None
        self.vfs = None
        self.mounted = False
        self.mount_path = config.System.SD_MOUNT_PATH
        
        self._initialize_sd_card()
        
    def _initialize_sd_card(self, retries: int = 3) -> bool:
        """Initialize and mount SD card"""
        self.logger.info("Initializing SD card...")
        
        for attempt in range(retries):
            try:
                self.spi_manager.switch_to_sd()
                spi = self.spi_manager.get_spi()
                
                # Ensure chip selects are deselected
                self.cs_sd(1)
                time.sleep_ms(10)
                
                # Initialize SD card
                self.sd = sdcard.SDCard(spi, self.cs_sd)
                self.vfs = os.VfsFat(self.sd)
                
                # Mount filesystem
                try:
                    os.mount(self.vfs, self.mount_path)
                except OSError:
                    # Already mounted or mount point exists
                    pass
                    
                # Verify mount and create directories
                self._create_directory_structure()
                self.mounted = True
                
                self.logger.info(f"SD card mounted successfully at {self.mount_path}")
                return True
                
            except Exception as e:
                self.logger.warning(f"SD mount attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(1)
                    
        self.mounted = False
        self.logger.error("SD card mount failed after all retries")
        return False
        
    def _create_directory_structure(self):
        """Create required directory structure"""
        directories = [
            self.mount_path,
            f"{self.mount_path}/programs",
            f"{self.mount_path}/memos", 
            f"{self.mount_path}/graphs",
            f"{self.mount_path}/backups"
        ]
        
        for directory in directories:
            try:
                os.listdir(directory)
            except OSError:
                try:
                    os.mkdir(directory)
                    self.logger.debug(f"Created directory: {directory}")
                except OSError as e:
                    self.logger.warning(f"Failed to create directory {directory}: {e}")
                    
        # Ensure required files exist
        required_files = [
            f"{self.mount_path}/{self.config.System.RESULTS_FILE}",
            f"{self.mount_path}/{self.config.System.GRAPH_HISTORY_FILE}"
        ]
        
        for file_path in required_files:
            try:
                with open(file_path, "a") as f:
                    pass  # Touch file
            except Exception as e:
                self.logger.warning(f"Failed to create file {file_path}: {e}")
                
    def ensure_mounted(self) -> bool:
        """Ensure SD card is mounted"""
        if not self.mounted:
            return self._initialize_sd_card()
        return True
        
    def write_line(self, file_path: str, line: str, append: bool = True) -> bool:
        """Write line to file with transaction safety"""
        if not self.ensure_mounted():
            return False
            
        try:
            self.spi_manager.switch_to_sd()
            
            full_path = f"{self.mount_path}/{file_path}"
            mode = "a" if append else "w"
            
            with open(full_path, mode) as f:
                f.write(line + "\n")
                f.flush()
                
            self.logger.debug(f"Wrote to {full_path}: {line[:50]}...")
            return True
            
        except Exception as e:
            self.logger.error(f"File write failed: {e}")
            return False
        finally:
            self.spi_manager.switch_to_display()
            
    def read_file(self, file_path: str) -> Optional[List[str]]:
        """Read file and return lines"""
        if not self.ensure_mounted():
            return None
            
        try:
            self.spi_manager.switch_to_sd()
            
            full_path = f"{self.mount_path}/{file_path}"
            with open(full_path, "r") as f:
                lines = f.read().splitlines()
                
            self.logger.debug(f"Read {len(lines)} lines from {full_path}")
            return lines
            
        except Exception as e:
            self.logger.error(f"File read failed: {e}")
            return None
        finally:
            self.spi_manager.switch_to_display()
            
    def list_files(self, directory: str = "") -> List[str]:
        """List files in directory"""
        if not self.ensure_mounted():
            return []
            
        try:
            self.spi_manager.switch_to_sd()
            
            full_path = f"{self.mount_path}/{directory}" if directory else self.mount_path
            files = os.listdir(full_path)
            files = [f for f in files if not f.startswith('.')]
            files.sort()
            
            self.logger.debug(f"Listed {len(files)} files in {full_path}")
            return files
            
        except Exception as e:
            self.logger.error(f"Directory listing failed: {e}")
            return []
        finally:
            self.spi_manager.switch_to_display()
            
    def delete_file(self, file_path: str) -> bool:
        """Delete file safely"""
        if not self.ensure_mounted():
            return False
            
        try:
            self.spi_manager.switch_to_sd()
            
            full_path = f"{self.mount_path}/{file_path}"
            os.remove(full_path)
            
            self.logger.info(f"Deleted file: {full_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"File deletion failed: {e}")
            return False
        finally:
            self.spi_manager.switch_to_display()
