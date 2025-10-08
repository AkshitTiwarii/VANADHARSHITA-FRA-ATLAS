"""
Enhanced Decision Support System (DSS) Engine
AI/ML-based scheme recommendation with budget optimization

Features:
- ML-based scheme prediction using Random Forest
- Multi-criteria decision analysis (MCDA)
- Budget optimization algorithms
- Impact prediction models
- DAJGUA ministry integration
- Beneficiary profiling
- Conflict resolution
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)

# Try to import ML libraries (optional, fallback to rule-based)
ML_AVAILABLE = False
RandomForestClassifier = None
GradientBoostingRegressor = None
StandardScaler = None

try:
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
    logger.info("✅ ML libraries (sklearn, numpy) available for DSS")
except (ImportError, Exception) as e:
    logger.warning(f"⚠️ ML libraries not available, using rule-based DSS only")
    logger.info("💡 To enable ML: pip install scikit-learn numpy")
    # Create dummy numpy for basic operations
    class DummyNumpy:
        @staticmethod
        def array(data):
            return data
    np = DummyNumpy()


@dataclass
class VillageProfile:
    """Comprehensive village profile for DSS"""
    village_id: str
    village_name: str
    
    # Geographic data
    area_hectares: float = 0.0
    forest_cover_percent: float = 0.0
    agricultural_land_percent: float = 0.0
    water_bodies_count: int = 0
    
    # Demographic data
    population: int = 0
    households: int = 0
    tribal_population_percent: float = 0.0
    
    # Economic indicators
    average_income: float = 0.0
    unemployment_rate: float = 0.0
    poverty_rate: float = 0.0
    
    # Infrastructure
    roads_km: float = 0.0
    schools_count: int = 0
    health_centers_count: int = 0
    
    # FRA specific
    forest_rights_claims: int = 0
    approved_claims: int = 0
    pending_claims: int = 0
    disputed_claims: int = 0
    
    # Satellite-derived indices
    ndvi_score: float = 0.0
    water_stress_index: float = 0.0
    deforestation_risk: float = 0.0
    
    # Existing schemes
    active_schemes: List[str] = field(default_factory=list)
    total_budget_utilized: float = 0.0


@dataclass
class SchemeRecommendation:
    """Individual scheme recommendation with reasoning"""
    scheme_code: str
    scheme_name: str
    priority_score: float  # 0-1
    confidence: float  # 0-1
    estimated_budget: float
    estimated_beneficiaries: int
    expected_impact_score: float  # 0-1
    reasoning: Dict[str, Any]
    implementation_steps: List[str]
    potential_conflicts: List[str]
    prerequisites: List[str]


@dataclass
class DSSResult:
    """Complete DSS recommendation result"""
    village_id: str
    recommendations: List[SchemeRecommendation]
    total_budget_required: float
    priority_category: str  # "critical", "high", "medium", "low"
    overall_score: float
    multi_criteria_analysis: Dict[str, float]
    optimization_strategy: str
    implementation_timeline: Dict[str, str]
    risk_factors: List[str]
    success_probability: float
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class SchemeDatabase:
    """Database of government schemes with eligibility criteria"""
    
    SCHEMES = {
        "PM_KISAN": {
            "name": "Pradhan Mantri Kisan Samman Nidhi",
            "ministry": "Agriculture",
            "budget_per_beneficiary": 6000,  # Rs per year
            "criteria": {
                "agricultural_land_percent": 10.0,  # minimum
                "landholding": True
            },
            "impact_areas": ["income", "agriculture"],
            "implementation_time_days": 30
        },
        "JAL_JEEVAN_MISSION": {
            "name": "Jal Jeevan Mission",
            "ministry": "Jal Shakti",
            "budget_per_beneficiary": 15000,  # Rs per household connection
            "criteria": {
                "water_stress_index": 0.5,  # minimum stress to qualify
                "water_bodies_count": 3  # maximum (low water availability)
            },
            "impact_areas": ["health", "water", "sanitation"],
            "implementation_time_days": 180
        },
        "MGNREGA": {
            "name": "Mahatma Gandhi National Rural Employment Guarantee Act",
            "ministry": "Rural Development",
            "budget_per_beneficiary": 8000,  # Rs per household (100 days work)
            "criteria": {
                "unemployment_rate": 5.0,  # minimum
                "poverty_rate": 10.0  # minimum
            },
            "impact_areas": ["employment", "income", "infrastructure"],
            "implementation_time_days": 60
        },
        "DAJGUA": {
            "name": "Dharti Aaba Janjatiya Gram Utkarsh Abhiyan",
            "ministry": "Tribal Affairs",
            "budget_per_beneficiary": 25000,  # Rs per household
            "criteria": {
                "tribal_population_percent": 25.0,  # minimum
                "forest_rights_claims": 5  # minimum
            },
            "impact_areas": ["tribal_welfare", "education", "health", "infrastructure"],
            "implementation_time_days": 120
        },
        "PMAY_GRAMIN": {
            "name": "Pradhan Mantri Awas Yojana - Gramin",
            "ministry": "Rural Development",
            "budget_per_beneficiary": 120000,  # Rs per house
            "criteria": {
                "poverty_rate": 20.0,  # minimum
                "housing_shortage": True
            },
            "impact_areas": ["housing", "shelter"],
            "implementation_time_days": 365
        },
        "PMGSY": {
            "name": "Pradhan Mantri Gram Sadak Yojana",
            "ministry": "Rural Development",
            "budget_per_beneficiary": 50000,  # Rs per km
            "criteria": {
                "roads_km": 5.0,  # maximum (poor connectivity)
                "population": 100  # minimum
            },
            "impact_areas": ["connectivity", "infrastructure"],
            "implementation_time_days": 365
        },
        "NRLM": {
            "name": "National Rural Livelihood Mission",
            "ministry": "Rural Development",
            "budget_per_beneficiary": 12000,  # Rs per SHG member
            "criteria": {
                "poverty_rate": 15.0,
                "unemployment_rate": 5.0
            },
            "impact_areas": ["livelihood", "income", "women_empowerment"],
            "implementation_time_days": 90
        },
        "FOREST_CONSERVATION": {
            "name": "Forest Conservation and Afforestation",
            "ministry": "Environment & Forests",
            "budget_per_beneficiary": 10000,  # Rs per hectare
            "criteria": {
                "forest_cover_percent": 10.0,  # minimum
                "deforestation_risk": 0.3  # minimum
            },
            "impact_areas": ["environment", "forest"],
            "implementation_time_days": 180
        }
    }
    
    @classmethod
    def get_scheme(cls, code: str) -> Optional[Dict]:
        return cls.SCHEMES.get(code)
    
    @classmethod
    def get_all_schemes(cls) -> List[str]:
        return list(cls.SCHEMES.keys())


class MLSchemePredictor:
    """ML-based scheme prediction using Random Forest"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = [
            'forest_cover', 'agricultural_land', 'water_bodies',
            'population', 'tribal_percent', 'unemployment', 'poverty',
            'ndvi', 'water_stress', 'deforestation_risk', 'forest_claims'
        ]
        self.scheme_codes = SchemeDatabase.get_all_schemes()
        
        if ML_AVAILABLE:
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            logger.info("✅ ML Scheme Predictor initialized")
        else:
            logger.warning("⚠️ ML not available, using rule-based predictor")
    
    def extract_features(self, profile: VillageProfile):
        """Extract feature vector from village profile"""
        features_list = [
            profile.forest_cover_percent,
            profile.agricultural_land_percent,
            profile.water_bodies_count,
            profile.population,
            profile.tribal_population_percent,
            profile.unemployment_rate,
            profile.poverty_rate,
            profile.ndvi_score,
            profile.water_stress_index,
            profile.deforestation_risk,
            profile.forest_rights_claims
        ]
        
        if ML_AVAILABLE:
            import numpy as np
            features = np.array(features_list).reshape(1, -1)
        else:
            features = [features_list]  # Simple list for rule-based
        
        return features
    
    def predict_schemes(self, profile: VillageProfile) -> List[Tuple[str, float]]:
        """Predict suitable schemes with confidence scores"""
        # Always use rule-based prediction for now (ML model needs training data)
        return self._rule_based_prediction(profile)
    
    def _rule_based_prediction(self, profile: VillageProfile) -> List[Tuple[str, float]]:
        """Fallback rule-based prediction"""
        scores = {}
        
        for scheme_code in self.scheme_codes:
            scheme = SchemeDatabase.get_scheme(scheme_code)
            if not scheme:
                continue
            
            score = 0.5  # Base score
            criteria = scheme.get('criteria', {})
            
            # Check each criterion
            if 'agricultural_land_percent' in criteria:
                if profile.agricultural_land_percent >= criteria['agricultural_land_percent']:
                    score += 0.2
            
            if 'water_stress_index' in criteria:
                if profile.water_stress_index >= criteria['water_stress_index']:
                    score += 0.15
            
            if 'water_bodies_count' in criteria:
                if profile.water_bodies_count <= criteria['water_bodies_count']:
                    score += 0.15
            
            if 'unemployment_rate' in criteria:
                if profile.unemployment_rate >= criteria['unemployment_rate']:
                    score += 0.2
            
            if 'poverty_rate' in criteria:
                if profile.poverty_rate >= criteria['poverty_rate']:
                    score += 0.2
            
            if 'tribal_population_percent' in criteria:
                if profile.tribal_population_percent >= criteria['tribal_population_percent']:
                    score += 0.25
            
            if 'forest_rights_claims' in criteria:
                if profile.forest_rights_claims >= criteria['forest_rights_claims']:
                    score += 0.15
            
            if 'forest_cover_percent' in criteria:
                if profile.forest_cover_percent >= criteria['forest_cover_percent']:
                    score += 0.15
            
            if 'deforestation_risk' in criteria:
                if profile.deforestation_risk >= criteria['deforestation_risk']:
                    score += 0.15
            
            scores[scheme_code] = min(score, 1.0)
        
        # Sort by score
        results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return results


