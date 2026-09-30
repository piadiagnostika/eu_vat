import requests
import re
import frappe
from frappe import _

# =====================================================================
# CONFIGURABLE TAX CATEGORIES
# Modify these 3 constants to match your ERPNext tax category names.
# The entire codebase references these constants:
# =====================================================================
TAX_CATEGORY_DOMESTIC = "Domestic"  # Domestic transactions (e.g. Austria) or EU entities without valid VIES (20% VAT)
TAX_CATEGORY_EU_B2B = "EU B2B"      # Intra-community EU B2B with verified VIES VAT (0% Reverse Charge)
TAX_CATEGORY_NON_EU = "Import"      # Non-EU / Third country transactions (e.g. "Import" or "Non-EU")


# Standard 2-letter ISO / VIES country codes for European Union member states
EU_COUNTRY_CODES = {
    "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "ES", "FI", "FR",
    "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO",
    "SE", "SI", "SK", "XI"
}
EU_COUNTRIES = EU_COUNTRY_CODES


# Standard EU member state names (matching official ERPNext Country records) mapped to VIES 2-letter codes
COUNTRY_NAME_TO_CODE = {
    "AUSTRIA": "AT",
    "BELGIUM": "BE",
    "BULGARIA": "BG",
    "CROATIA": "HR",
    "CYPRUS": "CY",
    "CZECH REPUBLIC": "CZ",
    "CZECHIA": "CZ",
    "DENMARK": "DK",
    "ESTONIA": "EE",
    "FINLAND": "FI",
    "FRANCE": "FR",
    "GERMANY": "DE",
    "GREECE": "EL",
    "HUNGARY": "HU",
    "IRELAND": "IE",
    "ITALY": "IT",
    "LATVIA": "LV",
    "LITHUANIA": "LT",
    "LUXEMBOURG": "LU",
    "MALTA": "MT",
    "NETHERLANDS": "NL",
    "POLAND": "PL",
    "PORTUGAL": "PT",
    "ROMANIA": "RO",
    "SLOVAKIA": "SK",
    "SLOVENIA": "SI",
    "SPAIN": "ES",
    "SWEDEN": "SE",
    "NORTHERN IRELAND": "XI"
}


def resolve_country_code(raw_country):
    """
    Resolves a raw country input (name, code, territory) into an official EU VIES 2-letter code.
    Returns: (country_code, raw_country_string)
    """
    if not raw_country:
        return None, ""

    normalized = str(raw_country).strip().upper()

    code = None
    if len(normalized) == 2:
        code = "EL" if normalized == "GR" else normalized
    elif normalized in COUNTRY_NAME_TO_CODE:
        code = COUNTRY_NAME_TO_CODE[normalized]
    elif hasattr(frappe, "db"):
        try:
            db_code = frappe.db.get_value("Country", {"country_name": raw_country}, "code")
            if db_code:
                code = db_code.strip().upper()
                if code == "GR":
                    code = "EL"
        except Exception:
            pass

    return code, raw_country


def get_home_country_code(doc=None):
    """
    Determines the domestic country code of the ERPNext instance or company.
    First checks doc.company, then Global Defaults, and falls back to 'AT'.
    """
    home_country_raw = None
    if doc and getattr(doc, "company", None) and hasattr(frappe, "db"):
        try:
            home_country_raw = frappe.db.get_value("Company", doc.company, "country")
        except Exception:
            pass

    if not home_country_raw and hasattr(frappe, "db"):
        try:
            home_country_raw = (
                frappe.db.get_single_value("Global Defaults", "country")
                or frappe.defaults.get_global_default("country")
            )
        except Exception:
            pass

    if home_country_raw:
        code, _ = resolve_country_code(home_country_raw)
        if code:
            return code

    return "AT"


