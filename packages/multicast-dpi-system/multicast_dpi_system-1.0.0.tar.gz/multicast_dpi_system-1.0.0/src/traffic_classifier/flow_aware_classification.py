"""
Flow-Aware Traffic Classifier

Tracks flow/group statistics and enhances bandwidth classification using observed traffic patterns.
"""
from typing import Dict, Any, Optional
import time
from collections import defaultdict
from src.traffic_classifier.rule_classification import RuleBasedClassifier
from src.traffic_classifier.datamodels import ClassificationResult, BandwidthClass
from src.core.packet_context import PacketContext
from src.utils.logging_utils import LoggingManager
from src.utils.config_handler import ConfigManager
from src.core.flow_stats_manager import FlowStatsManager, FlowStatistics

class FlowAwareClassifier:
    """
    Flow-aware traffic classifier that maintains per-flow statistics and enhances
    bandwidth classification using observed traffic patterns.
    """
    
    def __init__(self, logging_manager: LoggingManager, config_manager: ConfigManager, flow_stats_manager: Optional[FlowStatsManager] = None) -> None:
        self.logger = logging_manager.get_logger("flow_aware_classifier")
        self.config_manager = config_manager
        self.rule_classifier = RuleBasedClassifier(logging_manager, config_manager)
        self.flow_stats_manager = flow_stats_manager or FlowStatsManager()
        
        # Bandwidth thresholds in bits per second (loaded from config)
        raw_thresholds = self.config_manager.get_config('bandwidth_thresholds', {})
        self.bandwidth_thresholds = {
            BandwidthClass.ULTRA_HIGH: raw_thresholds.get('ultra_high', 20000000),
            BandwidthClass.HIGH: raw_thresholds.get('high', 5000000),
            BandwidthClass.MEDIUM: raw_thresholds.get('medium', 1000000),
            BandwidthClass.LOW: raw_thresholds.get('low', 0)
        }

    def classify_traffic(self, context: PacketContext) -> ClassificationResult:
        """Classify traffic using flow-aware logic."""
        # Update flow statistics
        flow_stats: FlowStatistics = self.flow_stats_manager.update_flow_stats(context)
        
        # Get static classification from rule-based classifier
        static_result: ClassificationResult = self.rule_classifier.classify_traffic(context)
        
        # Set the flow's category to the classified category
        flow_stats.category = static_result.primary_category.value
        
        # Enhance bandwidth class using observed bitrate
        observed_bandwidth: float = 0.0
        if flow_stats.duration > 0:
            observed_bandwidth = (flow_stats.byte_count * 8) / flow_stats.duration  # bits per second
        
        flow_bandwidth_class: BandwidthClass = self._bandwidth_class_from_bitrate(observed_bandwidth)
        
        # Use the higher of static or observed bandwidth class
        final_bandwidth_class: BandwidthClass = max(
            static_result.bandwidth_class, 
            flow_bandwidth_class, 
            key=lambda b: list(BandwidthClass).index(b)
        )
        
        # Flow-aware sub-categories
        flow_aware_subcats: list = []
        flow_aware_flags: dict = {}
        
        if flow_stats.packets_per_second > 500:
            flow_aware_subcats.append('high_rate_stream')
            flow_aware_flags['high_rate_stream'] = True
            
        if flow_stats.duration > 60:
            flow_aware_subcats.append('long_lived_stream')
            flow_aware_flags['long_lived_stream'] = True
            
        if flow_stats.average_packet_size > 1200:
            flow_aware_subcats.append('large_packets')
            flow_aware_flags['large_packets'] = True
            
        if flow_stats.packets_per_second > 0 and (flow_stats.average_packet_size / flow_stats.packets_per_second) > 1000:
            flow_aware_subcats.append('bursty')
            flow_aware_flags['bursty'] = True
        
        # Combine sub-categories
        all_subcats: list = static_result.sub_categories + flow_aware_subcats
        
        # Build result with flow statistics and flow-aware flags
        result: ClassificationResult = ClassificationResult(
            primary_category=static_result.primary_category,
            sub_categories=all_subcats,
            priority_level=static_result.priority_level,
            bandwidth_class=final_bandwidth_class,
            confidence_score=static_result.confidence_score,
            classification_metadata={
                **static_result.classification_metadata,
                'flow_key': flow_stats.flow_key,
                'flow_packet_count': flow_stats.packet_count,
                'flow_byte_count': flow_stats.byte_count,
                'flow_duration': flow_stats.duration,
                'flow_packets_per_second': flow_stats.packets_per_second,
                'flow_average_packet_size': flow_stats.average_packet_size,
                'observed_bandwidth_bps': observed_bandwidth,
                'flow_bandwidth_class': flow_bandwidth_class.value,
                'final_bandwidth_class': final_bandwidth_class.value,
                **flow_aware_flags
            },
            processing_time_ms=static_result.processing_time_ms,
            timestamp=static_result.timestamp
        )
        
        self.logger.debug(f"Flow-aware classified {flow_stats.flow_key}: bandwidth={final_bandwidth_class.value} (observed {observed_bandwidth:.2f} bps), subcats={all_subcats}")
        return result

    def _bandwidth_class_from_bitrate(self, bps: float) -> BandwidthClass:
        """Map observed bits per second to a BandwidthClass."""
        if bps >= self.bandwidth_thresholds[BandwidthClass.ULTRA_HIGH]:
            return BandwidthClass.ULTRA_HIGH
        elif bps >= self.bandwidth_thresholds[BandwidthClass.HIGH]:
            return BandwidthClass.HIGH
        elif bps >= self.bandwidth_thresholds[BandwidthClass.MEDIUM]:
            return BandwidthClass.MEDIUM
        else:
            return BandwidthClass.LOW

    def get_flow_statistics(self) -> Dict[str, FlowStatistics]:
        """Return current flow statistics for monitoring."""
        return self.flow_stats_manager.get_flow_statistics()

    def cleanup_old_flows(self, max_age_seconds: int = 300) -> None:
        """Clean up old flow statistics to prevent memory leaks."""
        self.flow_stats_manager.cleanup_old_flows(max_age_seconds) 