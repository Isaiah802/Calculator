#!/usr/bin/env python3
"""
================================================================================
💻 PC COMPANION APPLICATION - PEANUT 3000 DESKTOP CLIENT
================================================================================
Desktop companion application for enhanced Peanut 3000 calculator functionality
- Real-time calculation display mirroring
- Large screen graphing and visualization  
- File synchronization and backup
- Settings configuration interface
- Advanced mathematical input methods

Part of Phase 3: PC Connectivity & External Interface
Author: Peanut 3000 Development Team
Version: 2.0.0
Date: November 6, 2025

Requirements: pip install tkinter matplotlib numpy pyserial
================================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import serial
import serial.tools.list_ports
import json
import struct
import time
import threading
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import queue
from pathlib import Path
import math

# ================= CONSTANTS & CONFIGURATION =================
class PCConfig:
    """PC companion application configuration"""
    
    # Window Settings
    WINDOW_TITLE = "Peanut 3000 - PC Companion"
    WINDOW_SIZE = "1200x800"
    MIN_WINDOW_SIZE = (800, 600)
    
    # Serial Communication
    BAUDRATE = 115200
    TIMEOUT = 1.0
    RECONNECT_INTERVAL = 5.0
    
    # Protocol Settings
    MAGIC_HEADER = b"PN30"
    PROTOCOL_VERSION = "1.0"
    
    # UI Settings
    GRAPH_UPDATE_INTERVAL = 100  # ms
    STATUS_UPDATE_INTERVAL = 1000  # ms
    MAX_CALC_HISTORY = 100
    
    # Colors
    COLORS = {
        'bg': '#2B2B2B',
        'fg': '#FFFFFF',
        'accent': '#4CAF50',
        'warning': '#FF9800',
        'error': '#F44336',
        'info': '#2196F3'
    }

class MessageType(Enum):
    """Message types matching calculator protocol"""
    HEARTBEAT = 0x01
    CALCULATION = 0x02
    GRAPH_DATA = 0x03
    FILE_TRANSFER = 0x04
    SETTINGS = 0x05
    FIRMWARE = 0x06
    ERROR = 0xFF

# ================= SERIAL COMMUNICATION MANAGER =================
class SerialManager:
    """Manages serial communication with Peanut 3000"""
    
    def __init__(self):
        self.connection = None
        self.connected = False
        self.port = None
        self.rx_queue = queue.Queue()
        self.tx_queue = queue.Queue()
        self.running = False
        self.thread = None
        
    def scan_ports(self) -> List[str]:
        """Scan for available serial ports"""
        ports = []
        for port_info in serial.tools.list_ports.comports():
            ports.append(port_info.device)
        return ports
        
    def connect(self, port: str) -> bool:
        """Connect to specified serial port"""
        try:
            if self.connection:
                self.disconnect()
                
            self.connection = serial.Serial(
                port, 
                PCConfig.BAUDRATE, 
                timeout=PCConfig.TIMEOUT
            )
            
            self.port = port
            self.connected = True
            self.running = True
            
            # Start communication thread
            self.thread = threading.Thread(target=self._communication_loop, daemon=True)
            self.thread.start()
            
            print(f"Connected to Peanut 3000 on {port}")
            return True
            
        except Exception as e:
            print(f"Connection failed: {e}")
            self.connected = False
            return False
            
    def disconnect(self):
        """Disconnect from serial port"""
        self.running = False
        self.connected = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
            
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
            self.connection = None
            
        print("Disconnected from Peanut 3000")
        
    def _communication_loop(self):
        """Main communication loop (runs in separate thread)"""
        while self.running and self.connected:
            try:
                # Send queued messages
                while not self.tx_queue.empty():
                    try:
                        message = self.tx_queue.get_nowait()
                        self.connection.write(message)
                    except queue.Empty:
                        break
                        
                # Receive messages
                if self.connection.in_waiting > 0:
                    data = self.connection.read(self.connection.in_waiting)
                    self._process_received_data(data)
                    
                time.sleep(0.01)  # Small delay to prevent excessive CPU usage
                
            except Exception as e:
                print(f"Communication error: {e}")
                self.connected = False
                break
                
    def _process_received_data(self, data: bytes):
        """Process received data and parse packets"""
        # Simple packet parsing (would need proper buffering for production)
        if len(data) >= 8 and data[:4] == PCConfig.MAGIC_HEADER:
            try:
                msg_type = MessageType(data[4])
                data_len = struct.unpack('<H', data[5:7])[0]
                
                if len(data) >= 8 + data_len + 1:
                    payload = data[8:8+data_len]
                    
                    # Parse JSON payload
                    json_data = json.loads(payload.decode('utf-8'))
                    
                    # Add to receive queue
                    self.rx_queue.put((msg_type, json_data))
                    
            except Exception as e:
                print(f"Packet parsing error: {e}")
                
    def send_message(self, msg_type: MessageType, data: Dict[str, Any]) -> bool:
        """Send message to calculator"""
        if not self.connected:
            return False
            
        try:
            # Create packet
            json_data = json.dumps(data).encode('utf-8')
            packet = bytearray()
            packet.extend(PCConfig.MAGIC_HEADER)
            packet.append(msg_type.value)
            packet.extend(struct.pack('<H', len(json_data)))
            packet.extend(struct.pack('<L', int(time.time() * 1000)))  # Timestamp
            packet.extend(json_data)
            
            # Simple checksum
            checksum = sum(packet) & 0xFF
            packet.append(checksum)
            
            # Add to transmit queue
            self.tx_queue.put(bytes(packet))
            return True
            
        except Exception as e:
            print(f"Send message error: {e}")
            return False
            
    def get_message(self) -> Optional[Tuple[MessageType, Dict[str, Any]]]:
        """Get received message from queue"""
        try:
            return self.rx_queue.get_nowait()
        except queue.Empty:
            return None

# ================= CALCULATION DISPLAY WIDGET =================
class CalculationDisplay(ttk.Frame):
    """Display for real-time calculations"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        self.calculation_history = []
        
    def setup_ui(self):
        """Setup calculation display UI"""
        # Title
        title_label = ttk.Label(self, text="📱 Calculator Display", font=('Arial', 14, 'bold'))
        title_label.pack(pady=5)
        
        # Current calculation frame
        current_frame = ttk.LabelFrame(self, text="Current Calculation", padding=10)
        current_frame.pack(fill='x', padx=5, pady=5)
        
        # Expression display
        self.expression_var = tk.StringVar(value="Ready...")
        expression_label = ttk.Label(current_frame, text="Expression:")
        expression_label.pack(anchor='w')
        
        self.expression_display = ttk.Label(
            current_frame, 
            textvariable=self.expression_var,
            font=('Consolas', 12),
            background='white',
            relief='sunken',
            padding=5
        )
        self.expression_display.pack(fill='x', pady=2)
        
        # Result display
        self.result_var = tk.StringVar(value="")
        result_label = ttk.Label(current_frame, text="Result:")
        result_label.pack(anchor='w', pady=(10,0))
        
        self.result_display = ttk.Label(
            current_frame,
            textvariable=self.result_var,
            font=('Consolas', 14, 'bold'),
            background='lightgreen',
            relief='sunken',
            padding=5
        )
        self.result_display.pack(fill='x', pady=2)
        
        # History frame
        history_frame = ttk.LabelFrame(self, text="Calculation History", padding=10)
        history_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # History listbox with scrollbar
        list_frame = ttk.Frame(history_frame)
        list_frame.pack(fill='both', expand=True)
        
        self.history_listbox = tk.Listbox(
            list_frame,
            font=('Consolas', 10),
            selectmode='single'
        )
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.history_listbox.yview)
        self.history_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.history_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Buttons frame
        button_frame = ttk.Frame(history_frame)
        button_frame.pack(fill='x', pady=(10,0))
        
        ttk.Button(button_frame, text="Clear History", command=self.clear_history).pack(side='left')
        ttk.Button(button_frame, text="Export History", command=self.export_history).pack(side='left', padx=(5,0))
        
    def update_calculation(self, expression: str, result: str):
        """Update current calculation display"""
        self.expression_var.set(expression)
        self.result_var.set(result)
        
        # Add to history
        timestamp = time.strftime("%H:%M:%S")
        history_entry = f"[{timestamp}] {expression} = {result}"
        self.calculation_history.append(history_entry)
        
        # Update history listbox
        self.history_listbox.insert(tk.END, history_entry)
        self.history_listbox.see(tk.END)  # Scroll to bottom
        
        # Limit history size
        if len(self.calculation_history) > PCConfig.MAX_CALC_HISTORY:
            self.calculation_history.pop(0)
            self.history_listbox.delete(0)
            
    def clear_history(self):
        """Clear calculation history"""
        self.calculation_history.clear()
        self.history_listbox.delete(0, tk.END)
        
    def export_history(self):
        """Export calculation history to file"""
        if not self.calculation_history:
            messagebox.showwarning("Warning", "No calculation history to export")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write("Peanut 3000 Calculation History\n")
                    f.write("=" * 40 + "\n\n")
                    for entry in self.calculation_history:
                        f.write(entry + "\n")
                        
                messagebox.showinfo("Success", f"History exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export history: {e}")

