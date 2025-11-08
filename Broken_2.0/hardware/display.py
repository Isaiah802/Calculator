#!/usr/bin/env python3
"""
DisplayManager - ILI9341 display control with framebuffer

Part of the Hardware Abstraction Layer for Peanut 3000 Calculator.
Manages ILI9341 display initialization, framebuffer, and drawing operations.
"""

from machine import Pin
import framebuf
import time
import gc


class DisplayManager:
    """Hardware display interface with buffering and optimization"""
    
    def __init__(self, spi_manager, config, logger, HardwareError):
        self.spi_manager = spi_manager
        self.config = config
        self.logger = logger
        self.HardwareError = HardwareError
        
        self.width = self.config.Hardware.DISPLAY_WIDTH
        self.height = self.config.Hardware.DISPLAY_HEIGHT
        
        # Control pins
        self.cs = Pin(self.config.Hardware.DISPLAY_CS, Pin.OUT)
        self.dc = Pin(self.config.Hardware.DISPLAY_DC, Pin.OUT)
        self.rst = Pin(self.config.Hardware.DISPLAY_RST, Pin.OUT)
        
        # Frame buffer - allocate with a graceful fallback if memory is low
        try:
            # give the GC a chance before allocating the big buffer
            try:
                gc.collect()
            except Exception:
                pass
            self.buffer = bytearray(self.width * self.height * 2)
            self.fb = framebuf.FrameBuffer(
                self.buffer,
                self.width,
                self.height,
                framebuf.RGB565
            )
            self.reduced_resolution = False
        except MemoryError:
            # Try a reduced-resolution fallback (half size) to conserve RAM
            self.logger.warning("Low memory: falling back to reduced display buffer")
            try:
                self.width = max(160, self.width // 2)
                self.height = max(120, self.height // 2)
                self.buffer = bytearray(self.width * self.height * 2)
                self.fb = framebuf.FrameBuffer(
                    self.buffer,
                    self.width,
                    self.height,
                    framebuf.RGB565
                )
                self.reduced_resolution = True
            except Exception as e:
                # As a last resort, disable framebuffer and operate in a minimal mode
                self.logger.error(f"Unable to allocate framebuffer: {e}")
                self.buffer = None
                self.fb = None
                self.reduced_resolution = True
        
        # State tracking
        self.dirty = True
        self.last_update = 0
        
        self._initialize_display()
        
    def _initialize_display(self):
        """Initialize the ILI9341 display"""
        self.logger.info("Initializing display...")
        try:
            # Reset sequence
            self.rst.value(0)
            time.sleep_ms(50)
            self.rst.value(1)
            time.sleep_ms(120)
            
            # Initialization commands
            self._send_command(0x01)  # Software reset
            time.sleep_ms(150)
            self._send_command(0x11)  # Sleep out
            time.sleep_ms(500)
            self._send_command(0x3A, b'\x55')  # Pixel format 16-bit
            self._send_command(0x36, b'\x28')  # Memory access control
            self._send_command(0x29)  # Display on
            time.sleep_ms(100)
            
            self.logger.info("Display initialization complete")
            
        except Exception as e:
            self.logger.error(f"Display initialization failed: {e}")
            raise self.HardwareError(f"Display init failed: {e}")
            
    def _send_command(self, cmd: int, data: bytes = None):
        """Send command to display"""
        self.spi_manager.switch_to_display()
        spi = self.spi_manager.get_spi()
        
        # Send command
        self.dc.value(0)
        self.cs.value(0)
        spi.write(bytes([cmd]))
        self.cs.value(1)
        
        # Send data if provided
        if data:
            self.dc.value(1)
            self.cs.value(0)
            spi.write(data)
            self.cs.value(1)
            
    def _set_window(self, x0: int, y0: int, x1: int, y1: int):
        """Set drawing window"""
        self._send_command(0x2A, bytes([x0>>8, x0&255, x1>>8, x1&255]))
        self._send_command(0x2B, bytes([y0>>8, y0&255, y1>>8, y1&255]))
        self._send_command(0x2C)
        
    def clear(self, color: int = None):
        """Clear display with color"""
        if color is None:
            color = self.config.UI.BACKGROUND
        self.fb.fill(color)
        self.dirty = True
        
    def show(self, force: bool = False):
        """Update display if dirty or forced"""
        if not (self.dirty or force):
            return
            
        try:
            self._set_window(0, 0, self.width - 1, self.height - 1)

            # Send framebuffer data
            self.spi_manager.switch_to_display()
            spi = self.spi_manager.get_spi()

            self.dc.value(1)
            self.cs.value(0)
            spi.write(self.buffer)
            self.cs.value(1)
            
            self.dirty = False
            self.last_update = time.ticks_ms()
            
        except Exception as e:
            self.logger.error(f"Display update failed: {e}")
            # Continue operation even if display update fails
            
    def draw_text(self, x: int, y: int, text: str, color: int = None):
        """Draw text with bounds checking"""
        if color is None:
            color = self.config.UI.FOREGROUND
            
        # Bounds checking
        text_str = str(text)
        if x >= 0 and y >= 0 and x < self.width and y < self.height:
            self.fb.text(text_str, x, y, color)
            self.dirty = True
            
    def draw_rect(self, x: int, y: int, w: int, h: int, color: int):
        """Draw rectangle outline"""
        self.fb.rect(x, y, w, h, color)
        self.dirty = True
        
    def fill_rect(self, x: int, y: int, w: int, h: int, color: int):
        """Draw filled rectangle"""
        self.fb.fill_rect(x, y, w, h, color)
        self.dirty = True
        
    def draw_pixel(self, x: int, y: int, color: int):
        """Draw single pixel"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.fb.pixel(x, y, color)
            self.dirty = True
            
    def draw_line(self, x0: int, y0: int, x1: int, y1: int, color: int):
        """Draw line between two points"""
        self.fb.line(x0, y0, x1, y1, color)
        self.dirty = True
        
    def draw_hline(self, x: int, y: int, w: int, color: int):
        """Draw horizontal line"""
        self.fb.hline(x, y, w, color)
        self.dirty = True
        
    def draw_vline(self, x: int, y: int, h: int, color: int):
        """Draw vertical line"""
        self.fb.vline(x, y, h, color)
        self.dirty = True
