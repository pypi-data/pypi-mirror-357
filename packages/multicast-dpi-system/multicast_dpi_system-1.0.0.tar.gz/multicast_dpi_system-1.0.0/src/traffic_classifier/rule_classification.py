"""
Rule-Based Traffic Classifier

Implements the core classification logic using configurable rules and heuristics.
"""
from typing import Dict, Any, List, Optional, Tuple
import time
from src.utils.logging_utils import LoggingManager
from src.utils.config_handler import ConfigManager
from src.core.packet_context import PacketContext
from .datamodels import TrafficCategory, PriorityLevel, BandwidthClass, ClassificationResult
from src.interfaces.traffic_classifier import ITrafficClassifier

class RuleBasedClassifier(ITrafficClassifier):
    """
    Rule-based traffic classifier for multicast DPI system.
    
    Processes DPI results to categorize traffic into meaningful classes
    using configurable rules and heuristics.
    """
    
    logger: Any
    config_manager: ConfigManager
    _category_rules: Optional[Dict[TrafficCategory, Any]] = None
    _custom_rules: Optional[List[Dict[str, Any]]] = None
    _priority_rules: Optional[Dict[PriorityLevel, List[TrafficCategory]]] = None
    _bandwidth_rules: Optional[Dict[BandwidthClass, Dict[str, Any]]] = None
    
    def __init__(self, logging_manager: LoggingManager, config_manager: ConfigManager) -> None:
        self.logger = logging_manager.get_logger("rule_classifier")
        self.config_manager = config_manager
        self._category_rules: Optional[Dict[TrafficCategory, Any]] = None
        self._custom_rules: Optional[List[Dict[str, Any]]] = None
        self._priority_rules: Optional[Dict[PriorityLevel, List[TrafficCategory]]] = None
        self._bandwidth_rules: Optional[Dict[BandwidthClass, Dict[str, Any]]] = None
        self.logger.info("RuleBasedClassifier initialized")
    
    @property
    def category_rules(self) -> Dict[TrafficCategory, Any]:
        if self._category_rules is None:
            self._category_rules = self._load_category_rules()
        return self._category_rules

    @property
    def custom_rules(self) -> List[Dict[str, Any]]:
        if self._custom_rules is None:
            self._custom_rules = self._load_custom_rules()
        return self._custom_rules

    @property
    def priority_rules(self) -> Dict[PriorityLevel, List[TrafficCategory]]:
        if self._priority_rules is None:
            self._priority_rules = self._load_priority_rules()
        return self._priority_rules

    @property
    def bandwidth_rules(self) -> Dict[BandwidthClass, Dict[str, Any]]:
        if self._bandwidth_rules is None:
            self._bandwidth_rules = self._load_bandwidth_rules()
        return self._bandwidth_rules

    def _load_category_rules(self) -> Dict[TrafficCategory, Any]:
        """Load category rules from config manager (YAML)."""
        raw_category_rules = self.config_manager.get_config('category_rules', {})
        category_rules: Dict[TrafficCategory, Any] = {}
        for cat_str, rules in raw_category_rules.items():
            try:
                cat_enum = TrafficCategory(cat_str) if cat_str in TrafficCategory._value2member_map_ else TrafficCategory.UNKNOWN
            except Exception:
                cat_enum = TrafficCategory.UNKNOWN
            category_rules[cat_enum] = rules
        return category_rules

    def _load_custom_rules(self) -> List[Dict[str, Any]]:
        """Load custom rules from config manager (YAML)."""
        return self.config_manager.get_config('custom_rules', [])

    def _load_priority_rules(self) -> Dict[PriorityLevel, List[TrafficCategory]]:
        """Initialize priority assignment rules from config"""
        raw_priority_rules = self.config_manager.get_config('priority_rules', {})
        priority_rules: Dict[PriorityLevel, List[TrafficCategory]] = {}
        for priority_str, categories in raw_priority_rules.items():
            try:
                priority = PriorityLevel[priority_str.upper()]
            except Exception:
                continue
            priority_rules[priority] = [TrafficCategory(cat) if cat in TrafficCategory._value2member_map_ else TrafficCategory.UNKNOWN for cat in categories]
        return priority_rules

    def _load_bandwidth_rules(self) -> Dict[BandwidthClass, Dict[str, Any]]:
        """Initialize bandwidth classification rules from config"""
        raw_bandwidth_rules = self.config_manager.get_config('bandwidth_rules', {})
        bandwidth_rules: Dict[BandwidthClass, Dict[str, Any]] = {}
        for bw_class_str, rules in raw_bandwidth_rules.items():
            try:
                bw_class = BandwidthClass[bw_class_str.upper()]
            except Exception:
                continue
            categories = [TrafficCategory(cat) if cat in TrafficCategory._value2member_map_ else TrafficCategory.UNKNOWN for cat in rules.get('categories', [])]
            codecs = rules.get('codecs', [])
            resolutions = rules.get('resolutions', [])
            min_bitrate = rules.get('min_bitrate', 0)
            bandwidth_rules[bw_class] = {
                'min_bitrate': min_bitrate,
                'categories': categories,
                'codecs': codecs,
                'resolutions': resolutions
            }
        return bandwidth_rules

    def classify_traffic(self, context: PacketContext) -> ClassificationResult:
        """
        Classify traffic based on DPI results and packet context.
        Custom rules are checked first, then standard category rules.
        """
        start_time: float = time.time()
        dpi_results: Dict[str, Any] = context.dpi_metadata
        if not dpi_results:
            return self._create_unknown_result(context, start_time)
        
        custom_result: Optional[ClassificationResult] = self._check_custom_rules(context, dpi_results)
        if custom_result:
            return custom_result
        
        primary_category, match_explanation, match_weights, max_weights = self._determine_primary_category(context, dpi_results)
        sub_categories: List[str] = self._determine_sub_categories(context, dpi_results, primary_category)
        priority_level: PriorityLevel = self._assign_priority(primary_category, dpi_results)
        bandwidth_class: BandwidthClass = self._classify_bandwidth(primary_category, dpi_results)
        confidence_score: float = self._calculate_confidence(match_weights, max_weights)
        classification_metadata: Dict[str, Any] = self._build_metadata(context, dpi_results)
        classification_metadata['rule_match_explanation'] = match_explanation
        
        processing_time: float = (time.time() - start_time) * 1000
        result: ClassificationResult = ClassificationResult(
            primary_category=primary_category,
            sub_categories=sub_categories,
            priority_level=priority_level,
            bandwidth_class=bandwidth_class,
            confidence_score=confidence_score,
            classification_metadata=classification_metadata,
            processing_time_ms=processing_time
        )
        self.logger.debug(f"Classified flow {context.get_flow_key()} as {primary_category.value} (confidence={confidence_score:.2f})")
        return result
    
    def _check_custom_rules(self, context: PacketContext, dpi_results: dict) -> Optional[ClassificationResult]:
        """Check and apply custom rules from config. Returns ClassificationResult if matched, else None."""
        protocol_info = dpi_results.get('protocol_identification', {})
        protocol = protocol_info.get('application_protocol', '').upper()
        codec = protocol_info.get('codec', '').upper() if protocol_info.get('codec') else None
        dst_ip = context.packet.dst_ip
        matched = None
        for rule in self.custom_rules:
            cond = rule.get('conditions', {})
            # Check protocol
            if 'protocol' in cond and protocol != cond['protocol'].upper():
                continue
            # Check codec
            if 'codec' in cond and (not codec or codec != cond['codec'].upper()):
                continue
            # Check multicast group (simple prefix match for /24, /16, etc.)
            if 'multicast_group' in cond:
                if not dst_ip or not cond['multicast_group'] in dst_ip:
                    continue
            # If all conditions match, build result
            try:
                category = TrafficCategory(rule['category'].upper()) if hasattr(TrafficCategory, rule['category'].upper()) else TrafficCategory(rule['category'])
            except Exception:
                category = TrafficCategory.UNKNOWN
            try:
                priority = PriorityLevel[rule['priority'].upper()]
            except Exception:
                priority = PriorityLevel.MEDIUM
            try:
                bandwidth = BandwidthClass[rule['bandwidth_class'].upper()]
            except Exception:
                bandwidth = BandwidthClass.MEDIUM
            matched = ClassificationResult(
                primary_category=category,
                sub_categories=[],
                priority_level=priority,
                bandwidth_class=bandwidth,
                confidence_score=1.0,
                classification_metadata={'matched_custom_rule': rule},
                processing_time_ms=0.0
            )
            break
        return matched
    
    def _determine_primary_category(self, context: PacketContext, dpi_results: Dict[str, Any]):
        """Determine the primary traffic category and explain rule matches."""
        protocol_info = dpi_results.get('protocol_identification', {})
        protocol = protocol_info.get('application_protocol', '')
        codec = protocol_info.get('codec')
        protocol = protocol.upper() if protocol else ''
        codec = codec.upper() if codec else None
        best_category = TrafficCategory.UNKNOWN
        best_score = 0
        best_explanation = {}
        best_weights = 0
        best_max_weights = 1  # avoid div by zero
        for category, rules in self.category_rules.items():
            score = 0
            explanation = {}
            weights = 0
            max_weights = 0
            # Define weights
            protocol_weight = 10
            codec_weight = 5
            signature_weight = 3
            # Check protocol match
            if 'protocols' in rules and protocol in [p.upper() for p in rules['protocols']]:
                score += protocol_weight
                weights += protocol_weight
                explanation['protocol'] = protocol
            max_weights += protocol_weight
            # Check codec match
            if 'codecs' in rules and codec and codec in [c.upper() for c in rules['codecs']]:
                score += codec_weight
                weights += codec_weight
                explanation['codec'] = codec
            max_weights += codec_weight
            # Check signature matches
            signature_matches = dpi_results.get('signature_matches', [])
            if signature_matches:
                for match in signature_matches:
                    if 'categories' in rules and match.get('category') in rules['categories']:
                        score += signature_weight
                        weights += signature_weight
                        if 'signatures' not in explanation:
                            explanation['signatures'] = []
                        explanation['signatures'].append(match.get('name', 'unknown'))
            max_weights += signature_weight * len(signature_matches) if signature_matches else 0
            # Update best match
            if score > best_score:
                best_score = score
                best_category = category
                best_explanation = explanation
                best_weights = weights
                best_max_weights = max_weights
        return best_category, best_explanation, best_weights, best_max_weights

    def _determine_sub_categories(self, context: PacketContext, dpi_results: Dict[str, Any], 
                                 primary_category: TrafficCategory) -> List[str]:
        """Determine sub-categories based on DPI results and primary category."""
        sub_categories = []
        protocol_info = dpi_results.get('protocol_identification', {})
        signature_matches = dpi_results.get('signature_matches', [])
        # Add protocol-specific sub-categories
        if protocol_info.get('application_protocol'):
            sub_categories.append(f"protocol_{protocol_info['application_protocol'].lower()}")
        if protocol_info.get('codec'):
            sub_categories.append(f"codec_{protocol_info['codec'].lower()}")
        # Add signature-based sub-categories
        for match in signature_matches:
            if match.get('category'):
                sub_categories.append(f"signature_{match['category'].lower()}")
        # Add category-specific sub-categories
        if primary_category == TrafficCategory.VIDEO_STREAMING:
            sub_categories.append('video_content')
        elif primary_category == TrafficCategory.AUDIO_STREAMING:
            sub_categories.append('audio_content')
        elif primary_category == TrafficCategory.VOICE_CALL:
            sub_categories.append('real_time')
        return list(set(sub_categories))  # Remove duplicates

    def _assign_priority(self, category: TrafficCategory, dpi_results: Dict[str, Any]) -> PriorityLevel:
        """Assign priority level based on category and DPI results."""
        for priority, categories in self.priority_rules.items():
            if category in categories:
                return priority
        return PriorityLevel.MEDIUM

    def _classify_bandwidth(self, category: TrafficCategory, dpi_results: Dict[str, Any]) -> BandwidthClass:
        """Classify bandwidth requirements based on category and DPI results."""
        for bw_class, rules in self.bandwidth_rules.items():
            if category in rules.get('categories', []):
                return bw_class
        return BandwidthClass.MEDIUM

    def _calculate_confidence(self, match_weights: int, max_weights: int) -> float:
        """Calculate confidence score based on rule match weights."""
        if max_weights == 0:
            return 0.0
        return min(1.0, match_weights / max_weights)

    def _build_metadata(self, context: PacketContext, dpi_results: Dict[str, Any]) -> Dict[str, Any]:
        """Build classification metadata from DPI results."""
        return {
            'flow_key': context.get_flow_key(),
            'dpi_results': dpi_results,
            'packet_length': context.packet.length,
            'timestamp': context.packet.timestamp
        }

    def _create_unknown_result(self, context: PacketContext, start_time: float) -> ClassificationResult:
        """Create a result for unclassified traffic."""
        processing_time = (time.time() - start_time) * 1000
        return ClassificationResult(
            primary_category=TrafficCategory.UNKNOWN,
            sub_categories=['unclassified'],
            priority_level=PriorityLevel.LOW,
            bandwidth_class=BandwidthClass.LOW,
            confidence_score=0.0,
            classification_metadata={
                'flow_key': context.get_flow_key(),
                'reason': 'no_dpi_results'
            },
            processing_time_ms=processing_time
        )

    def _ip_in_range(self, ip: str, range_str: str) -> bool:
        """Check if IP is in the specified range (simple implementation)."""
        # Simple prefix matching for now
        return ip.startswith(range_str)

    def get_classification_statistics(self) -> Dict[str, Any]:
        """Get classification statistics."""
        return {'method': 'rule_based'}

    def get_flow_statistics(self) -> Dict[str, Any]:
        """Get flow statistics (not applicable for rule-based classifier)."""
        return {}

    def cleanup_old_flows(self, max_age_seconds: int = 300) -> None:
        """Clean up old flows (not applicable for rule-based classifier)."""
        pass
