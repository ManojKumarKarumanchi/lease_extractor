"""Pydantic schemas for lease document extraction."""

from typing import List, Optional
from pydantic import BaseModel, Field

class PageOCR(BaseModel):
    """OCR results for a single page."""

    page_number: int
    text: str = Field(
        description="Full extracted text including handwritten, printed, tables"
    )
    tables: List[str] = Field(
        default_factory=list, description="Markdown tables found on this page"
    )
    handwritten_notes: List[str] = Field(
        default_factory=list, description="Handwritten text found"
    )
    signatures: List[str] = Field(
        default_factory=list, description="Signature descriptions"
    )
    confidence: float = Field(ge=0, le=1, description="OCR confidence sapp 0-1")

class LeaseKVPairs(BaseModel):
    """Structured lease summary matching the required output template."""

    # PARTIES & PREMISES
    address: Optional[str] = Field(None, description="Property address")
    unit: Optional[str] = Field(None, description="Unit designation")
    landlord: Optional[str] = Field(None, description="Landlord/Lessor name")
    tenant: Optional[str] = Field(None, description="Tenant/Lessee name")
    dba_name: Optional[str] = Field(None, description="DBA/Trading name")
    leased_area_sf: Optional[str] = Field(
        None, description="Leased area in square feet"
    )
    remeasurement_provision: Optional[str] = Field(
        None, description="Remeasurement provision"
    )
    security_deposit: Optional[str] = Field(None, description="Security deposit amount")
    guarantor: Optional[str] = Field(None, description="Guarantor name")

    # KEY DATES
    lease_term_months: Optional[str] = Field(None, description="Lease term in months")
    lease_term_notes: Optional[str] = Field(None, description="Notes on lease term")
    free_rent: Optional[str] = Field(None, description="Free rent period and amount")
    tenant_allowance: Optional[str] = Field(None, description="Tenant allowance amount")
    deadline_submit_plans: Optional[str] = Field(
        None, description="Deadline to submit plans"
    )
    deadline_apply_permits: Optional[str] = Field(
        None, description="Deadline to apply for permits"
    )
    tenant_possession_date: Optional[str] = Field(
        None, description="Tenant possession date"
    )
    possession_before_permits: Optional[str] = Field(
        None, description="Possession before permits Y/N"
    )
    landlord_delivery_date: Optional[str] = Field(
        None, description="Landlord delivery date"
    )
    rent_commencement_date: Optional[str] = Field(
        None, description="Rent commencement date"
    )

    # OPTIONS - Renewal
    renewal_number_of_options: Optional[str] = Field(
        None, description="Number of renewal options"
    )
    renewal_term_years: Optional[str] = Field(None, description="Renewal term in years")
    renewal_type: Optional[str] = Field(None, description="Renewal option type")
    renewal_earliest_notice: Optional[str] = Field(
        None, description="Earliest notice for renewal"
    )
    renewal_latest_notice: Optional[str] = Field(
        None, description="Latest notice for renewal"
    )
    renewal_tenant_initiates: Optional[str] = Field(
        None, description="Tenant initiates renewal Y/N"
    )
    renewal_notes: Optional[str] = Field(None, description="Renewal option notes")

    # OPTIONS - Early Termination
    early_termination_description: Optional[str] = Field(
        None, description="Early termination description"
    )
    early_termination_sales_kickout: Optional[str] = Field(
        None, description="Sales kickout clause"
    )
    early_termination_cotenancy: Optional[str] = Field(
        None, description="Co-tenancy clause"
    )

    # OPTIONS - Other
    contraction_option: Optional[str] = Field(
        None, description="Contraction option Y/N"
    )
    expansion_option: Optional[str] = Field(None, description="Expansion option Y/N")
    purchase_option: Optional[str] = Field(None, description="Purchase option Y/N")

    # SUBLEASE & ASSIGNMENT
    sublease_written_notice: Optional[str] = Field(
        None, description="Written notice required Y/N"
    )
    sublease_ll_consent_terms: Optional[str] = Field(
        None, description="Landlord consent terms"
    )
    sublease_rent_profits_pct: Optional[str] = Field(
        None, description="Landlord share of rent profits %"
    )
    sublease_third_party: Optional[str] = Field(
        None, description="Third party sublease Y/N"
    )
    sublease_affiliates: Optional[str] = Field(
        None, description="Affiliate sublease Y/N"
    )
    sublease_change_of_control: Optional[str] = Field(
        None, description="Change of control requirement Y/N"
    )
    sublease_recapture: Optional[str] = Field(
        None, description="Landlord recapture right Y/N"
    )
    sublease_processing_fee: Optional[str] = Field(None, description="Processing fee")
    sublease_other: Optional[str] = Field(None, description="Other sublease terms")
    sublease_notes: Optional[str] = Field(None, description="Sublease notes")

    # TENANT INSURANCE
    insurance_general_liability: Optional[str] = Field(
        None, description="General liability amount"
    )
    insurance_property: Optional[str] = Field(
        None, description="Property insurance requirements"
    )
    insurance_workers_comp: Optional[str] = Field(
        None, description="Workers compensation requirements"
    )
    insurance_auto: Optional[str] = Field(None, description="Auto insurance amount")
    insurance_business_interruption: Optional[str] = Field(
        None, description="Business interruption insurance"
    )
    insurance_employer_liability: Optional[str] = Field(
        None, description="Employer liability amount"
    )

    # SIGNAGE & USE
    signage_design_standards: Optional[str] = Field(
        None, description="Design standards attached Y/N"
    )
    signage_approval: Optional[str] = Field(
        None, description="Signage approval requirements"
    )
    signage_description: Optional[str] = Field(
        None, description="Signage description and types"
    )
    signage_removal_repair: Optional[str] = Field(
        None, description="Removal/repair/replacement terms"
    )
    permitted_use: Optional[str] = Field(
        None, description="Permitted use / exclusive use"
    )
    exclusive_use_radius: Optional[str] = Field(
        None, description="Radius restriction for exclusive use"
    )

    # RENT - Base
    rent_annual_amount: Optional[str] = Field(
        None, description="Annual base rent amount"
    )
    rent_monthly_amount: Optional[str] = Field(
        None, description="Monthly base rent amount"
    )
    rent_annual_psf: Optional[str] = Field(
        None, description="Annual rent per square foot"
    )

    # RENT - Percentage
    percentage_rent_details: Optional[str] = Field(
        None, description="Percentage rent details"
    )

    # RENT - Late Fee
    late_fee_calculation: Optional[str] = Field(
        None, description="Late fee calculation method"
    )
    late_fee_percentage: Optional[str] = Field(None, description="Late fee percentage")
    late_fee_grace_period: Optional[str] = Field(
        None, description="Grace period for late fees"
    )
    late_fee_notes: Optional[str] = Field(None, description="Late fee notes")

    # RENT - Holdover
    holdover_permitted: Optional[str] = Field(
        None, description="Holdover permitted Y/N"
    )
    holdover_fee: Optional[str] = Field(None, description="Holdover fee")
    holdover_damages: Optional[str] = Field(None, description="Holdover damages")

    # CAM
    cam_pro_rata_share: Optional[str] = Field(None, description="CAM pro rata share %")
    cam_cap: Optional[str] = Field(None, description="CAM cap")
    cam_cap_type: Optional[str] = Field(None, description="CAM cap type")
    cam_expense_stop: Optional[str] = Field(None, description="CAM expense stop")
    cam_denominator: Optional[str] = Field(None, description="Denominator definition")
    cam_base_year: Optional[str] = Field(None, description="CAM base year Y/N")
    cam_admin_fee: Optional[str] = Field(None, description="CAM admin fee")
    cam_admin_exclusions: Optional[str] = Field(
        None, description="CAM admin exclusions"
    )
    cam_grossup_provision: Optional[str] = Field(
        None, description="CAM gross-up provision"
    )
    cam_reconciliation: Optional[str] = Field(
        None, description="CAM reconciliation terms"
    )
    cam_payment_frequency: Optional[str] = Field(
        None, description="CAM payment frequency"
    )
    cam_audit_rights: Optional[str] = Field(None, description="CAM audit rights")
    cam_inclusions: Optional[str] = Field(None, description="CAM inclusions")
    cam_exclusions: Optional[str] = Field(None, description="CAM exclusions")
    cam_notes: Optional[str] = Field(None, description="CAM notes")

    # TAXES
    taxes_incl_operating: Optional[str] = Field(
        None, description="Taxes included in operating Y/N"
    )
    taxes_pro_rata_share: Optional[str] = Field(
        None, description="Tax pro rata share %"
    )
    taxes_payment_frequency: Optional[str] = Field(
        None, description="Tax payment frequency"
    )
    taxes_audit_rights: Optional[str] = Field(None, description="Tax audit rights")
    taxes_denominator: Optional[str] = Field(
        None, description="Denominator definition Y/N"
    )
    taxes_right_to_contest: Optional[str] = Field(
        None, description="Right to contest taxes"
    )
    taxes_base_year: Optional[str] = Field(None, description="Tax base year Y/N")
    taxes_paid_to_authority: Optional[str] = Field(
        None, description="Paid to tax authority Y/N"
    )
    taxes_first_year_estimate: Optional[str] = Field(
        None, description="First year tax estimate"
    )

    # DEFAULT
    default_monetary_notice: Optional[str] = Field(
        None, description="Monetary notice and cure period"
    )
    default_non_monetary_notice: Optional[str] = Field(
        None, description="Non-monetary notice and cure period"
    )
    default_notes: Optional[str] = Field(None, description="Default notes")

    # SPECIAL COMPLIANCE
    special_compliance: Optional[str] = Field(
        None, description="Special compliance provisions"
    )