# ================= GRAPH DISPLAY WIDGET =================
class GraphDisplay(ttk.Frame):
    """Advanced graph display with matplotlib"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        self.current_expression = ""
        self.plot_data = {'x': [], 'y': []}
        self.setup_matplotlib()
        
    def setup_ui(self):
        """Setup graph display UI"""
        # Title
        title_label = ttk.Label(self, text="📊 Advanced Graphing", font=('Arial', 14, 'bold'))
        title_label.pack(pady=5)
        
        # Controls frame
        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill='x', padx=5, pady=5)
        
        # Expression entry
        ttk.Label(controls_frame, text="Function:").pack(side='left')
        self.expression_var = tk.StringVar(value="sin(x)")
        self.expression_entry = ttk.Entry(
            controls_frame, 
            textvariable=self.expression_var,
            font=('Consolas', 10),
            width=30
        )
        self.expression_entry.pack(side='left', padx=(5,10))
        
        # Buttons
        ttk.Button(controls_frame, text="Plot", command=self.plot_function).pack(side='left', padx=2)
        ttk.Button(controls_frame, text="Clear", command=self.clear_plot).pack(side='left', padx=2)
        ttk.Button(controls_frame, text="Export", command=self.export_plot).pack(side='left', padx=2)
        
    def setup_matplotlib(self):
        """Setup matplotlib figure and canvas"""
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(8, 6), dpi=100)
        self.ax.set_title("Function Graph")
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("y")
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5)
        
        # Navigation toolbar
        toolbar_frame = ttk.Frame(self)
        toolbar_frame.pack(fill='x', padx=5)
        
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()
        
    def update_graph(self, expression: str, points: List[Tuple[float, float]]):
        """Update graph with new data from calculator"""
        self.current_expression = expression
        
        if points:
            x_data = [p[0] for p in points]
            y_data = [p[1] for p in points]
            
            self.plot_data = {'x': x_data, 'y': y_data}
            
            # Update plot
            self.ax.clear()
            self.ax.plot(x_data, y_data, 'b-', linewidth=2, label=f'y = {expression}')
            self.ax.set_title(f"Graph: y = {expression}")
            self.ax.grid(True, alpha=0.3)
            self.ax.set_xlabel("x")
            self.ax.set_ylabel("y")
            self.ax.legend()
            
            self.canvas.draw()
            
    def plot_function(self):
        """Plot function locally (for testing)"""
        expression = self.expression_var.get()
        
        try:
            # Generate test data
            x = np.linspace(-10, 10, 1000)
            
            # Simple expression evaluation (replace with safer method in production)
            y = eval(expression.replace('sin', 'np.sin')
                              .replace('cos', 'np.cos')
                              .replace('tan', 'np.tan')
                              .replace('log', 'np.log')
                              .replace('sqrt', 'np.sqrt')
                              .replace('^', '**')
                              .replace('x', 'x'))
            
            # Update plot
            self.ax.clear()
            self.ax.plot(x, y, 'b-', linewidth=2, label=f'y = {expression}')
            self.ax.set_title(f"Graph: y = {expression}")
            self.ax.grid(True, alpha=0.3)
            self.ax.set_xlabel("x")
            self.ax.set_ylabel("y")
            self.ax.legend()
            
            # Set reasonable axis limits
            self.ax.set_xlim(-10, 10)
            if np.isfinite(y).any():
                y_finite = y[np.isfinite(y)]
                if len(y_finite) > 0:
                    y_range = np.max(y_finite) - np.min(y_finite)
                    y_center = (np.max(y_finite) + np.min(y_finite)) / 2
                    self.ax.set_ylim(y_center - y_range/2*1.1, y_center + y_range/2*1.1)
            
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to plot function: {e}")
            
    def clear_plot(self):
        """Clear the plot"""
        self.ax.clear()
        self.ax.set_title("Function Graph")
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlabel("x")
        self.ax.set_ylabel("y")
        self.canvas.draw()
        
    def export_plot(self):
        """Export plot to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("PDF files", "*.pdf"),
                ("SVG files", "*.svg"),
                ("All files", "*.*")
            ]
        )
        
        if filename:
            try:
                self.fig.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Success", f"Plot exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export plot: {e}")

