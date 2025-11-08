#!/usr/bin/env python3
"""
================================================================================
🔌 USB INTERFACE MODULE - PEANUT 3000 PC CONNECTIVITY
================================================================================
USB HID Interface for PC Numpad Functionality and Data Communication
- USB HID numpad emulation with multiple modes
- Serial communication for data transfer
- Real-time calculation streaming
- File transfer protocols
- Firmware update support

Part of Phase 3: PC Connectivity & External Interface
Author: Peanut 3000 Development Team
Version: 2.0.0
Date: November 6, 2025
================================================================================
"""

import time
import json
# typing module not available in MicroPython - type hints work without import
# enum module not available in standard MicroPython
import struct

try:
    import usb_hid
    import usb_cdc
    from adafruit_hid.keyboard import Keyboard
    from adafruit_hid.keycode import Keycode
    from adafruit_hid.consumer_control import ConsumerControl
    from adafruit_hid.consumer_control_code import ConsumerControlCode
    USB_AVAILABLE = True
except ImportError:
    USB_AVAILABLE = False
    print("[WARNING] USB HID libraries not available - PC connectivity disabled")

# ================= CONSTANTS & CONFIGURATION =================
class USBConfig:
    """USB interface configuration"""
    
    # Communication Settings
    SERIAL_BAUDRATE = 115200
    PACKET_SIZE = 64
    TIMEOUT_MS = 1000
    
    # HID Settings
    REPEAT_DELAY_MS = 500
    REPEAT_RATE_MS = 50
    
    # Protocol Settings
    PROTOCOL_VERSION = "1.0"
    MAGIC_HEADER = b"PN30"
    
    # Buffer Sizes
    TX_BUFFER_SIZE = 512
    RX_BUFFER_SIZE = 512

# Simple Enum replacement for MicroPython compatibility
class NumpadMode:
    """Numpad operating modes"""
    STANDARD = "standard"      # Standard PC numpad
    SCIENTIFIC = "scientific"  # Scientific calculator functions
    CUSTOM = "custom"          # User-defined mappings
    MACRO = "macro"           # Macro recording/playback

class MessageType:
    """Communication message types"""
    HEARTBEAT = 0x01
    CALCULATION = 0x02
    GRAPH_DATA = 0x03
    FILE_TRANSFER = 0x04
    SETTINGS = 0x05
    FIRMWARE = 0x06
    ERROR = 0xFF

