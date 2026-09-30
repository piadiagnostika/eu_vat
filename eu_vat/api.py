import frappe
from eu_vat.utils.vat_validation import validate_eu_vat, EU_COUNTRIES, COUNTRY_NAME_TO_CODE
import requests

@frappe.whitelist()
def check_vies_vat(tax_id: str, customer_country: str = None):
    """
    Utility API callable from Desk client scripts or web forms.
    Returns: {
        "valid": bool,
        "is_eu": bool,
        "country_code": str,
        "vat_number": str,
        "country_mismatch": bool,
        "customer_country_code": str,
        "details": dict
    }
    """
    if not tax_id:
        return {"valid": False, "error": "No Tax ID provided"}

    clean_vat = tax_id.strip().upper().replace(".", "").replace(" ", "").replace("-", "")
    country_code = clean_vat[:2]
    if country_code == "GR":
        country_code = "EL"

    if country_code not in EU_COUNTRIES or len(clean_vat) < 5:
        return {
            "valid": False,
            "is_eu": False,
            "tax_id": clean_vat,
            "message": "Not an EU VAT formatted number (starts with domestic prefix or is national CIF/NIF)."
        }

    # Country mismatch check
    country_mismatch = False
    resolved_cust_code = None
    if customer_country:
        norm = str(customer_country).strip().upper()
        if len(norm) == 2:
            resolved_cust_code = "EL" if norm == "GR" else norm
        else:
            resolved_cust_code = COUNTRY_NAME_TO_CODE.get(norm)
        if resolved_cust_code and resolved_cust_code in EU_COUNTRIES:
            if resolved_cust_code != country_code:
                country_mismatch = True

    vat_number = clean_vat[2:]
    api_url = f"https://ec.europa.eu/taxation_customs/vies/rest-api/ms/{country_code}/vat/{vat_number}"

    try:
        res = requests.get(api_url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            is_valid = bool(data.get("isValid"))
            return {
                "valid": is_valid,
                "is_eu": True,
                "country_code": country_code,
                "vat_number": vat_number,
                "country_mismatch": country_mismatch,
                "customer_country_code": resolved_cust_code,
                "name": data.get("name") or "",
                "address": data.get("address") or "",
                "request_date": data.get("requestDate")
            }
        return {"valid": False, "is_eu": True, "error": f"VIES returned status {res.status_code}"}
    except Exception as e:
        return {"valid": False, "is_eu": True, "error": str(e)}

__all__ = ["validate_eu_vat", "check_vies_vat"]