def validate_eu_vat(doc, method=None):
    """
    Validates EU VAT numbers via the European Commission VIES REST API.

    Rules:
    1. Non-EU / Import category: Skips European VIES checks.
    2. Empty Tax ID: resets intra_community_valid to 0. Throws error only if EU B2B is selected.
    3. National/Non-EU Tax ID: resets intra_community_valid to 0, shows a non-blocking notice,
       and allows saving (unless EU B2B is explicitly selected).
    4. Country Mismatch: If Customer is from Country A but enters VAT for Country B,
       prevents unauthorized intra-community tax exemption.
    5. Valid EU VAT in VIES: sets intra_community_valid to 1 and auto-assigns TAX_CATEGORY_EU_B2B
       (except for Austrian domestic accounts, which receive TAX_CATEGORY_DOMESTIC).
       During batch import, SUCCESS messages are silenced while ERRORS and WARNINGS remain active.
    6. Invalid in VIES: resets intra_community_valid to 0. Throws an error only if EU B2B is selected,
       otherwise permits saving as a standard customer with a non-blocking warning.
    """
    current_category = getattr(doc, "tax_category", None)
    is_eu_b2b_selected = (current_category == TAX_CATEGORY_EU_B2B)
    is_in_import = bool(getattr(frappe.flags, "in_import", False) or getattr(frappe.flags, "in_migrate", False))

    # Identify the party name (Supplier Name / Customer Name / Doc Name)
    party_name = (
        getattr(doc, "supplier_name", None)
        or getattr(doc, "customer_name", None)
        or getattr(doc, "name", None)
        or getattr(doc, "company_name", None)
        or _("Unknown Entity")
    )
    raw_vat = str(getattr(doc, "tax_id", None) or "").strip()

    # 0. Skip validation if the category is configured as Non-EU / Import
    if current_category == TAX_CATEGORY_NON_EU:
        doc.pia_intra_community_valid = 0
        return

    # Check partner's country
    customer_country_raw = getattr(doc, "country", None) or getattr(doc, "territory", None)
    customer_country_code, display_name = resolve_country_code(customer_country_raw)

    # If the partner is definitively from outside the EU, skip EU VAT checks
    if customer_country_code and customer_country_code not in EU_COUNTRY_CODES:
        doc.pia_intra_community_valid = 0
        if is_eu_b2b_selected:
            frappe.throw(
                msg=_("Non-EU Country Mismatch for '{0}' (VAT: '{1}'): Country '{2}' is outside the European Union. '{3}' tax category cannot be applied.").format(
                    party_name, raw_vat, display_name or customer_country_code, TAX_CATEGORY_EU_B2B
                ),
                title=_("Non-EU Country Mismatch: {0}").format(party_name)
            )
        return

    # 1. Check for empty Tax ID
    if not doc.tax_id:
        doc.pia_intra_community_valid = 0
        if is_eu_b2b_selected:
            frappe.throw(
                msg=_("Missing VAT Number for '{0}': A valid EU VAT number is mandatory when Tax Category is set to '{1}'.").format(
                    party_name, TAX_CATEGORY_EU_B2B
                ),
                title=_("Missing VAT Number: {0}").format(party_name)
            )
        return

    # Clean the Tax ID (remove spaces, dots, hyphens, and convert to uppercase)
    clean_tax_id = re.sub(r'[^A-Za-z0-9]', '', str(doc.tax_id).strip().upper())
    raw_vat = clean_tax_id

    # Greece uses 'EL' for VAT in VIES, even if ISO is 'GR'
    if clean_tax_id.startswith("GR"):
        clean_tax_id = "EL" + clean_tax_id[2:]

    # 2. Check for EU VAT format (2-letter country prefix in EU + identifier)
    prefix_is_alpha = len(clean_tax_id) >= 2 and clean_tax_id[:2].isalpha()
    prefix_code = clean_tax_id[:2] if prefix_is_alpha else ""

    # Smart auto-prefix: If the partner's country is known and in the EU (e.g. Ireland / IE),
    # but the Tax ID omitted the 2-letter country prefix (e.g. '4749148U' instead of 'IE4749148U'),
    # automatically prepend the country prefix and update doc.tax_id.
    if (not prefix_is_alpha or prefix_code not in EU_COUNTRY_CODES) and customer_country_code in EU_COUNTRY_CODES:
        if customer_country_code == "AT" and not clean_tax_id.startswith("U"):
            # Domestic Austrian Steuernummer (e.g. 12 345/6789), not a UID
            pass
        else:
            clean_tax_id = customer_country_code + clean_tax_id
            prefix_is_alpha = True
            prefix_code = customer_country_code
            doc.tax_id = clean_tax_id
            raw_vat = clean_tax_id

    if not prefix_is_alpha or prefix_code not in EU_COUNTRY_CODES:
        doc.pia_intra_community_valid = 0
        if is_eu_b2b_selected:
            frappe.throw(
                msg=_("Invalid EU VAT Format for '{0}' (Tax ID: '{1}'): Does not have a valid 2-letter EU country prefix. '{2}' requires an intra-community VAT (e.g. ES{1} for Spain).").format(
                    party_name, clean_tax_id, TAX_CATEGORY_EU_B2B
                ),
                title=_("Invalid EU VAT Format: {0}").format(party_name)
            )
        else:
            # Notice is shown (even in import) so the user is informed
            frappe.msgprint(
                msg=_("Notice for '{0}': Tax ID '{1}' does not have an EU VAT prefix. Saved as domestic/standard tax ID.").format(
                    party_name, clean_tax_id
                ),
                title=_("Domestic/Standard Tax ID: {0}").format(party_name),
                indicator="blue"
            )
            return

    country_code = prefix_code
    vat_number = clean_tax_id[2:]

    # 3. Country Matching Validation
    if customer_country_code and customer_country_code in EU_COUNTRY_CODES:
        if customer_country_code != country_code:
            doc.pia_intra_community_valid = 0
            mismatch_err = _(
                "Country Mismatch for '{0}' (VAT: '{1}'): The VAT prefix '{2}' does not match the country '{3}' ({4}). "
                "You cannot assign a VAT number from a different member state to this customer/supplier."
            ).format(party_name, raw_vat, country_code, display_name, customer_country_code)

            if is_eu_b2b_selected:
                # If the VAT is Austrian (AT), it is domestic, not EU B2B
                if country_code == "AT":
                    doc.tax_category = TAX_CATEGORY_DOMESTIC
                    frappe.msgprint(
                        msg=_("Note for '{0}' (VAT: '{1}'): Has an Austrian VAT prefix ('AT'). Reset Tax Category from '{2}' to '{3}'.").format(
                            party_name, raw_vat, TAX_CATEGORY_EU_B2B, TAX_CATEGORY_DOMESTIC
                        ),
                        title=_("Domestic VAT: {0}").format(party_name),
                        indicator="orange"
                    )
                    return
                # In import, show warning rather than crash if multinational, else throw
                if not is_in_import:
                    frappe.throw(
                        msg=mismatch_err,
                        title=_("Country Mismatch: {0}").format(party_name)
                    )
                else:
                    frappe.msgprint(
                        msg=mismatch_err,
                        title=_("Country Mismatch: {0}").format(party_name),
                        indicator="orange"
                    )
                    return
            else:
                frappe.msgprint(
                    msg=mismatch_err,
                    title=_("Country Mismatch: {0}").format(party_name),
                    indicator="orange"
                )
                return

    # 4. Check against official EU VIES REST API
    url = f"https://ec.europa.eu/taxation_customs/vies/rest-api/ms/{country_code}/vat/{vat_number}"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            is_valid = bool(data.get("isValid"))

            if not is_valid:
                doc.pia_intra_community_valid = 0

                # If the user selected EU B2B tax category, throw an error to prevent illegal tax exemption
                if is_eu_b2b_selected:
                    frappe.throw(
                        msg=_("VIES Verification Failed for '{0}' (VAT: '{1}'): The EU VAT number is NOT valid in the official VIES system. It cannot be used with '{2}'.").format(
                            party_name, raw_vat, TAX_CATEGORY_EU_B2B
                        ),
                        title=_("VIES Verification Failed: {0}").format(party_name)
                    )
                else:
                    # Non-blocking warning is shown in both manual and import mode
                    frappe.msgprint(
                        msg=_("Notice for '{0}' (VAT: '{1}'): Not registered in the European VIES system. Saved without intra-community tax exemption.").format(
                            party_name, raw_vat
                        ),
                        title=_("VIES Verification: {0}").format(party_name),
                        indicator="orange"
                    )
            else:
                # SUCCESS: Mark the intra-community VAT checkbox
                doc.pia_intra_community_valid = 1

                # Auto-assign tax category
                home_country_code = get_home_country_code(doc)
                if country_code != home_country_code:
                    if doc.doctype in ["Customer", "Supplier", "Sales Invoice"]:
                        doc.tax_category = TAX_CATEGORY_EU_B2B
                else:
                    if doc.doctype in ["Customer", "Supplier", "Sales Invoice"]:
                        doc.tax_category = TAX_CATEGORY_DOMESTIC

                # Store VIES registered company name and address if fields are present
                company_name = data.get("name") or ""
                company_address = data.get("address") or ""
                if hasattr(doc, "pia_vies_company_name"):
                    doc.pia_vies_company_name = company_name
                if hasattr(doc, "pia_vies_address"):
                    doc.pia_vies_address = company_address

                # SILENCE ONLY SUCCESS ON MASS IMPORT:
                # Success popups appear during UI manual saves, but are silenced during batch imports
                if not is_in_import:
                    success_msg = _("EU VAT number '{0}' successfully verified in VIES (Intra-community valid).").format(doc.tax_id)
                    if company_name:
                        success_msg += f"<br><b>{_('Registered Name')}:</b> {company_name}"
                    if company_address:
                        formatted_address = company_address.replace("\n", ", ")
                        success_msg += f"<br><b>{_('Registered Address')}:</b> {formatted_address}"
                    frappe.msgprint(
                        msg=success_msg,
                        title=_("VIES Validated"),
                        indicator="green"
                    )
        else:
            # If the EU VIES server returns an error (e.g. 500, 503 service unavailable)
            doc.pia_intra_community_valid = 0
            frappe.msgprint(
                msg=_("Warning for '{0}' (VAT: '{1}'): Could not verify in VIES (European service temporarily unavailable).").format(
                    party_name, raw_vat
                ),
                title=_("VIES Service Unavailable: {0}").format(party_name),
                indicator="orange"
            )

    except requests.exceptions.RequestException:
        # Handle connection timeouts and network outages gracefully
        doc.pia_intra_community_valid = 0
        frappe.log_error(message=frappe.get_traceback(), title="VIES Connection Timeout")
        frappe.msgprint(
            msg=_("Warning for '{0}' (VAT: '{1}'): No connection to VIES. Intra-community VAT could not be verified automatically. Please check Tax Category manually.").format(
                party_name, raw_vat
            ),
            title=_("VIES Connection Failed: {0}").format(party_name),
            indicator="orange"
        )