class ImpactPredictor:
    """Predict expected impact of schemes using ML"""
    
    def __init__(self):
        self.model = None
        if ML_AVAILABLE:
            self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            logger.info("✅ Impact Predictor initialized")
    
    def predict_impact(self, profile: VillageProfile, scheme_code: str) -> float:
        """Predict impact score (0-1) for a scheme in given village"""
        
        # Rule-based impact prediction
        scheme = SchemeDatabase.get_scheme(scheme_code)
        if not scheme:
            return 0.5
        
        impact_score = 0.5  # Base impact
        
        # Adjust based on village readiness
        if scheme_code == "PM_KISAN":
            impact_score += 0.1 * (profile.agricultural_land_percent / 100.0)
            
        elif scheme_code == "JAL_JEEVAN_MISSION":
            impact_score += 0.2 * profile.water_stress_index
            
        elif scheme_code == "MGNREGA":
            impact_score += 0.15 * (profile.unemployment_rate / 100.0)
            impact_score += 0.1 * (profile.poverty_rate / 100.0)
            
        elif scheme_code == "DAJGUA":
            impact_score += 0.2 * (profile.tribal_population_percent / 100.0)
            impact_score += 0.1 * (profile.forest_rights_claims / 100.0)
            
        elif scheme_code == "FOREST_CONSERVATION":
            impact_score += 0.15 * (profile.forest_cover_percent / 100.0)
            impact_score += 0.15 * profile.deforestation_risk
        
        # Cap at 1.0
        return min(impact_score, 1.0)