# ================= USB HID NUMPAD EMULATOR =================
class USBNumpadEmulator:
    """PC numpad emulation with multiple operating modes"""
    
    def __init__(self):
        self.enabled = USB_AVAILABLE
        self.keyboard = None
        self.consumer_control = None
        self.current_mode = NumpadMode.STANDARD
        self.macro_recording = False
        self.recorded_macros = {}
        self.current_macro = []
        
        # Key mapping configurations
        self._setup_key_mappings()
        
        if self.enabled:
            self._initialize_hid()
            
    def _initialize_hid(self):
        """Initialize USB HID devices"""
        try:
            self.keyboard = Keyboard(usb_hid.devices)
            self.consumer_control = ConsumerControl(usb_hid.devices)
            print("[USB] HID devices initialized successfully")
        except Exception as e:
            print(f"[USB] HID initialization failed: {e}")
            self.enabled = False
            
    def _setup_key_mappings(self):
        """Setup key mappings for different modes"""
        # Standard numpad mapping
        self.standard_map = {
            '0': Keycode.KEYPAD_ZERO,
            '1': Keycode.KEYPAD_ONE,
            '2': Keycode.KEYPAD_TWO,
            '3': Keycode.KEYPAD_THREE,
            '4': Keycode.KEYPAD_FOUR,
            '5': Keycode.KEYPAD_FIVE,
            '6': Keycode.KEYPAD_SIX,
            '7': Keycode.KEYPAD_SEVEN,
            '8': Keycode.KEYPAD_EIGHT,
            '9': Keycode.KEYPAD_NINE,
            '+': Keycode.KEYPAD_PLUS,
            '-': Keycode.KEYPAD_MINUS,
            '*': Keycode.KEYPAD_ASTERISK,
            '/': Keycode.KEYPAD_FORWARD_SLASH,
            '=': Keycode.KEYPAD_EQUALS,
            '.': Keycode.KEYPAD_PERIOD,
            'Enter': Keycode.KEYPAD_ENTER,
        }
        
        # Scientific mode mapping (using Ctrl+ combinations)
        self.scientific_map = {
            'sin(': [Keycode.CONTROL, Keycode.S],
            'cos(': [Keycode.CONTROL, Keycode.C],
            'tan(': [Keycode.CONTROL, Keycode.T],
            'log(': [Keycode.CONTROL, Keycode.L],
            'ln(': [Keycode.CONTROL, Keycode.N],
            'sqrt(': [Keycode.CONTROL, Keycode.R],
            '^2': [Keycode.CONTROL, Keycode.TWO],
            'π': [Keycode.CONTROL, Keycode.P],
            'exp(': [Keycode.CONTROL, Keycode.E],
        }
        
        # Custom mappings (user-definable)
        self.custom_map = {}
        
    def set_mode(self, mode):
        """Switch numpad operating mode"""
        # Validate mode is a valid value
        valid_modes = [NumpadMode.STANDARD, NumpadMode.SCIENTIFIC, NumpadMode.CUSTOM, NumpadMode.MACRO]
        if mode not in valid_modes:
            print(f"[USB] Invalid numpad mode: {mode}")
            return False
                
        self.current_mode = mode
        print(f"[USB] Numpad mode switched to: {mode}")
        return True
        
    def send_keypress(self, key: str, modifiers: List[int] = None) -> bool:
        """Send keypress to PC"""
        if not self.enabled or not self.keyboard:
            return False
            
        try:
            if self.current_mode == NumpadMode.STANDARD:
                return self._send_standard_key(key)
            elif self.current_mode == NumpadMode.SCIENTIFIC:
                return self._send_scientific_key(key)
            elif self.current_mode == NumpadMode.CUSTOM:
                return self._send_custom_key(key)
            elif self.current_mode == NumpadMode.MACRO:
                return self._handle_macro_key(key)
                
        except Exception as e:
            print(f"[USB] Keypress failed: {e}")
            return False
            
        return False
        
    def _send_standard_key(self, key: str) -> bool:
        """Send standard numpad key"""
        keycode = self.standard_map.get(key)
        if keycode:
            self.keyboard.press(keycode)
            time.sleep_ms(USBConfig.REPEAT_RATE_MS)
            self.keyboard.release(keycode)
            
            # Record for macro if recording
            if self.macro_recording:
                self.current_macro.append(('key', key, time.ticks_ms()))
                
            return True
        return False
        
    def _send_scientific_key(self, key: str) -> bool:
        """Send scientific function key combination"""
        key_combo = self.scientific_map.get(key)
        if key_combo:
            # Press all keys in combination
            for keycode in key_combo:
                self.keyboard.press(keycode)
                
            time.sleep_ms(USBConfig.REPEAT_RATE_MS)
            
            # Release all keys
            for keycode in reversed(key_combo):
                self.keyboard.release(keycode)
                
            # Record for macro if recording
            if self.macro_recording:
                self.current_macro.append(('scientific', key, time.ticks_ms()))
                
            return True
            
        # Fall back to standard for numbers and operators
        return self._send_standard_key(key)
        
    def _send_custom_key(self, key: str) -> bool:
        """Send custom-mapped key"""
        if key in self.custom_map:
            custom_action = self.custom_map[key]
            # Execute custom action (implementation depends on action type)
            print(f"[USB] Custom action for {key}: {custom_action}")
            return True
        return self._send_standard_key(key)
        
    def _handle_macro_key(self, key: str) -> bool:
        """Handle macro recording/playback"""
        if key == 'macro_record':
            self.start_macro_recording()
        elif key == 'macro_stop':
            self.stop_macro_recording()
        elif key.startswith('macro_play_'):
            macro_name = key[11:]  # Remove 'macro_play_' prefix
            self.play_macro(macro_name)
        else:
            # Regular key in macro mode
            return self._send_standard_key(key)
        return True
        
    def start_macro_recording(self, name: str = None):
        """Start recording a macro"""
        if name is None:
            name = f"macro_{len(self.recorded_macros) + 1}"
            
        self.macro_recording = True
        self.current_macro = []
        self.current_macro_name = name
        print(f"[USB] Started recording macro: {name}")
        
    def stop_macro_recording(self) -> bool:
        """Stop recording and save macro"""
        if not self.macro_recording:
            return False
            
        self.macro_recording = False
        if self.current_macro:
            self.recorded_macros[self.current_macro_name] = self.current_macro.copy()
            print(f"[USB] Saved macro '{self.current_macro_name}' with {len(self.current_macro)} actions")
            
        self.current_macro = []
        return True
        
    def play_macro(self, name: str) -> bool:
        """Playback recorded macro"""
        if name not in self.recorded_macros:
            print(f"[USB] Macro not found: {name}")
            return False
            
        macro = self.recorded_macros[name]
        print(f"[USB] Playing macro: {name}")
        
        for action_type, key, timestamp in macro:
            if action_type == 'key':
                self._send_standard_key(key)
            elif action_type == 'scientific':
                self._send_scientific_key(key)
                
            time.sleep_ms(50)  # Small delay between actions
            
        return True
        
    def set_custom_mapping(self, key: str, action: Any):
        """Set custom key mapping"""
        self.custom_map[key] = action
        print(f"[USB] Custom mapping set: {key} -> {action}")
        
    def get_status(self) -> Dict[str, Any]:
        """Get numpad status information"""
        return {
            "enabled": self.enabled,
            "mode": self.current_mode.value if self.current_mode else None,
            "macro_recording": self.macro_recording,
            "recorded_macros": list(self.recorded_macros.keys()),
            "custom_mappings": len(self.custom_map)
        }

