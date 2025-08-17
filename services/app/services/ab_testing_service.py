import asyncio
import logging
import random
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import statistics
from ..models import OutreachTemplate, OutreachCampaign

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestStatus(Enum):
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class TestType(Enum):
    SUBJECT_LINE = "subject_line"
    EMAIL_BODY = "email_body"
    TONE = "tone"
    CTA = "call_to_action"
    SEND_TIME = "send_time"
    TEMPLATE_TYPE = "template_type"

@dataclass
class TestVariant:
    variant_id: str
    variant_name: str
    template: OutreachTemplate
    traffic_allocation: float  # Percentage of traffic (0.0 to 1.0)
    sent_count: int = 0
    opened_count: int = 0
    clicked_count: int = 0
    replied_count: int = 0
    conversion_count: int = 0  # Interviews/positive responses
    
    @property
    def open_rate(self) -> float:
        return (self.opened_count / self.sent_count) if self.sent_count > 0 else 0.0
    
    @property
    def click_rate(self) -> float:
        return (self.clicked_count / self.sent_count) if self.sent_count > 0 else 0.0
    
    @property
    def reply_rate(self) -> float:
        return (self.replied_count / self.sent_count) if self.sent_count > 0 else 0.0
    
    @property
    def conversion_rate(self) -> float:
        return (self.conversion_count / self.sent_count) if self.sent_count > 0 else 0.0

@dataclass
class ABTest:
    test_id: str
    test_name: str
    test_type: TestType
    variants: List[TestVariant]
    status: TestStatus
    start_date: datetime
    end_date: Optional[datetime]
    minimum_sample_size: int
    confidence_level: float  # 0.95 for 95% confidence
    winning_variant_id: Optional[str] = None
    statistical_significance: Optional[float] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class TestResults:
    test_id: str
    winning_variant: TestVariant
    confidence_level: float
    statistical_significance: float
    improvement_percentage: float
    recommendation: str
    detailed_metrics: Dict[str, Any]

