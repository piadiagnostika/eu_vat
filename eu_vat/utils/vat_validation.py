import requests
import re
import frappe
from frappe import _

# Standard 2-letter ISO / VIES country codes for European Union member states
EU_COUNTRY_CODES = {
    "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "ES", "FI", "FR",
    "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO",
    "SE", "SI", "SK", "XI"
}

# Alias for compatibility with api.py
EU_COUNTRIES = EU_COUNTRY_CODES

# Country name mapping for multi-lingual input resolution
COUNTRY_NAME_TO_CODE = {
    # Spanish
    "ALEMANIA": "DE", "AUSTRIA": "AT", "BELGICA": "BE", "BÉLGICA": "BE",
    "BULGARIA": "BG", "CHIPRE": "CY", "CROACIA": "HR", "DINAMARCA": "DK",
    "ESLOVAQUIA": "SK", "ESLOVENIA": "SI", "ESPAÑA": "ES", "ESPANA": "ES",
    "ESTONIA": "EE", "FINLANDIA": "FI", "FRANCIA": "FR", "GRECIA": "EL",
    "HUNGRIA": "HU", "HUNGRÍA": "HU", "IRLANDA": "IE", "ITALIA": "IT",
    "LETONIA": "LV", "LITUANIA": "LT", "LUXEMBURGO": "LU", "MALTA": "MT",
    "PAISES BAJOS": "NL", "PAÍSES BAJOS": "NL", "HOLANDA": "NL", "POLONIA": "PL",
    "PORTUGAL": "PT", "REPUBLICA CHECA": "CZ", "REPÚBLICA CHECA": "CZ",
    "RUMANIA": "RO", "RUMANÍA": "RO", "SUECIA": "SE", "IRLANDA DEL NORTE": "XI",

    # English
    "GERMANY": "DE", "AUSTRIA": "AT", "BELGIUM": "BE", "BULGARIA": "BG",
    "CYPRUS": "CY", "CROATIA": "HR", "DENMARK": "DK", "SLOVAKIA": "SK",
    "SLOVENIA": "SI", "SPAIN": "ES", "ESTONIA": "EE", "FINLAND": "FI",
    "FRANCE": "FR", "GREECE": "EL", "HUNGARY": "HU", "IRELAND": "IE",
    "ITALY": "IT", "LATVIA": "LV", "LITHUANIA": "LT", "LUXEMBOURG": "LU",
    "MALTA": "MT", "NETHERLANDS": "NL", "HOLLAND": "NL", "POLAND": "PL",
    "PORTUGAL": "PT", "CZECH REPUBLIC": "CZ", "CZECHIA": "CZ", "ROMANIA": "RO",
    "SWEDEN": "SE", "NORTHERN IRELAND": "XI",

    # German
    "DEUTSCHLAND": "DE", "ÖSTERREICH": "AT", "OESTERREICH": "AT", "BELGIEN": "BE",
    "BULGARIEN": "BG", "ZYPERN": "CY", "KROATIEN": "HR", "DÄNEMARK": "DK",
    "DAENEMARK": "DK", "SLOWAKEI": "SK", "SLOWENIEN": "SI", "SPANIEN": "ES",
    "ESTLAND": "EE", "FINNLAND": "FI", "FRANKREICH": "FR", "GRIECHENLAND": "EL",
    "UNGARN": "HU", "IRLAND": "IE", "ITALIEN": "IT", "LETTLAND": "LV",
    "LITAUEN": "LT", "LUXEMBURG": "LU", "NIEDERLANDE": "NL", "POLEN": "PL",
    "TSCHECHIEN": "CZ", "TSCHECHISCHE REPUBLIK": "CZ", "RUMÄNIEN": "RO",
    "RUMAENIEN": "RO", "SCHWEDEN": "SE", "NORDIRLAND": "XI"
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

def validate_eu_vat(doc, method=None):
    """
    Validates EU VAT numbers via the European Commission VIES REST API.

    Rules:
    1. Empty Tax ID: resets intra_community_valid to 0. Throws error only if EU B2B is selected.
    2. National/Non-EU Tax ID: resets intra_community_valid to 0, shows a non-blocking notice,
       and allows saving (unless EU B2B is explicitly selected).
    3. Country Mismatch: If Customer is from Country A (e.g. Spain / ES) but enters a VAT for
       Country B (e.g. Germany / DE), the system flags the country mismatch and prevents illegal
       intra-community exemption.
    4. Valid EU VAT in VIES: sets intra_community_valid to 1 and auto-assigns tax category 'EU B2B'
       (except for Austrian domestic accounts).
    5. Invalid in VIES: resets intra_community_valid to 0. Throws an error only if EU B2B is selected,
       otherwise permits saving as a standard customer with a non-blocking warning.
    """
    is_eu_b2b_selected = getattr(doc, "tax_category", None) == "EU B2B"

    # 1. Check for empty Tax ID
    if not doc.tax_id:
        doc.pia_intra_community_valid = 0
        if is_eu_b2b_selected:
            frappe.throw(
                msg=_("A valid EU VAT number is mandatory when Tax Category is set to 'EU B2B'."),
                title=_("Missing VAT Number")
            )
        return

    # Clean the Tax ID (remove spaces, dots, hyphens, and convert to uppercase)
    clean_tax_id = re.sub(r'[^A-Za-z0-9]', '', str(doc.tax_id).strip().upper())

    # Greece uses 'EL' for VAT in VIES, even if ISO is 'GR'
    if clean_tax_id.startswith("GR"):
        clean_tax_id = "EL" + clean_tax_id[2:]

    # 2. Check for EU VAT format (2-letter country prefix + identifier)
    if len(clean_tax_id) < 3 or not clean_tax_id[:2].isalpha():
        doc.pia_intra_community_valid = 0
        if is_eu_b2b_selected:
            frappe.throw(
                msg=_("The Tax ID '{0}' does not have a valid EU country prefix. EU B2B tax category requires an intra-community VAT (e.g. ES{0} for Spain).").format(clean_tax_id),
                title=_("Invalid EU VAT Format")
            )
        else:
            frappe.msgprint(
                msg=_("Notice: Tax ID '{0}' does not have an EU VAT prefix. Saved as domestic/standard tax ID.").format(clean_tax_id),
                title=_("Domestic Tax ID"),
                indicator="blue"
            )
            return

    country_code = clean_tax_id[:2]
    vat_number = clean_tax_id[2:]

    # 3. Country Matching Validation
    customer_country_raw = getattr(doc, "country", None) or getattr(doc, "territory", None)
    customer_country_code, display_name = resolve_country_code(customer_country_raw)

    if customer_country_code and customer_country_code in EU_COUNTRY_CODES:
        if customer_country_code != country_code:
            doc.pia_intra_community_valid = 0
            mismatch_err = _(
                "Country Mismatch: The VAT prefix '{0}' does not match the customer's country '{1}' ({2}). "
                "You cannot assign a VAT number from a different member state to this customer."
            ).format(country_code, display_name, customer_country_code)

            if is_eu_b2b_selected:
                frappe.throw(
                    msg=mismatch_err,
                    title=_("Country Mismatch Error")
                )
            else:
                frappe.msgprint(
                    msg=mismatch_err,
                    title=_("Country Mismatch Warning"),
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
                        msg=_("The EU VAT number '{0}' is NOT valid in the official VIES system. It cannot be used with the 'EU B2B' tax category.").format(doc.tax_id),
                        title=_("VIES Verification Failed")
                    )
                else:
                    frappe.msgprint(
                        msg=_("Notice: The VAT number '{0}' is not registered in the European VIES system. Saved without intra-community tax exemption.").format(doc.tax_id),
                        title=_("VIES Verification"),
                        indicator="orange"
                    )
            else:
                # SUCCESS: Mark the intra-community VAT checkbox
                doc.pia_intra_community_valid = 1

                # Auto-assign 'EU B2B' tax category (except for domestic Austrian entities)
                if country_code != "AT":
                    if doc.doctype in ["Customer", "Supplier", "Sales Invoice"]:
                        doc.tax_category = "EU B2B"

                # Store VIES registered company name and address if fields are present
                company_name = data.get("name") or ""
                company_address = data.get("address") or ""
                if hasattr(doc, "pia_vies_company_name"):
                    doc.pia_vies_company_name = company_name
                if hasattr(doc, "pia_vies_address"):
                    doc.pia_vies_address = company_address

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
                msg=_("Warning: Could not verify VAT in VIES (European service temporarily unavailable)."),
                title=_("VIES Service Unavailable"),
                indicator="orange"
            )

    except requests.exceptions.RequestException:
        # Handle connection timeouts and network outages gracefully
        doc.pia_intra_community_valid = 0
        frappe.log_error(message=frappe.get_traceback(), title="VIES Connection Timeout")
        frappe.msgprint(
            msg=_("Warning: No connection to VIES. Intra-community VAT could not be verified automatically. Please check Tax Category manually."),
            title=_("VIES Connection Failed"),
            indicator="orange"
        )