# ================= SERIAL COMMUNICATION PROTOCOL =================
class USBSerialProtocol:
    """Serial communication protocol for data exchange"""
    
    def __init__(self):
        self.enabled = USB_AVAILABLE
        self.serial = None
        self.tx_buffer = bytearray(USBConfig.TX_BUFFER_SIZE)
        self.rx_buffer = bytearray(USBConfig.RX_BUFFER_SIZE)
        self.packet_counter = 0
        
        if self.enabled:
            self._initialize_serial()
            
    def _initialize_serial(self):
        """Initialize USB CDC serial connection"""
        try:
            self.serial = usb_cdc.console
            if self.serial:
                print("[USB] Serial communication initialized")
            else:
                print("[USB] Serial not available")
                self.enabled = False
        except Exception as e:
            print(f"[USB] Serial initialization failed: {e}")
            self.enabled = False
            
    def _create_packet(self, msg_type: MessageType, data: bytes) -> bytes:
        """Create protocol packet"""
        packet = bytearray()
        packet.extend(USBConfig.MAGIC_HEADER)  # Magic header
        packet.append(msg_type.value)          # Message type
        packet.extend(struct.pack('<H', len(data)))  # Data length (little-endian)
        packet.extend(struct.pack('<L', self.packet_counter))  # Packet counter
        packet.extend(data)                    # Data payload
        
        # Simple checksum
        checksum = sum(packet) & 0xFF
        packet.append(checksum)
        
        self.packet_counter += 1
        return bytes(packet)
        
    def _parse_packet(self, packet: bytes):
        """Parse received packet"""
        if len(packet) < 8:  # Minimum packet size
            return False, None, None
            
        # Verify magic header
        if packet[:4] != USBConfig.MAGIC_HEADER:
            return False, None, None
            
        msg_type = packet[4]  # MessageType is now just an int
        data_len = struct.unpack('<H', packet[5:7])[0]
        
        if len(packet) < 8 + data_len + 1:  # Header + data + checksum
            return False, None, None
            
        data = packet[8:8+data_len]
        checksum = packet[8+data_len]
        
        # Verify checksum
        calc_checksum = sum(packet[:-1]) & 0xFF
        if checksum != calc_checksum:
            return False, None, None
            
        return True, msg_type, data
        
    def send_calculation(self, expression: str, result: str) -> bool:
        """Send calculation to PC"""
        if not self.enabled or not self.serial:
            return False
            
        try:
            data = {
                "expression": expression,
                "result": result,
                "timestamp": time.ticks_ms()
            }
            
            json_data = json.dumps(data).encode('utf-8')
            packet = self._create_packet(MessageType.CALCULATION, json_data)
            
            self.serial.write(packet)
            return True
            
        except Exception as e:
            print(f"[USB] Send calculation failed: {e}")
            return False
            
    def send_graph_data(self, expression: str, points: List[Tuple[float, float]]) -> bool:
        """Send graph data to PC"""
        if not self.enabled or not self.serial:
            return False
            
        try:
            data = {
                "expression": expression,
                "points": points,
                "timestamp": time.ticks_ms()
            }
            
            json_data = json.dumps(data).encode('utf-8')
            packet = self._create_packet(MessageType.GRAPH_DATA, json_data)
            
            self.serial.write(packet)
            return True
            
        except Exception as e:
            print(f"[USB] Send graph data failed: {e}")
            return False
            
    def send_heartbeat(self) -> bool:
        """Send heartbeat to maintain connection"""
        if not self.enabled or not self.serial:
            return False
            
        try:
            data = {
                "timestamp": time.ticks_ms(),
                "version": USBConfig.PROTOCOL_VERSION
            }
            
            json_data = json.dumps(data).encode('utf-8')
            packet = self._create_packet(MessageType.HEARTBEAT, json_data)
            
            self.serial.write(packet)
            return True
            
        except Exception as e:
            print(f"[USB] Send heartbeat failed: {e}")
            return False
            
    def receive_data(self) -> Optional[Tuple[MessageType, Dict[str, Any]]]:
        """Receive and parse data from PC"""
        if not self.enabled or not self.serial:
            return None
            
        try:
            if self.serial.in_waiting > 0:
                # Read available data
                data = self.serial.read(self.serial.in_waiting)
                
                # Try to parse packet
                success, msg_type, payload = self._parse_packet(data)
                if success:
                    try:
                        json_data = json.loads(payload.decode('utf-8'))
                        return msg_type, json_data
                    except json.JSONDecodeError:
                        print("[USB] Invalid JSON in received packet")
                        
        except Exception as e:
            print(f"[USB] Receive data failed: {e}")
            
        return None
        
    def send_file(self, filename: str, data: bytes) -> bool:
        """Send file to PC"""
        if not self.enabled or not self.serial:
            return False
            
        try:
            # Send file in chunks
            chunk_size = USBConfig.PACKET_SIZE - 20  # Leave room for headers
            total_chunks = (len(data) + chunk_size - 1) // chunk_size
            
            for chunk_idx in range(total_chunks):
                start_pos = chunk_idx * chunk_size
                end_pos = min(start_pos + chunk_size, len(data))
                chunk_data = data[start_pos:end_pos]
                
                file_packet = {
                    "filename": filename,
                    "chunk_index": chunk_idx,
                    "total_chunks": total_chunks,
                    "data": list(chunk_data)  # Convert to list for JSON
                }
                
                json_data = json.dumps(file_packet).encode('utf-8')
                packet = self._create_packet(MessageType.FILE_TRANSFER, json_data)
                
                self.serial.write(packet)
                time.sleep_ms(10)  # Small delay between chunks
                
            return True
            
        except Exception as e:
            print(f"[USB] File transfer failed: {e}")
            return False