class ABTestingService:
    def __init__(self):
        self.active_tests: Dict[str, ABTest] = {}
        self.completed_tests: Dict[str, ABTest] = {}
        self.test_assignments: Dict[str, str] = {}  # candidate_id -> variant_id
        
        # Default test configurations
        self.default_confidence_level = 0.95
        self.default_minimum_sample_size = 100
        self.default_test_duration_days = 14
        
    def create_ab_test(self,
                      test_name: str,
                      test_type: TestType,
                      templates: List[OutreachTemplate],
                      traffic_allocation: List[float] = None,
                      minimum_sample_size: int = None,
                      confidence_level: float = None,
                      duration_days: int = None) -> ABTest:
        """
        Create a new A/B test
        """
        try:
            test_id = f"test_{test_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Set defaults
            if traffic_allocation is None:
                traffic_allocation = [1.0 / len(templates)] * len(templates)
            if minimum_sample_size is None:
                minimum_sample_size = self.default_minimum_sample_size
            if confidence_level is None:
                confidence_level = self.default_confidence_level
            if duration_days is None:
                duration_days = self.default_test_duration_days
            
            # Validate traffic allocation
            if abs(sum(traffic_allocation) - 1.0) > 0.01:
                raise ValueError("Traffic allocation must sum to 1.0")
            
            # Create variants
            variants = []
            for i, (template, allocation) in enumerate(zip(templates, traffic_allocation)):
                variant = TestVariant(
                    variant_id=f"{test_id}_variant_{i+1}",
                    variant_name=f"Variant {chr(65+i)}",  # A, B, C, etc.
                    template=template,
                    traffic_allocation=allocation
                )
                variants.append(variant)
            
            # Create test
            ab_test = ABTest(
                test_id=test_id,
                test_name=test_name,
                test_type=test_type,
                variants=variants,
                status=TestStatus.DRAFT,
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=duration_days),
                minimum_sample_size=minimum_sample_size,
                confidence_level=confidence_level
            )
            
            self.active_tests[test_id] = ab_test
            logger.info(f"Created A/B test: {test_name} ({test_id})")
            
            return ab_test
            
        except Exception as e:
            logger.error(f"Error creating A/B test: {str(e)}")
            raise
    
    def start_test(self, test_id: str) -> bool:
        """
        Start an A/B test
        """
        try:
            if test_id not in self.active_tests:
                raise ValueError(f"Test {test_id} not found")
            
            test = self.active_tests[test_id]
            if test.status != TestStatus.DRAFT:
                raise ValueError(f"Test {test_id} is not in draft status")
            
            test.status = TestStatus.RUNNING
            test.start_date = datetime.now()
            
            logger.info(f"Started A/B test: {test.test_name} ({test_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error starting test {test_id}: {str(e)}")
            return False
    
    def assign_variant(self, test_id: str, candidate_id: str) -> Optional[TestVariant]:
        """
        Assign a candidate to a test variant
        """
        try:
            if test_id not in self.active_tests:
                return None
            
            test = self.active_tests[test_id]
            if test.status != TestStatus.RUNNING:
                return None
            
            # Check if candidate already assigned
            assignment_key = f"{test_id}_{candidate_id}"
            if assignment_key in self.test_assignments:
                variant_id = self.test_assignments[assignment_key]
                return next((v for v in test.variants if v.variant_id == variant_id), None)
            
            # Assign based on traffic allocation
            rand = random.random()
            cumulative_allocation = 0.0
            
            for variant in test.variants:
                cumulative_allocation += variant.traffic_allocation
                if rand <= cumulative_allocation:
                    self.test_assignments[assignment_key] = variant.variant_id
                    return variant
            
            # Fallback to first variant
            self.test_assignments[assignment_key] = test.variants[0].variant_id
            return test.variants[0]
            
        except Exception as e:
            logger.error(f"Error assigning variant for test {test_id}: {str(e)}")
            return None
    
    def record_event(self, test_id: str, variant_id: str, event_type: str) -> bool:
        """
        Record an event for a test variant
        """
        try:
            if test_id not in self.active_tests:
                return False
            
            test = self.active_tests[test_id]
            variant = next((v for v in test.variants if v.variant_id == variant_id), None)
            
            if not variant:
                return False
            
            # Record the event
            if event_type == 'sent':
                variant.sent_count += 1
            elif event_type == 'opened':
                variant.opened_count += 1
            elif event_type == 'clicked':
                variant.clicked_count += 1
            elif event_type == 'replied':
                variant.replied_count += 1
            elif event_type == 'converted':
                variant.conversion_count += 1
            
            # Check if test should be analyzed
            self._check_test_completion(test_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error recording event for test {test_id}: {str(e)}")
            return False
    
    def analyze_test_results(self, test_id: str) -> Optional[TestResults]:
        """
        Analyze test results and determine statistical significance
        """
        try:
            if test_id not in self.active_tests and test_id not in self.completed_tests:
                return None
            
            test = self.active_tests.get(test_id) or self.completed_tests.get(test_id)
            
            # Check if we have enough data
            total_sent = sum(v.sent_count for v in test.variants)
            if total_sent < test.minimum_sample_size:
                logger.info(f"Test {test_id} doesn't have enough data yet ({total_sent}/{test.minimum_sample_size})")
                return None
            
            # Find the best performing variant (by reply rate)
            best_variant = max(test.variants, key=lambda v: v.reply_rate)
            
            # Calculate statistical significance
            significance = self._calculate_statistical_significance(test.variants)
            
            # Calculate improvement
            baseline_variant = test.variants[0]  # Assume first variant is baseline
            improvement = ((best_variant.reply_rate - baseline_variant.reply_rate) / baseline_variant.reply_rate * 100) if baseline_variant.reply_rate > 0 else 0
            
            # Generate recommendation
            recommendation = self._generate_recommendation(test, best_variant, significance)
            
            # Detailed metrics
            detailed_metrics = {
                'variants': [
                    {
                        'name': v.variant_name,
                        'sent': v.sent_count,
                        'open_rate': v.open_rate,
                        'click_rate': v.click_rate,
                        'reply_rate': v.reply_rate,
                        'conversion_rate': v.conversion_rate
                    } for v in test.variants
                ],
                'test_duration_days': (datetime.now() - test.start_date).days,
                'total_sent': total_sent
            }
            
            results = TestResults(
                test_id=test_id,
                winning_variant=best_variant,
                confidence_level=test.confidence_level,
                statistical_significance=significance,
                improvement_percentage=improvement,
                recommendation=recommendation,
                detailed_metrics=detailed_metrics
            )
            
            # Update test with results
            test.winning_variant_id = best_variant.variant_id
            test.statistical_significance = significance
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing test results for {test_id}: {str(e)}")
            return None
    
    def stop_test(self, test_id: str, reason: str = "Manual stop") -> bool:
        """
        Stop a running test
        """
        try:
            if test_id not in self.active_tests:
                return False
            
            test = self.active_tests[test_id]
            test.status = TestStatus.COMPLETED
            test.end_date = datetime.now()
            
            # Move to completed tests
            self.completed_tests[test_id] = test
            del self.active_tests[test_id]
            
            logger.info(f"Stopped test {test_id}: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping test {test_id}: {str(e)}")
            return False
    
    def get_test_status(self, test_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current status of a test
        """
        test = self.active_tests.get(test_id) or self.completed_tests.get(test_id)
        if not test:
            return None
        
        return {
            'test_id': test.test_id,
            'test_name': test.test_name,
            'status': test.status.value,
            'start_date': test.start_date.isoformat(),
            'end_date': test.end_date.isoformat() if test.end_date else None,
            'variants': [
                {
                    'variant_id': v.variant_id,
                    'variant_name': v.variant_name,
                    'sent_count': v.sent_count,
                    'open_rate': v.open_rate,
                    'reply_rate': v.reply_rate,
                    'conversion_rate': v.conversion_rate
                } for v in test.variants
            ],
            'total_sent': sum(v.sent_count for v in test.variants),
            'minimum_sample_size': test.minimum_sample_size
        }
    
    def _check_test_completion(self, test_id: str):
        """
        Check if test should be completed automatically
        """
        test = self.active_tests.get(test_id)
        if not test or test.status != TestStatus.RUNNING:
            return
        
        # Check if we've reached minimum sample size and duration
        total_sent = sum(v.sent_count for v in test.variants)
        duration_met = datetime.now() >= test.end_date
        sample_size_met = total_sent >= test.minimum_sample_size
        
        if duration_met and sample_size_met:
            # Analyze results
            results = self.analyze_test_results(test_id)
            if results and results.statistical_significance >= test.confidence_level:
                self.stop_test(test_id, "Reached statistical significance")
            elif duration_met:
                self.stop_test(test_id, "Reached maximum duration")
    
    def _calculate_statistical_significance(self, variants: List[TestVariant]) -> float:
        """
        Calculate statistical significance using z-test for proportions
        """
        try:
            if len(variants) < 2:
                return 0.0
            
            # Use reply rate as the primary metric
            baseline = variants[0]
            best_variant = max(variants[1:], key=lambda v: v.reply_rate)
            
            if baseline.sent_count == 0 or best_variant.sent_count == 0:
                return 0.0
            
            p1 = baseline.reply_rate
            p2 = best_variant.reply_rate
            n1 = baseline.sent_count
            n2 = best_variant.sent_count
            
            # Pooled proportion
            p_pool = (baseline.replied_count + best_variant.replied_count) / (n1 + n2)
            
            # Standard error
            se = (p_pool * (1 - p_pool) * (1/n1 + 1/n2)) ** 0.5
            
            if se == 0:
                return 0.0
            
            # Z-score
            z = abs(p2 - p1) / se
            
            # Convert z-score to confidence level (approximation)
            # For 95% confidence, z should be >= 1.96
            confidence = min(0.99, max(0.0, (z - 1.96) / 1.96 * 0.95 + 0.95))
            
            return confidence
            
        except Exception as e:
            logger.error(f"Error calculating statistical significance: {str(e)}")
            return 0.0
    
    def _generate_recommendation(self, test: ABTest, winning_variant: TestVariant, significance: float) -> str:
        """
        Generate recommendation based on test results
        """
        if significance >= test.confidence_level:
            return f"Implement {winning_variant.variant_name} - statistically significant improvement with {significance:.1%} confidence."
        elif significance >= 0.80:
            return f"Consider implementing {winning_variant.variant_name} - shows promise but needs more data for statistical significance."
        else:
            return "No clear winner detected. Consider running the test longer or trying different variations."
    
    def get_active_tests(self) -> List[Dict[str, Any]]:
        """
        Get all active tests
        """
        return [self.get_test_status(test_id) for test_id in self.active_tests.keys()]
    
    def get_completed_tests(self) -> List[Dict[str, Any]]:
        """
        Get all completed tests
        """
        return [self.get_test_status(test_id) for test_id in self.completed_tests.keys()]
    
    def create_subject_line_test(self, base_template: OutreachTemplate, subject_variations: List[str]) -> ABTest:
        """
        Create a subject line A/B test
        """
        templates = []
        for i, subject in enumerate(subject_variations):
            template = OutreachTemplate(
                template_id=f"{base_template.template_id}_subject_{i+1}",
                template_type=base_template.template_type,
                subject_line=subject,
                email_body=base_template.email_body,
                call_to_action=base_template.call_to_action,
                tone=base_template.tone,
                personalization_data=base_template.personalization_data,
                created_at=datetime.now()
            )
            templates.append(template)
        
        return self.create_ab_test(
            test_name=f"Subject Line Test - {base_template.template_type}",
            test_type=TestType.SUBJECT_LINE,
            templates=templates
        )
    
    def create_tone_test(self, templates_by_tone: Dict[str, OutreachTemplate]) -> ABTest:
        """
        Create a tone variation A/B test
        """
        templates = list(templates_by_tone.values())
        
        return self.create_ab_test(
            test_name="Tone Variation Test",
            test_type=TestType.TONE,
            templates=templates
        )

# Global instance
ab_testing_service = ABTestingService()

def create_ab_test(test_name: str,
                  test_type: str,
                  templates: List[OutreachTemplate],
                  **kwargs) -> ABTest:
    """
    Create a new A/B test
    """
    test_type_enum = TestType(test_type)
    return ab_testing_service.create_ab_test(test_name, test_type_enum, templates, **kwargs)

def start_ab_test(test_id: str) -> bool:
    """
    Start an A/B test
    """
    return ab_testing_service.start_test(test_id)

def assign_test_variant(test_id: str, candidate_id: str) -> Optional[TestVariant]:
    """
    Assign a candidate to a test variant
    """
    return ab_testing_service.assign_variant(test_id, candidate_id)

def record_test_event(test_id: str, variant_id: str, event_type: str) -> bool:
    """
    Record an event for a test variant
    """
    return ab_testing_service.record_event(test_id, variant_id, event_type)

def analyze_ab_test(test_id: str) -> Optional[TestResults]:
    """
    Analyze A/B test results
    """
    return ab_testing_service.analyze_test_results(test_id)

def get_test_status(test_id: str) -> Optional[Dict[str, Any]]:
    """
    Get test status
    """
    return ab_testing_service.get_test_status(test_id)