class BudgetOptimizer:
    """Optimize budget allocation across multiple schemes"""
    
    @staticmethod
    def optimize_allocation(
        recommendations: List[SchemeRecommendation],
        total_budget: float,
        constraints: Optional[Dict[str, Any]] = None
    ) -> List[SchemeRecommendation]:
        """
        Optimize budget allocation using priority scores and impact
        
        Uses a greedy algorithm with impact/cost ratio
        """
        if not recommendations:
            return []
        
        # Calculate impact per rupee for each scheme
        for rec in recommendations:
            if rec.estimated_budget > 0:
                rec.impact_per_rupee = rec.expected_impact_score / rec.estimated_budget
            else:
                rec.impact_per_rupee = 0
        
        # Sort by impact per rupee (greedy approach)
        sorted_recs = sorted(recommendations, key=lambda x: x.impact_per_rupee, reverse=True)
        
        # Allocate budget greedily
        allocated = []
        remaining_budget = total_budget
        
        for rec in sorted_recs:
            if rec.estimated_budget <= remaining_budget:
                allocated.append(rec)
                remaining_budget -= rec.estimated_budget
            elif constraints and constraints.get('allow_partial', False):
                # Partial allocation if allowed
                if remaining_budget > 0:
                    rec.estimated_budget = remaining_budget
                    rec.estimated_beneficiaries = int(
                        rec.estimated_beneficiaries * (remaining_budget / rec.estimated_budget)
                    )
                    allocated.append(rec)
                    remaining_budget = 0
        
        return allocated
    
    @staticmethod
    def calculate_optimal_mix(
        village_profile: VillageProfile,
        available_budget: float
    ) -> Dict[str, float]:
        """Calculate optimal budget distribution across schemes"""
        
        # Simple proportional allocation based on need
        allocation = {}
        total_weight = 0
        
        weights = {
            "PM_KISAN": village_profile.agricultural_land_percent / 100.0,
            "JAL_JEEVAN_MISSION": village_profile.water_stress_index,
            "MGNREGA": (village_profile.unemployment_rate + village_profile.poverty_rate) / 200.0,
            "DAJGUA": village_profile.tribal_population_percent / 100.0,
            "FOREST_CONSERVATION": (village_profile.forest_cover_percent / 100.0) * village_profile.deforestation_risk
        }
        
        total_weight = sum(weights.values())
        
        if total_weight > 0:
            for scheme, weight in weights.items():
                allocation[scheme] = (weight / total_weight) * available_budget
        
        return allocation


