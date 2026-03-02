"""
Lease summary schema: required and optional fields matching the assignment template.
"""
from typing import Optional
from pydantic import BaseModel, Field


class LeaseSummary(BaseModel):
    """Structured lease summary for display and export."""

    # Required fields (assignment minimum)
    tenant: str = Field(description="Tenant name(s)")
    landlord: str = Field(description="Landlord name")
    lease_start_date: str = Field(description="Lease start / commencement date")
    lease_end_date: str = Field(description="Lease end / termination date")
    rent_amount: str = Field(description="Rent amount and basis (e.g. monthly, per SF)")
    renewal_options: str = Field(description="Renewal options")
    termination_clauses: str = Field(description="Termination clauses summary")
    security_deposit: str = Field(description="Security deposit amount")
    special_provisions: str = Field(description="Special provisions summary")

    # Optional / additional template fields
    premises_address: Optional[str] = Field(default=None, description="Leased premises address")
    permitted_use: Optional[str] = Field(default=None, description="Permitted use")
    rent_commencement_date: Optional[str] = Field(default=None, description="Rent commencement date")
    cam_tax_insurance: Optional[str] = Field(default=None, description="CAM / Tax / Insurance")
    advanced_rental: Optional[str] = Field(default=None, description="Advanced rental if any")
    lease_term: Optional[str] = Field(default=None, description="Lease term (e.g. 5 years)")
    trade_name: Optional[str] = Field(default=None, description="Tenant trade name / DBA")
    approximate_size_sqft: Optional[str] = Field(default=None, description="Approximate size in square feet")

    # Additional optional fields (LLM-filled; some have rule-based fallbacks)
    landlord_address: Optional[str] = Field(default=None, description="Full address of landlord")
    tenant_address: Optional[str] = Field(default=None, description="Full address of tenant")
    guarantor: Optional[str] = Field(default=None, description="Guarantor name or entity if any")
    execution_date: Optional[str] = Field(default=None, description="Date lease was executed or signed")
    option_notice_period: Optional[str] = Field(default=None, description="Notice period to exercise renewal option")
    option_rent: Optional[str] = Field(default=None, description="Rent for renewal option (e.g. fair market, formula)")
    insurance_requirements: Optional[str] = Field(default=None, description="Insurance obligations (e.g. liability, property)")
    assignment_subletting: Optional[str] = Field(default=None, description="Summary of assignment or subletting rights")
    default_remedies: Optional[str] = Field(default=None, description="Summary of default and remedies (e.g. cure period, termination)")
    parking: Optional[str] = Field(default=None, description="Parking rights or allocation")
    signage: Optional[str] = Field(default=None, description="Signage rights or restrictions")
    broker: Optional[str] = Field(default=None, description="Broker or listing agent if mentioned")
    additional_terms_from_document: Optional[str] = Field(
        default=None,
        description="Any other significant lease terms, clauses, or data in the document not covered by the schema fields. Format as one item per line: 'Label: value'.",
    )

    def to_display_dict(self) -> dict:
        """For Streamlit display: label -> value."""
        return {
            "Tenant": self.tenant,
            "Landlord": self.landlord,
            "Lease Start Date": self.lease_start_date,
            "Lease End Date": self.lease_end_date,
            "Rent Amount": self.rent_amount,
            "Renewal Options": self.renewal_options,
            "Termination Clauses": self.termination_clauses,
            "Security Deposit": self.security_deposit,
            "Special Provisions": self.special_provisions,
            "Premises Address": self.premises_address or "—",
            "Permitted Use": self.permitted_use or "—",
            "Rent Commencement Date": self.rent_commencement_date or "—",
            "CAM / Tax / Insurance": self.cam_tax_insurance or "—",
            "Advanced Rental": self.advanced_rental or "—",
            "Lease Term": self.lease_term or "—",
            "Trade Name": self.trade_name or "—",
            "Approximate Size (SF)": self.approximate_size_sqft or "—",
            "Landlord Address": self.landlord_address or "—",
            "Tenant Address": self.tenant_address or "—",
            "Guarantor": self.guarantor or "—",
            "Execution Date": self.execution_date or "—",
            "Option Notice Period": self.option_notice_period or "—",
            "Option Rent": self.option_rent or "—",
            "Insurance Requirements": self.insurance_requirements or "—",
            "Assignment / Subletting": self.assignment_subletting or "—",
            "Default & Remedies": self.default_remedies or "—",
            "Parking": self.parking or "—",
            "Signage": self.signage or "—",
            "Broker": self.broker or "—",
        }
