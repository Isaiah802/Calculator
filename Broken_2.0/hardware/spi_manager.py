#!/usr/bin/env python3
"""
SPIManager - Thread-safe SPI bus management

Part of the Hardware Abstraction Layer for Peanut 3000 Calculator.
Manages SPI bus switching between display and SD card modes.
"""

from machine import Pin, SPI
import time


class SPIManager:
    """Thread-safe SPI bus management"""
    
    def __init__(self, config, logger, HardwareError):
        self.config = config
        self.logger = logger
        self.HardwareError = HardwareError
        
        self.spi = SPI(
            self.config.Hardware.SPI_BUS, 
            baudrate=self.config.Hardware.SPI_BAUDRATE_DISPLAY,
            polarity=0, 
            phase=0,
            sck=Pin(self.config.Hardware.SPI_SCK),
            mosi=Pin(self.config.Hardware.SPI_MOSI),
            miso=Pin(self.config.Hardware.SPI_MISO)
        )
        self.current_mode = 'display'
        
    def switch_to_display(self):
        """Switch SPI bus to display mode"""
        if self.current_mode != 'display':
            try:
                self.spi.init(
                    baudrate=self.config.Hardware.SPI_BAUDRATE_DISPLAY,
                    polarity=0, phase=0
                )
                self.current_mode = 'display'
                self.logger.debug("SPI switched to display mode")
            except Exception as e:
                self.logger.error(f"Failed to switch SPI to display: {e}")
                raise self.HardwareError(f"SPI display switch failed: {e}")
                
    def switch_to_sd(self):
        """Switch SPI bus to SD card mode"""
        if self.current_mode != 'sd':
            try:
                self.spi.init(
                    baudrate=self.config.Hardware.SPI_BAUDRATE_SD,
                    polarity=0, phase=0
                )
                self.current_mode = 'sd'
                self.logger.debug("SPI switched to SD card mode")
            except Exception as e:
                self.logger.error(f"Failed to switch SPI to SD: {e}")
                raise self.HardwareError(f"SPI SD switch failed: {e}")
                
    def get_spi(self) -> SPI:
        """Get SPI bus instance"""
        return self.spi