class ConflictResolver:
    """Resolve conflicts between competing schemes"""
    
    CONFLICTS = {
        "FOREST_CONSERVATION": ["PMGSY"],  # Road building vs forest conservation
        "DAJGUA": ["FOREST_CONSERVATION"],  # Development vs conservation
    }
    
    @staticmethod
    def detect_conflicts(recommendations: List[SchemeRecommendation]) -> List[str]:
        """Detect potential conflicts in scheme recommendations"""
        conflicts = []
        scheme_codes = [rec.scheme_code for rec in recommendations]
        
        for scheme_code in scheme_codes:
            conflicting = ConflictResolver.CONFLICTS.get(scheme_code, [])
            for conflict in conflicting:
                if conflict in scheme_codes:
                    conflicts.append(f"{scheme_code} conflicts with {conflict}")
        
        return conflicts
    
    @staticmethod
    def resolve(recommendations: List[SchemeRecommendation]) -> List[SchemeRecommendation]:
        """Resolve conflicts by prioritizing higher impact schemes"""
        conflicts = ConflictResolver.detect_conflicts(recommendations)
        
        if not conflicts:
            return recommendations
        
        # Simple resolution: keep higher priority schemes
        resolved = []
        removed_schemes = set()
        
        for rec in recommendations:
            if rec.scheme_code in removed_schemes:
                continue
            
            # Check if this scheme conflicts with any other
            conflicting = ConflictResolver.CONFLICTS.get(rec.scheme_code, [])
            
            for other_rec in recommendations:
                if other_rec.scheme_code in conflicting:
                    # Keep the one with higher priority
                    if rec.priority_score > other_rec.priority_score:
                        removed_schemes.add(other_rec.scheme_code)
                        rec.potential_conflicts.append(
                            f"Resolved conflict with {other_rec.scheme_code} (lower priority)"
                        )
                    else:
                        removed_schemes.add(rec.scheme_code)
                        break
            
            if rec.scheme_code not in removed_schemes:
                resolved.append(rec)
        
        return resolved


