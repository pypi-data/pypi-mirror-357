"""
Multicast Listener implementation for Linux using pyshark with centralized config support.
"""
import threading
import time
import os
from typing import Callable, Optional, Dict, Any
from pathlib import Path
import pyshark
from src.core.packet import Packet
from src.core.factory import PacketFactory
from src.utils.logging_utils import LoggingManager

class MulticastListener:
    def __init__(
        self,
        interface: Optional[str],
        multicast_ips: Optional[list],
        ports: Optional[list],
        bpf_filter: Optional[str],
        logging_manager: LoggingManager
    ):
        """
        Initialize multicast listener with centralized config support.
        
        Args:
            interface: Network interface to listen on (overrides config)
            multicast_ips: List of multicast IPs to filter (overrides config)
            ports: List of ports to filter (overrides config)
            bpf_filter: BPF filter to apply at capture time (optional)
            logging_manager: The centralized logging manager.
        """
        self.logger = logging_manager.get_logger(self.__class__.__name__)
        self.interface = interface
        self.multicast_ips = multicast_ips or []
        self.ports = ports
        self.capture = None
        self.capture_thread = None
        self.running = False
        self.callback = None
        self._lock = threading.Lock()
        self.bpf_filter = bpf_filter
        self.logger.info(f"Initialized MulticastListener with interface: {self.interface}")
    
    def __enter__(self):
        """Context manager entry point."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit point.
        Ensures resources are cleaned up even if an exception occurs.
        """
        self.stop_capture()
        if exc_type is not None:
            self.logger.error(f"Exception occurred: {exc_val}", exc_info=(exc_type, exc_val, exc_tb))
        return False

    def _generate_bpf_filter(self) -> str:
        """Generate BPF filter from configuration."""
        filters = []
        
        # IP filters
        if self.multicast_ips:
            ip_filters = [f'dst host {ip}' for ip in self.multicast_ips]
            if ip_filters:
                filters.append(f'({" or ".join(ip_filters)})')
        
        # Port filters
        if self.ports:
            port_filters = [f'dst port {port}' for port in self.ports]
            if port_filters:
                filters.append(f'({" or ".join(port_filters)})')
        
        # Combine filters or use default multicast filter
        if filters:
            return ' and '.join(filters)
        
        # Default BPF filter for multicast
        return 'ip multicast or ip6 multicast'

    def start_capture(self, callback: Callable[[Packet], None]) -> bool:
        """
        Start multicast packet capture with configured settings.
        """
        if self.running:
            self.logger.warning("Capture already running")
            return False

        try:
            bpf_filter = self.bpf_filter or ''
            self.logger.info(f"Starting capture with BPF filter: {bpf_filter}")
            
            self.capture = pyshark.LiveCapture(
                interface=self.interface,
                bpf_filter=bpf_filter,
                use_json=True,
                include_raw=True,
                display_filter=''
            )
            
            self.callback = callback
            self.running = True
            self.capture_thread = threading.Thread(
                target=self._capture_loop,
                name=f"MulticastListener-{self.interface}",
                daemon=True
            )
            self.capture_thread.start()
            
            time.sleep(0.2)
            if not self.capture_thread.is_alive():
                raise RuntimeError("Capture thread failed to start")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start capture: {e}", exc_info=True)
            self.stop_capture()
            return False

    def _capture_loop(self):
        """Main capture loop running in background thread."""
        try:
            for pyshark_packet in self.capture.sniff_continuously(packet_count=0):
                if not self.running:
                    break
                    
                try:
                    if not hasattr(pyshark_packet, 'frame_raw'):
                        continue
                        
                    raw_data = bytes.fromhex(pyshark_packet.frame_raw.value)
                    
                    # Use the factory to create the packet and context
                    packet, context = PacketFactory.create_packet_with_context(
                        raw_data=raw_data,
                        timestamp=pyshark_packet.sniff_time.timestamp(),
                        interface=self.interface
                    )
                    
                    if self.callback:
                        # Pass the context to the callback, not the raw packet
                        self.callback(context)
                        
                except Exception as e:
                    self.logger.error(f"Error processing packet: {e}", exc_info=True)
                    
        except Exception as e:
            self.logger.error(f"Capture loop error: {e}", exc_info=True)
        finally:
            self.stop_capture()

    def stop_capture(self):
        """Stop the capture and clean up resources."""
        with self._lock:
            if not self.running:
                return
                
            self.running = False
            
            try:
                if self.capture:
                    self.capture.close()
            except Exception as e:
                self.logger.error(f"Error closing capture: {e}", exc_info=True)
            
            try:
                if (self.capture_thread and 
                    threading.current_thread() is not self.capture_thread and
                    self.capture_thread.is_alive()):
                    self.capture_thread.join(timeout=5)
                    if self.capture_thread.is_alive():
                        self.logger.warning("Capture thread did not stop cleanly")
            except Exception as e:
                self.logger.error(f"Error joining thread: {e}", exc_info=True)
                
            self.logger.info("Multicast capture stopped")

    @property
    def current_config(self) -> Dict[str, Any]:
        """Get current configuration as dictionary."""
        return {
            'interface': self.interface,
            'multicast_ips': self.multicast_ips,
            'ports': self.ports
        }

    def __del__(self):
        """Destructor to ensure cleanup."""
        self.stop_capture()