# ================= USB INTERFACE MANAGER =================
class USBInterfaceManager:
    """Main USB interface management class"""
    
    def __init__(self):
        self.numpad = USBNumpadEmulator()
        self.protocol = USBSerialProtocol()
        self.enabled = USB_AVAILABLE
        self.last_heartbeat = 0
        self.heartbeat_interval = 5000  # 5 seconds
        
        # PC connection state
        self.pc_connected = False
        self.pc_capabilities = {}
        
        print(f"[USB] Interface manager initialized (enabled: {self.enabled})")
        
    def process_calculator_input(self, key: str, expression: str, result: str):
        """Process calculator input for PC transmission"""
        if not self.enabled:
            return
            
        # Send numpad emulation
        self.numpad.send_keypress(key)
        
        # Send calculation data if result available
        if result and result != "Error":
            self.protocol.send_calculation(expression, result)
            
    def process_graph_update(self, expression: str, points: List[Tuple[float, float]]):
        """Process graph update for PC transmission"""
        if not self.enabled:
            return
            
        # Send graph data to PC
        self.protocol.send_graph_data(expression, points)
        
    def update(self):
        """Update USB interface (call regularly from main loop)"""
        if not self.enabled:
            return
            
        # Send periodic heartbeat
        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_heartbeat) > self.heartbeat_interval:
            if self.protocol.send_heartbeat():
                self.last_heartbeat = now
                
        # Process incoming data
        received = self.protocol.receive_data()
        if received:
            msg_type, data = received
            self._handle_received_message(msg_type, data)
            
    def _handle_received_message(self, msg_type: MessageType, data: Dict[str, Any]):
        """Handle received message from PC"""
        if msg_type == MessageType.HEARTBEAT:
            self.pc_connected = True
            self.pc_capabilities = data.get('capabilities', {})
            print("[USB] PC heartbeat received")
            
        elif msg_type == MessageType.SETTINGS:
            self._handle_settings_message(data)
            
        elif msg_type == MessageType.FILE_TRANSFER:
            self._handle_file_transfer(data)
            
        else:
            print(f"[USB] Unhandled message type: {msg_type}")
            
    def _handle_settings_message(self, data: Dict[str, Any]):
        """Handle settings synchronization from PC"""
        try:
            if 'numpad_mode' in data:
                mode = data['numpad_mode']
                self.numpad.set_mode(mode)
                
            if 'custom_mappings' in data:
                mappings = data['custom_mappings']
                for key, action in mappings.items():
                    self.numpad.set_custom_mapping(key, action)
                    
            print("[USB] Settings updated from PC")
            
        except Exception as e:
            print(f"[USB] Settings update failed: {e}")
            
    def _handle_file_transfer(self, data: Dict[str, Any]):
        """Handle file transfer from PC"""
        # File transfer handling would be implemented here
        print(f"[USB] File transfer received: {data.get('filename', 'unknown')}")
        
    def get_status(self) -> Dict[str, Any]:
        """Get USB interface status"""
        return {
            "usb_enabled": self.enabled,
            "pc_connected": self.pc_connected,
            "numpad_status": self.numpad.get_status(),
            "protocol_version": USBConfig.PROTOCOL_VERSION,
            "last_heartbeat": self.last_heartbeat
        }
        
    def export_file_to_pc(self, filename: str, data: bytes) -> bool:
        """Export file to PC via USB"""
        return self.protocol.send_file(filename, data)
        
    def set_numpad_mode(self, mode: str) -> bool:
        """Set numpad operating mode"""
        return self.numpad.set_mode(mode)
        
    def record_macro(self, name: str):
        """Start recording a macro"""
        self.numpad.start_macro_recording(name)
        
    def stop_macro(self):
        """Stop recording macro"""
        self.numpad.stop_macro_recording()
        
    def play_macro(self, name: str):
        """Play recorded macro"""
        self.numpad.play_macro(name)