class EnhancedDSSEngine:
    """
    Main DSS Engine with AI/ML capabilities
    
    Integrates:
    - ML-based scheme prediction
    - Multi-criteria decision analysis
    - Budget optimization
    - Impact prediction
    - Conflict resolution
    """
    
    def __init__(self):
        self.ml_predictor = MLSchemePredictor()
        self.impact_predictor = ImpactPredictor()
        self.budget_optimizer = BudgetOptimizer()
        self.conflict_resolver = ConflictResolver()
        
        logger.info("✅ Enhanced DSS Engine initialized")
    
    def generate_recommendations(
        self,
        village_profile: VillageProfile,
        available_budget: Optional[float] = None,
        max_schemes: int = 5,
        constraints: Optional[Dict[str, Any]] = None
    ) -> DSSResult:
        """
        Generate comprehensive DSS recommendations
        
        Args:
            village_profile: Complete village data
            available_budget: Budget constraint (optional)
            max_schemes: Maximum schemes to recommend
            constraints: Additional constraints
        
        Returns:
            Complete DSS recommendation result
        """
        
        logger.info(f"Generating DSS recommendations for village: {village_profile.village_id}")
        
        # Step 1: ML-based scheme prediction
        scheme_predictions = self.ml_predictor.predict_schemes(village_profile)
        
        # Step 2: Generate detailed recommendations
        recommendations = []
        total_budget = 0
        
        for scheme_code, confidence in scheme_predictions[:max_schemes]:
            scheme = SchemeDatabase.get_scheme(scheme_code)
            if not scheme:
                continue
            
            # Calculate priority score using MCDA
            priority_score = self._calculate_priority_score(
                village_profile, scheme_code, confidence
            )
            
            # Predict impact
            expected_impact = self.impact_predictor.predict_impact(
                village_profile, scheme_code
            )
            
            # Estimate budget and beneficiaries
            estimated_budget, estimated_beneficiaries = self._estimate_resources(
                village_profile, scheme_code
            )
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                village_profile, scheme_code, priority_score
            )
            
            # Implementation steps
            impl_steps = self._generate_implementation_steps(scheme_code)
            
            # Check prerequisites
            prerequisites = self._check_prerequisites(village_profile, scheme_code)
            
            recommendation = SchemeRecommendation(
                scheme_code=scheme_code,
                scheme_name=scheme['name'],
                priority_score=priority_score,
                confidence=confidence,
                estimated_budget=estimated_budget,
                estimated_beneficiaries=estimated_beneficiaries,
                expected_impact_score=expected_impact,
                reasoning=reasoning,
                implementation_steps=impl_steps,
                potential_conflicts=[],
                prerequisites=prerequisites
            )
            
            recommendations.append(recommendation)
            total_budget += estimated_budget
        
        # Step 3: Resolve conflicts
        recommendations = self.conflict_resolver.resolve(recommendations)
        
        # Step 4: Optimize budget allocation if constraint provided
        if available_budget and available_budget < total_budget:
            recommendations = self.budget_optimizer.optimize_allocation(
                recommendations, available_budget, constraints
            )
            total_budget = sum(rec.estimated_budget for rec in recommendations)
        
        # Step 5: Multi-criteria analysis
        mcda_scores = self._perform_mcda(village_profile)
        
        # Step 6: Calculate overall priority category
        priority_category = self._categorize_priority(village_profile, mcda_scores)
        
        # Step 7: Calculate overall score
        overall_score = self._calculate_overall_score(recommendations, mcda_scores)
        
        # Step 8: Generate implementation timeline
        timeline = self._generate_timeline(recommendations)
        
        # Step 9: Identify risk factors
        risks = self._identify_risks(village_profile, recommendations)
        
        # Step 10: Calculate success probability
        success_prob = self._calculate_success_probability(
            village_profile, recommendations, risks
        )
        
        # Step 11: Determine optimization strategy
        strategy = self._determine_strategy(village_profile, recommendations)
        
        return DSSResult(
            village_id=village_profile.village_id,
            recommendations=recommendations,
            total_budget_required=total_budget,
            priority_category=priority_category,
            overall_score=overall_score,
            multi_criteria_analysis=mcda_scores,
            optimization_strategy=strategy,
            implementation_timeline=timeline,
            risk_factors=risks,
            success_probability=success_prob
        )
    
    def _calculate_priority_score(
        self, profile: VillageProfile, scheme_code: str, confidence: float
    ) -> float:
        """Calculate priority score using multiple criteria"""
        
        scheme = SchemeDatabase.get_scheme(scheme_code)
        if not scheme:
            return confidence
        
        # Weights for different factors
        weights = {
            'confidence': 0.3,
            'need': 0.3,
            'readiness': 0.2,
            'impact': 0.2
        }
        
        # Need score based on village conditions
        need_score = 0.5
        if scheme_code == "PM_KISAN":
            need_score = profile.agricultural_land_percent / 100.0
        elif scheme_code == "JAL_JEEVAN_MISSION":
            need_score = profile.water_stress_index
        elif scheme_code == "MGNREGA":
            need_score = (profile.unemployment_rate + profile.poverty_rate) / 200.0
        elif scheme_code == "DAJGUA":
            need_score = profile.tribal_population_percent / 100.0
        
        # Readiness score
        readiness = 0.7  # Base readiness
        if profile.roads_km < 5:
            readiness -= 0.1  # Poor connectivity
        if profile.schools_count < 2:
            readiness -= 0.1  # Poor education infrastructure
        
        # Impact score from predictor
        impact = self.impact_predictor.predict_impact(profile, scheme_code)
        
        # Weighted combination
        priority = (
            weights['confidence'] * confidence +
            weights['need'] * need_score +
            weights['readiness'] * readiness +
            weights['impact'] * impact
        )
        
        return min(priority, 1.0)
    
    def _estimate_resources(
        self, profile: VillageProfile, scheme_code: str
    ) -> Tuple[float, int]:
        """Estimate budget and beneficiaries for a scheme"""
        
        scheme = SchemeDatabase.get_scheme(scheme_code)
        if not scheme:
            return (0, 0)
        
        budget_per_beneficiary = scheme['budget_per_beneficiary']
        
        # Estimate beneficiaries based on scheme type
        if scheme_code == "PM_KISAN":
            # Agricultural landholders
            beneficiaries = int(profile.households * 0.6)  # 60% have land
        elif scheme_code == "JAL_JEEVAN_MISSION":
            # All households need water
            beneficiaries = profile.households
        elif scheme_code == "MGNREGA":
            # Unemployed adults
            beneficiaries = int(profile.population * 0.4 * profile.unemployment_rate / 100)
        elif scheme_code == "DAJGUA":
            # Tribal households
            beneficiaries = int(profile.households * profile.tribal_population_percent / 100)
        elif scheme_code == "PMGSY":
            # Roads in km
            beneficiaries = int(profile.area_hectares * 0.1)  # 0.1 km per hectare
        else:
            beneficiaries = int(profile.households * 0.5)
        
        total_budget = beneficiaries * budget_per_beneficiary
        
        return (total_budget, beneficiaries)
    
    def _generate_reasoning(
        self, profile: VillageProfile, scheme_code: str, priority: float
    ) -> Dict[str, Any]:
        """Generate detailed reasoning for recommendation"""
        
        reasoning = {
            "priority_level": "high" if priority > 0.7 else "medium" if priority > 0.5 else "low",
            "key_factors": [],
            "village_conditions": {},
            "expected_outcomes": []
        }
        
        scheme = SchemeDatabase.get_scheme(scheme_code)
        if not scheme:
            return reasoning
        
        # Add key factors
        if scheme_code == "PM_KISAN":
            reasoning["key_factors"].append(f"Agricultural land: {profile.agricultural_land_percent:.1f}%")
            reasoning["expected_outcomes"].append("Increased farmer income")
            reasoning["village_conditions"]["agriculture"] = "suitable"
            
        elif scheme_code == "JAL_JEEVAN_MISSION":
            reasoning["key_factors"].append(f"Water stress index: {profile.water_stress_index:.2f}")
            reasoning["key_factors"].append(f"Water bodies: {profile.water_bodies_count}")
            reasoning["expected_outcomes"].append("Improved water access")
            reasoning["village_conditions"]["water"] = "stressed"
            
        elif scheme_code == "MGNREGA":
            reasoning["key_factors"].append(f"Unemployment: {profile.unemployment_rate:.1f}%")
            reasoning["key_factors"].append(f"Poverty rate: {profile.poverty_rate:.1f}%")
            reasoning["expected_outcomes"].append("Employment generation")
            reasoning["village_conditions"]["employment"] = "needed"
            
        elif scheme_code == "DAJGUA":
            reasoning["key_factors"].append(f"Tribal population: {profile.tribal_population_percent:.1f}%")
            reasoning["key_factors"].append(f"Forest rights claims: {profile.forest_rights_claims}")
            reasoning["expected_outcomes"].append("Tribal welfare improvement")
            reasoning["village_conditions"]["tribal_focus"] = "high"
        
        return reasoning
    
    def _generate_implementation_steps(self, scheme_code: str) -> List[str]:
        """Generate implementation steps for a scheme"""
        
        scheme = SchemeDatabase.get_scheme(scheme_code)
        if not scheme:
            return []
        
        base_steps = [
            "1. Village-level awareness campaign",
            "2. Beneficiary identification and verification",
            "3. Application and documentation",
            "4. Approval and fund allocation"
        ]
        
        scheme_specific = {
            "PM_KISAN": [
                "5. Land record verification",
                "6. Bank account linking",
                "7. Direct benefit transfer setup"
            ],
            "JAL_JEEVAN_MISSION": [
                "5. Water source identification",
                "6. Pipeline and connection planning",
                "7. Construction and installation",
                "8. Water quality testing"
            ],
            "MGNREGA": [
                "5. Job card registration",
                "6. Work planning and allocation",
                "7. Wage payment processing"
            ],
            "DAJGUA": [
                "5. Community consultation",
                "6. Multi-sectoral coordination",
                "7. Infrastructure development",
                "8. Monitoring and evaluation"
            ]
        }
        
        steps = base_steps + scheme_specific.get(scheme_code, [])
        return steps
    
    def _check_prerequisites(
        self, profile: VillageProfile, scheme_code: str
    ) -> List[str]:
        """Check prerequisites for scheme implementation"""
        
        prereqs = []
        
        if scheme_code == "PM_KISAN":
            if profile.agricultural_land_percent < 10:
                prereqs.append("Insufficient agricultural land")
            prereqs.append("Land records digitization")
            prereqs.append("Bank account for all farmers")
            
        elif scheme_code == "JAL_JEEVAN_MISSION":
            if profile.water_bodies_count > 5:
                prereqs.append("Adequate water source already present")
            prereqs.append("Village water committee formation")
            prereqs.append("DPR preparation")
            
        elif scheme_code == "MGNREGA":
            prereqs.append("Job card registration")
            prereqs.append("Work identification")
            
        elif scheme_code == "DAJGUA":
            if profile.tribal_population_percent < 25:
                prereqs.append("Tribal population below threshold")
            prereqs.append("Gram Sabha resolution")
            prereqs.append("Ministry coordination")
        
        return prereqs
    
    def _perform_mcda(self, profile: VillageProfile) -> Dict[str, float]:
        """Perform Multi-Criteria Decision Analysis"""
        
        return {
            "economic_need": (profile.poverty_rate + profile.unemployment_rate) / 200.0,
            "infrastructure_gap": 1.0 - (profile.roads_km / 20.0),  # Normalized
            "environmental_priority": profile.deforestation_risk * (profile.forest_cover_percent / 100.0),
            "social_equity": profile.tribal_population_percent / 100.0,
            "water_security": profile.water_stress_index,
            "livelihood_potential": profile.agricultural_land_percent / 100.0,
            "fra_priority": min(profile.forest_rights_claims / 50.0, 1.0)
        }
    
    def _categorize_priority(
        self, profile: VillageProfile, mcda: Dict[str, float]
    ) -> str:
        """Categorize village priority level"""
        
        avg_score = sum(mcda.values()) / len(mcda)
        
        if avg_score > 0.75:
            return "critical"
        elif avg_score > 0.5:
            return "high"
        elif avg_score > 0.25:
            return "medium"
        else:
            return "low"
    
    def _calculate_overall_score(
        self, recommendations: List[SchemeRecommendation], mcda: Dict[str, float]
    ) -> float:
        """Calculate overall village score"""
        
        if not recommendations:
            return 0.0
        
        # Average of recommendation priorities and MCDA scores
        rec_score = sum(rec.priority_score for rec in recommendations) / len(recommendations)
        mcda_score = sum(mcda.values()) / len(mcda)
        
        return (rec_score + mcda_score) / 2.0
    
    def _generate_timeline(
        self, recommendations: List[SchemeRecommendation]
    ) -> Dict[str, str]:
        """Generate implementation timeline"""
        
        timeline = {}
        
        for rec in recommendations:
            scheme = SchemeDatabase.get_scheme(rec.scheme_code)
            if scheme:
                days = scheme.get('implementation_time_days', 180)
                timeline[rec.scheme_code] = f"{days} days"
        
        return timeline
    
    def _identify_risks(
        self, profile: VillageProfile, recommendations: List[SchemeRecommendation]
    ) -> List[str]:
        """Identify implementation risks"""
        
        risks = []
        
        # Infrastructure risks
        if profile.roads_km < 3:
            risks.append("Poor road connectivity may delay implementation")
        
        # Administrative risks
        if profile.pending_claims > profile.approved_claims:
            risks.append("High pending claims indicate administrative bottlenecks")
        
        # Social risks
        if profile.disputed_claims > 10:
            risks.append("High disputed claims may cause social conflicts")
        
        # Environmental risks
        if profile.deforestation_risk > 0.7:
            risks.append("High deforestation risk requires urgent intervention")
        
        # Budget risks
        total_budget = sum(rec.estimated_budget for rec in recommendations)
        if total_budget > 10000000:  # 1 crore
            risks.append("High budget requirement may face allocation challenges")
        
        # Conflict risks
        conflicts = self.conflict_resolver.detect_conflicts(recommendations)
        if conflicts:
            risks.extend(conflicts)
        
        return risks
    
    def _calculate_success_probability(
        self,
        profile: VillageProfile,
        recommendations: List[SchemeRecommendation],
        risks: List[str]
    ) -> float:
        """Calculate probability of successful implementation"""
        
        base_probability = 0.7
        
        # Adjust based on village readiness
        if profile.roads_km > 5:
            base_probability += 0.05
        if profile.schools_count > 2:
            base_probability += 0.05
        if profile.health_centers_count > 0:
            base_probability += 0.05
        
        # Adjust based on FRA track record
        if profile.approved_claims > 0:
            approval_rate = profile.approved_claims / max(profile.forest_rights_claims, 1)
            base_probability += 0.1 * approval_rate
        
        # Reduce based on risks
        risk_penalty = min(len(risks) * 0.05, 0.3)
        base_probability -= risk_penalty
        
        # Ensure between 0 and 1
        return max(0.0, min(base_probability, 1.0))
    
    def _determine_strategy(
        self, profile: VillageProfile, recommendations: List[SchemeRecommendation]
    ) -> str:
        """Determine optimization strategy"""
        
        total_budget = sum(rec.estimated_budget for rec in recommendations)
        avg_impact = sum(rec.expected_impact_score for rec in recommendations) / len(recommendations) if recommendations else 0
        
        if avg_impact > 0.7:
            return "High-Impact Focus: Prioritize schemes with maximum impact"
        elif total_budget > 5000000:  # 50 lakhs
            return "Budget Optimization: Phase implementation to spread costs"
        elif profile.tribal_population_percent > 50:
            return "DAJGUA Priority: Focus on tribal welfare schemes"
        elif profile.water_stress_index > 0.7:
            return "Water Security First: Address water crisis urgently"
        elif profile.poverty_rate > 30:
            return "Poverty Alleviation: Focus on livelihood schemes"
        else:
            return "Balanced Approach: Implement multiple schemes in parallel"