# ================= SETTINGS PANEL =================
class SettingsPanel(ttk.Frame):
    """Settings and configuration panel"""
    
    def __init__(self, parent, serial_manager):
        super().__init__(parent)
        self.serial_manager = serial_manager
        self.setup_ui()
        
    def setup_ui(self):
        """Setup settings panel UI"""
        # Title
        title_label = ttk.Label(self, text="⚙️ Settings & Configuration", font=('Arial', 14, 'bold'))
        title_label.pack(pady=5)
        
        # Connection settings
        conn_frame = ttk.LabelFrame(self, text="Connection Settings", padding=10)
        conn_frame.pack(fill='x', padx=5, pady=5)
        
        # Port selection
        port_frame = ttk.Frame(conn_frame)
        port_frame.pack(fill='x', pady=2)
        
        ttk.Label(port_frame, text="Serial Port:").pack(side='left')
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(port_frame, textvariable=self.port_var, width=15)
        self.port_combo.pack(side='left', padx=(5,10))
        
        ttk.Button(port_frame, text="Refresh", command=self.refresh_ports).pack(side='left', padx=2)
        ttk.Button(port_frame, text="Connect", command=self.connect).pack(side='left', padx=2)
        ttk.Button(port_frame, text="Disconnect", command=self.disconnect).pack(side='left', padx=2)
        
        # Connection status
        self.status_var = tk.StringVar(value="Disconnected")
        status_label = ttk.Label(conn_frame, textvariable=self.status_var, foreground='red')
        status_label.pack(anchor='w', pady=(5,0))
        
        # Calculator settings
        calc_frame = ttk.LabelFrame(self, text="Calculator Settings", padding=10)
        calc_frame.pack(fill='x', padx=5, pady=5)
        
        # Numpad mode
        mode_frame = ttk.Frame(calc_frame)
        mode_frame.pack(fill='x', pady=2)
        
        ttk.Label(mode_frame, text="Numpad Mode:").pack(side='left')
        self.mode_var = tk.StringVar(value="standard")
        mode_combo = ttk.Combobox(
            mode_frame, 
            textvariable=self.mode_var,
            values=["standard", "scientific", "custom", "macro"],
            state="readonly"
        )
        mode_combo.pack(side='left', padx=(5,10))
        mode_combo.bind('<<ComboboxSelected>>', self.on_mode_change)
        
        # Sync settings button
        ttk.Button(calc_frame, text="Sync Settings to Calculator", 
                  command=self.sync_settings).pack(pady=5)
        
        # File operations
        file_frame = ttk.LabelFrame(self, text="File Operations", padding=10)
        file_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(file_frame, text="Backup Calculator Data", 
                  command=self.backup_data).pack(side='left', padx=2)
        ttk.Button(file_frame, text="Restore Calculator Data", 
                  command=self.restore_data).pack(side='left', padx=2)
        ttk.Button(file_frame, text="Update Firmware", 
                  command=self.update_firmware).pack(side='left', padx=2)
        
        # Initialize
        self.refresh_ports()
        
    def refresh_ports(self):
        """Refresh available serial ports"""
        ports = self.serial_manager.scan_ports()
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.current(0)
            
    def connect(self):
        """Connect to selected port"""
        port = self.port_var.get()
        if not port:
            messagebox.showwarning("Warning", "Please select a serial port")
            return
            
        if self.serial_manager.connect(port):
            self.status_var.set(f"Connected to {port}")
            self.status_var.set("Connected")
            # Update status color would require custom widget
        else:
            messagebox.showerror("Error", f"Failed to connect to {port}")
            
    def disconnect(self):
        """Disconnect from current port"""
        self.serial_manager.disconnect()
        self.status_var.set("Disconnected")
        
    def on_mode_change(self, event):
        """Handle numpad mode change"""
        mode = self.mode_var.get()
        print(f"Numpad mode changed to: {mode}")
        
    def sync_settings(self):
        """Synchronize settings to calculator"""
        if not self.serial_manager.connected:
            messagebox.showwarning("Warning", "Not connected to calculator")
            return
            
        settings_data = {
            "numpad_mode": self.mode_var.get(),
            "sync_timestamp": time.time()
        }
        
        success = self.serial_manager.send_message(MessageType.SETTINGS, settings_data)
        if success:
            messagebox.showinfo("Success", "Settings synchronized to calculator")
        else:
            messagebox.showerror("Error", "Failed to synchronize settings")
            
    def backup_data(self):
        """Backup calculator data"""
        messagebox.showinfo("Info", "Backup functionality not yet implemented")
        
    def restore_data(self):
        """Restore calculator data"""
        messagebox.showinfo("Info", "Restore functionality not yet implemented")
        
    def update_firmware(self):
        """Update calculator firmware"""
        messagebox.showinfo("Info", "Firmware update functionality not yet implemented")