# ================= INTEGRATION FUNCTIONS =================
def create_usb_interface() -> Optional[USBInterfaceManager]:
    """Create USB interface manager instance"""
    if USB_AVAILABLE:
        return USBInterfaceManager()
    else:
        print("[USB] USB interface not available")
        return None

def test_usb_interface():
    """Test USB interface functionality"""
    print("=" * 50)
    print("🔌 USB INTERFACE TEST")
    print("=" * 50)
    
    interface = create_usb_interface()
    if not interface:
        print("❌ USB interface creation failed")
        return False
        
    # Test numpad emulation
    print("Testing numpad emulation...")
    for key in ['1', '2', '3', '+']:
        success = interface.numpad.send_keypress(key)
        print(f"  {key}: {'✅' if success else '❌'}")
        time.sleep_ms(100)
        
    # Test scientific mode
    print("Testing scientific mode...")
    interface.numpad.set_mode(NumpadMode.SCIENTIFIC)
    for key in ['sin(', 'cos(', 'π']:
        success = interface.numpad.send_keypress(key)
        print(f"  {key}: {'✅' if success else '❌'}")
        time.sleep_ms(100)
        
    # Test data transmission
    print("Testing data transmission...")
    success = interface.protocol.send_calculation("2+2", "4")
    print(f"  Calculation: {'✅' if success else '❌'}")
    
    success = interface.protocol.send_heartbeat()
    print(f"  Heartbeat: {'✅' if success else '❌'}")
    
    # Display status
    status = interface.get_status()
    print(f"\n📊 Status: {status}")
    
    print("\n✅ USB interface test complete")
    return True

if __name__ == "__main__":
    test_usb_interface()

# ================= END OF USB_INTERFACE.PY =================