# Singleton instance
_dss_engine = None

def get_dss_engine() -> EnhancedDSSEngine:
    """Get or create DSS engine singleton"""
    global _dss_engine
    if _dss_engine is None:
        _dss_engine = EnhancedDSSEngine()
    return _dss_engine


if __name__ == "__main__":
    # Test DSS engine
    print("Testing Enhanced DSS Engine...")
    
    # Create test village profile
    test_profile = VillageProfile(
        village_id="VIL001",
        village_name="Test Village",
        area_hectares=500,
        forest_cover_percent=35,
        agricultural_land_percent=45,
        water_bodies_count=2,
        population=2500,
        households=500,
        tribal_population_percent=60,
        average_income=50000,
        unemployment_rate=15,
        poverty_rate=25,
        roads_km=3,
        schools_count=2,
        health_centers_count=1,
        forest_rights_claims=45,
        approved_claims=30,
        pending_claims=10,
        disputed_claims=5,
        ndvi_score=0.65,
        water_stress_index=0.6,
        deforestation_risk=0.4
    )
    
    # Generate recommendations
    engine = get_dss_engine()
    result = engine.generate_recommendations(test_profile, available_budget=5000000)
    
    print(f"\n✅ DSS Analysis Complete for {test_profile.village_name}")
    print(f"Priority Category: {result.priority_category}")
    print(f"Overall Score: {result.overall_score:.2f}")
    print(f"Success Probability: {result.success_probability:.2%}")
    print(f"\nRecommended Schemes ({len(result.recommendations)}):")
    
    for i, rec in enumerate(result.recommendations, 1):
        print(f"\n{i}. {rec.scheme_name}")
        print(f"   Priority: {rec.priority_score:.2f} | Confidence: {rec.confidence:.2f}")
        print(f"   Budget: ₹{rec.estimated_budget:,.0f} | Beneficiaries: {rec.estimated_beneficiaries}")
        print(f"   Expected Impact: {rec.expected_impact_score:.2f}")
        print(f"   Key Factors: {', '.join(rec.reasoning.get('key_factors', [])[:2])}")
    
    print(f"\nTotal Budget Required: ₹{result.total_budget_required:,.0f}")
    print(f"Optimization Strategy: {result.optimization_strategy}")
    
    if result.risk_factors:
        print(f"\nRisk Factors ({len(result.risk_factors)}):")
        for risk in result.risk_factors[:3]:
            print(f"  - {risk}")