# ================= MAIN APPLICATION =================
class PeanutCompanionApp:
    """Main PC companion application"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.serial_manager = SerialManager()
        self.setup_ui()
        self.setup_updates()
        self.running = True
        
    def setup_ui(self):
        """Setup main application UI"""
        # Window configuration
        self.root.title(PCConfig.WINDOW_TITLE)
        self.root.geometry(PCConfig.WINDOW_SIZE)
        self.root.minsize(*PCConfig.MIN_WINDOW_SIZE)
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')  # Modern theme
        
        # Main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Calculator tab
        self.calc_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.calc_frame, text="📱 Calculator")
        self.calculation_display = CalculationDisplay(self.calc_frame)
        self.calculation_display.pack(fill='both', expand=True)
        
        # Graph tab  
        self.graph_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.graph_frame, text="📊 Graphing")
        self.graph_display = GraphDisplay(self.graph_frame)
        self.graph_display.pack(fill='both', expand=True)
        
        # Settings tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="⚙️ Settings")
        self.settings_panel = SettingsPanel(self.settings_frame, self.serial_manager)
        self.settings_panel.pack(fill='both', expand=True)
        
        # Status bar
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill='x', side='bottom')
        
        self.status_label = ttk.Label(
            self.status_bar, 
            text="Ready - Not connected to calculator",
            relief='sunken'
        )
        self.status_label.pack(side='left', fill='x', expand=True)
        
        # Protocol for window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_updates(self):
        """Setup periodic updates"""
        self.update_status()
        self.process_messages()
        
    def update_status(self):
        """Update status bar"""
        if self.serial_manager.connected:
            status = f"Connected to {self.serial_manager.port} - Receiving data"
            self.settings_panel.status_var.set(f"Connected to {self.serial_manager.port}")
        else:
            status = "Ready - Not connected to calculator"
            self.settings_panel.status_var.set("Disconnected")
            
        self.status_label.config(text=status)
        
        # Schedule next update
        if self.running:
            self.root.after(PCConfig.STATUS_UPDATE_INTERVAL, self.update_status)
            
    def process_messages(self):
        """Process incoming messages from calculator"""
        if self.serial_manager.connected:
            message = self.serial_manager.get_message()
            if message:
                msg_type, data = message
                self.handle_message(msg_type, data)
                
        # Schedule next check
        if self.running:
            self.root.after(50, self.process_messages)  # Check more frequently
            
    def handle_message(self, msg_type: MessageType, data: Dict[str, Any]):
        """Handle received message from calculator"""
        try:
            if msg_type == MessageType.CALCULATION:
                expression = data.get('expression', '')
                result = data.get('result', '')
                self.calculation_display.update_calculation(expression, result)
                
            elif msg_type == MessageType.GRAPH_DATA:
                expression = data.get('expression', '')
                points = data.get('points', [])
                # Convert list of lists back to tuples
                points = [(p[0], p[1]) for p in points if len(p) >= 2]
                self.graph_display.update_graph(expression, points)
                
            elif msg_type == MessageType.HEARTBEAT:
                print("Heartbeat received from calculator")
                
            elif msg_type == MessageType.ERROR:
                error_msg = data.get('message', 'Unknown error')
                messagebox.showerror("Calculator Error", error_msg)
                
        except Exception as e:
            print(f"Error handling message: {e}")
            
    def on_closing(self):
        """Handle application closing"""
        self.running = False
        if self.serial_manager.connected:
            self.serial_manager.disconnect()
        self.root.destroy()
        
    def run(self):
        """Run the application"""
        print("Starting Peanut 3000 PC Companion...")
        self.root.mainloop()

# ================= MAIN ENTRY POINT =================
def main():
    """Main entry point"""
    print("=" * 60)
    print("💻 PEANUT 3000 PC COMPANION APPLICATION")
    print("   Enhanced Calculator Desktop Client")
    print("=" * 60)
    
    try:
        app = PeanutCompanionApp()
        app.run()
    except Exception as e:
        print(f"❌ Application error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

# ================= END OF PC_COMPANION.PY =================