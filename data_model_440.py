
from pydantic import Field, BaseModel, ValidationError, ValidationInfo, field_validator, root_validator
from typing import Literal,Union
import pandas as pd
# %% Model for AI training 

class Damage(BaseModel):
    damage_mech: Literal[
        'Corrosion - Connection', 
        'Corrosion - Structure Member', 
        'Fatigue', 
        'Other', 
        'Overloading', 
        'Corrosion of Reinforcement', 
        'Ground Settlement', 
        'Impact', 
        'Overload/Yielding of Reinforcement', 
        'Not listed', 
        'Environmental exposure', 
        'Overloading'
    ]
    type: Literal[
        "Crevice",
        "Localised Corrosion ATM",
        "Pitting",
        "Repititive Cyclic Loading",
        "Construction / Repair Weld Defect",
        "Loose Bolt",
        "Missing Component",
        "No Selection Applicable - Refer to Detailed Defect Description",
        "Other Damage not Covered",
        "Settlement",
        "Unauthorised / Incorrect Modification or Repair",
        "Changed Loading Regime",
        "Impact from Vehicles/Mobile Plant",
        "Unknown",
        "Erosion of Fill",
        "Overload",
        "Subsidence of Fill",
        "Additional Components",
        "Missing components",
        "Not listed",
        "Timber Rotting",
        "Water Damage",
        "Loose Bolt",
        "Other Damage not Covered",
        "Impact from Miscellanous"
    ]
    condition: Literal[
        "Level 1",
        "Level 2",
        "Level 3",
        "Level 4",
        "Level 5",
        "Permanent Deformation",
        "Ruptured / Buckled / Full Section Loss",
        "In Corroded Area - Cracked",
        "In Corroded Area - Ruptured",
        "Missing Bolt(s)",
        "Missing Clip(s)",
        "Missing Member(s)",
        "Other Condition - Refer to Detailed Defect Description",
        "Ruptured / Buckled",
        "Condition Rating 1",
        "Condition Rating 2",
        "Condition Rating 3",
        "Condition Rating 4",
        "Condition Rating 5",
        "Condition Rating 6",
        "Condition Rating 7",
        "Not listed",
        "Major",
        "Minor",
        "Full Member Permanent Deformation (>1% of Centreline)",
        "Local Member Permanent Deformation"
    ]


class Location(BaseModel):
    facility: Literal['BHP Nickel West'] = 'BHP Nickel West'
    area: Literal[
        "Area 1",
        "Utilities",
        "Reduction",
        "Leach"
    ]
    asset: str = Field(default='Asset code or reference.')
    component: str = Field(default='Component of the asset where the defect is found.')
    location: str = Field(default='Detailed location of the defect.')
    date: str = Field(default="")


class RiskAssessment(BaseModel):
    detailed_description: str = Field(default='Defect detailed description.')
    final_failure_mode: str = Field(default='')
    final_failure_mode_add: str = Field(default='')
    effect: str = Field(default='Effect to the equipment due to component failure.')



class Impact(BaseModel):
    impact: Literal[
        "Health & Safety",
        "Environment",
        "Community",
        "Reputation & Legal",
        "Financial"
        ]
    severity: Literal[
        "Severity Level 1",
        "Severity Level 2",
        "Severity Level 3",
        "Severity Level 4",
        "Severity Level 5",

    ]
    consequence: str = Field(default="Calculated consequence from AIMS standard")
    reason: str = Field(default="")
    reason_add: str = Field(default="")
    likelihood: Literal[
        "Almost Certain (Failure within 1 Year)",
        "Likely (Failure within 2 Years)",
        "Possible (Failure within 5 Years)",
        "Unlikely (Failure within 20 Years)",
        "Rare (Failure within 50 Years)"
    ]
    priority: Literal[
        "P1",
        "P2",
        "P3",
        "P4"
    ]

class Methodology(BaseModel):
    required_action: Literal[
        "Monitor through routine inspections.",
        "Remediate within two years (24 months) from last inspection submission date.",
        "Remediate within one year (12 months) from last inspection submission date.",
        "Remediation plan to be actioned immediately."
    ]
    isolation: Literal["Yes", "No", 1, 0]
    monitor: Literal["Yes", "No", 1, 0]
    constraints: Literal["On-Line", "Off-Line"]
    type_of_work: Literal[
        "Actioned during Inspection",
        "Blast & Paint Repair",
        "Condition Monitoring",
        "Deformation Monitorin",
        "Engineering Repair Methodology Required",
        "Fatigue Assessment",
        "Load Rating",
        "Localised Steel / Joint Repair",
        "Maintenance Repair",
        "Standard Repair Detail",
        "Temporary Propping"
    ]
    access: str = Field(default="Access requirements.")
    permits: str = Field(default="Permits required.")
    verification: Literal[
        "Competent 3rd Party",
        "Competent Engineer",
        "Competent Supervisor"
    ]
    work_requirements: str = Field(default="Work requirements.")
    corrective_action: str = Field(default="")
    corrective_action_add: str = Field(default="")
    
    @field_validator('monitor')
    def convert_monitor(cls, value):
        return convert_boolean(value)
    
    @field_validator('monitor')
    def convert_isolation(cls, value):
        return convert_boolean(value)



class InspectionReport(BaseModel):
    damage: Damage
    location: Location
    risk_assessment: RiskAssessment
    impact: Impact
    methodology: Methodology

    def to_custom_dict(self) -> dict:
        return {
            "damage_mech": self.damage.damage_mech,
            "type": self.damage.type,
            "condition": self.damage.condition,
            "facility": self.location,
            "area": self.location.area,
            "asset": self.location.asset,
            "component": self.location.component,
            "location_description": self.location.location,
            "date": self.location.date,
            "detailed_description": self.risk_assessment.detailed_description,
            "failure_mode": self.risk_assessment.final_failure_mode,
            "failure_mode_add": self.risk_assessment.final_failure_mode_add,
            "listpicker_15": self.risk_assessment.effect,
            "impact": self.impact.impact,
            "severity": self.impact.severity,
            "consequence": self.impact.consequence,
            "reason": self.impact.reason,
            "reason_add": self.impact.reason_add,
            "likelihood": self.impact.likelihood,
            "priorisation": self.impact.priority,
            "required_action": self.methodology.required_action,
            "isolation": self.methodology.isolation,
            "monitor": self.methodology.monitor,
            "constraints": self.methodology.constraints,
            "work_to_be_completed": self.methodology.type_of_work,
            "corrective_action": self.methodology.corrective_action,
            "corrective_action_add": self.methodology.corrective_action_add,
            "access": self.methodology.access,
            "permits": self.methodology.permits,
            "verification_level": self.methodology.verification,
            "work_requirements": self.methodology.work_requirements
        }
    
    
    


def convert_boolean(v: int) -> str:
    if v == 1:
        return "Yes"
    elif v == 0:
        return "No"
    elif isinstance(v, str) and v in ["Yes", "No"]:
        return v
    else:
        raise ValidationError(f"Invalid value for monitor: {v}")
         