class QAResponse(BaseModel):
    """Response schema for Q&A about the lease document."""

    answer: str = Field(description="Answer to the question")
    reference_pages: List[int] = Field(
        description="Page numbers where answer was found"
    )
    section_reference: Optional[str] = Field(
        None, description="Section or clause reference if available"
    )
    confidence_sapp: float = Field(
        ge=0, le=1, description="Confidence in the answer 0-1"
    )
    relevant_excerpt: str = Field(
        description="Exact text excerpt supporting the answer"
    )

# Field categories for displaying KV pairs
KV_FIELD_CATEGORIES = {
    "PARTIES & PREMISES": [
        "address",
        "unit",
        "landlord",
        "tenant",
        "dba_name",
        "leased_area_sf",
        "remeasurement_provision",
        "security_deposit",
        "guarantor",
    ],
    "KEY DATES": [
        "lease_term_months",
        "lease_term_notes",
        "free_rent",
        "tenant_allowance",
        "deadline_submit_plans",
        "deadline_apply_permits",
        "tenant_possession_date",
        "possession_before_permits",
        "landlord_delivery_date",
        "rent_commencement_date",
    ],
    "OPTIONS": [
        "renewal_number_of_options",
        "renewal_term_years",
        "renewal_type",
        "renewal_earliest_notice",
        "renewal_latest_notice",
        "renewal_tenant_initiates",
        "renewal_notes",
        "early_termination_description",
        "early_termination_sales_kickout",
        "early_termination_cotenancy",
        "contraction_option",
        "expansion_option",
        "purchase_option",
    ],
    "SUBLEASE & ASSIGNMENT": [
        "sublease_written_notice",
        "sublease_ll_consent_terms",
        "sublease_rent_profits_pct",
        "sublease_third_party",
        "sublease_affiliates",
        "sublease_change_of_control",
        "sublease_recapture",
        "sublease_processing_fee",
        "sublease_other",
        "sublease_notes",
    ],
    "TENANT INSURANCE": [
        "insurance_general_liability",
        "insurance_property",
        "insurance_workers_comp",
        "insurance_auto",
        "insurance_business_interruption",
        "insurance_employer_liability",
    ],
    "SIGNAGE & USE": [
        "signage_design_standards",
        "signage_approval",
        "signage_description",
        "signage_removal_repair",
        "permitted_use",
        "exclusive_use_radius",
    ],
    "RENT": [
        "rent_annual_amount",
        "rent_monthly_amount",
        "rent_annual_psf",
        "percentage_rent_details",
        "late_fee_calculation",
        "late_fee_percentage",
        "late_fee_grace_period",
        "late_fee_notes",
        "holdover_permitted",
        "holdover_fee",
        "holdover_damages",
    ],
    "CAM": [
        "cam_pro_rata_share",
        "cam_cap",
        "cam_cap_type",
        "cam_expense_stop",
        "cam_denominator",
        "cam_base_year",
        "cam_admin_fee",
        "cam_admin_exclusions",
        "cam_grossup_provision",
        "cam_reconciliation",
        "cam_payment_frequency",
        "cam_audit_rights",
        "cam_inclusions",
        "cam_exclusions",
        "cam_notes",
    ],
    "TAXES": [
        "taxes_incl_operating",
        "taxes_pro_rata_share",
        "taxes_payment_frequency",
        "taxes_audit_rights",
        "taxes_denominator",
        "taxes_right_to_contest",
        "taxes_base_year",
        "taxes_paid_to_authority",
        "taxes_first_year_estimate",
    ],
    "DEFAULT": [
        "default_monetary_notice",
        "default_non_monetary_notice",
        "default_notes",
    ],
    "SPECIAL COMPLIANCE": ["special_compliance"],
}
