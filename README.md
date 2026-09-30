# EU VAT & VIES Validation for ERPNext

[![ERPNext Version](https://img.shields.io/badge/ERPNext-v16%20(tested)-blue.svg)](https://erpnext.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![API: European Commission VIES](https://img.shields.io/badge/API-EU%20VIES%20REST-green.svg)](https://ec.europa.eu/taxation_customs/vies/)
[![Translations](https://img.shields.io/badge/Translations-EN%20%7C%20ES%20%7C%20DE%20%7C%20FR%20%7C%20IT-purple.svg)](https://www.gnu.org/software/gettext/)

Official EU VAT validation, VIES real-time registry verification, and automatic intra-community tax rules for **ERPNext v16**.

---

## ✨ Features

- **⚡ Real-time EU VIES Validation**: Queries the European Commission's official VIES REST API instantly without requiring API keys or subscriptions.
- **🌍 Universal European Support**: Dynamically detects the home country of your ERPNext Company (or Global Defaults). Works out-of-the-box for companies based in **any EU member state** (Spain, Germany, France, Italy, Austria, Netherlands, etc.).
- **🛡️ Country Mismatch Prevention**: Checks that the VAT prefix matches the customer/supplier country (e.g. alerts if an `ES` VAT is entered for a German customer), preventing fraudulent or erroneous intra-community tax exemptions.
- **🏷️ Automated Tax Category Routing**:
  - Automatically assigns the **`EU B2B`** tax category when a valid cross-border EU VAT number is confirmed.
  - Leaves domestic transactions subject to standard national VAT.
  - Strict compliance: Blocks saving with `EU B2B` if the VAT number is invalid, empty, or mismatched.
- **🏢 Registered Company Name & Address Auto-Capture**: Automatically retrieves the official business name and registered fiscal address returned by VIES.
- **🎨 Interactive UI Card in Desk**: Displays a sleek status card in the Tax section of Customer and Supplier forms with an instant **"⚡ Verify VIES"** button and visual indicators.
- **🌐 Full GNU Gettext Localization (ERPNext 16 Compliant)**:
  - English (`en`)
  - Spanish (`es`)
  - German (`de`)
  - French (`fr`)
  - Italian (`it`)

---

## 📋 Requirements

- **Frappe Framework**: v16 (actively tested & supported)
- **ERPNext**: v16 (actively tested & supported)
- Python packages: `requests` (included with Frappe)

---

## 🚀 Installation

From your bench directory:

```bash
# 1. Fetch the application repository
bench get-app https://github.com/piadiagnostika/eu_vat.git

# 2. Install the app onto your target site
bench --site <your-site-name> install-app eu_vat

# 3. Run database migrations to load custom fields & fixtures
bench --site <your-site-name> migrate

# 4. (Optional) Rebuild client assets
bench build
```

---

## 🏷️ Tax Category Automation & Enforcement Rules

The application directly manages the **Tax Category** on `Customer`, `Supplier`, and `Sales Invoice` according to European tax regulations (Directive 2006/112/EC):

### 1. Automatic Assignment to `EU B2B` (Cross-Border Exemption)
- When an EU VAT number is validated in VIES and the customer's country differs from your company's home member state, the system automatically sets:
  - `tax_category = "EU B2B"`
  - `pia_intra_community_valid = 1`
- This triggers your zero-rated intra-community sales tax template (reverse charge / Art. 138).

### 2. Domestic Safeguard (No Exemption for Home Country)
- If the customer belongs to your own home member state (e.g. both company and client are in Spain `ES`, or Germany `DE`):
  - The app **does NOT** assign `EU B2B`.
  - Domestic transactions remain subject to standard local VAT, avoiding accidental tax exemptions for local clients.

### 3. Strict Enforcement for `EU B2B`
If a user manually selects or leaves the Tax Category as **`EU B2B`**, validation becomes **mandatory and blocking**:
- **Empty Tax ID:** Throws an error preventing save (`Missing VAT Number`).
- **Invalid VIES Status:** Throws an error preventing save (`VIES Verification Failed`).
- **Country Mismatch:** Throws an error preventing save (`Country Mismatch Error`).
- *Benefit:* Ensures your organization never legally compromises itself by issuing tax-exempt intra-community invoices without verified VIES registration.

### 4. Non-EU & Standard Domestic Workflow
- If `EU B2B` is **not** selected and a local tax ID (without EU prefix) or an unverified VAT is entered, ERPNext permits normal saving with an informative, non-blocking notification.

---

## ⚙️ How It Works

### Validation Flow on Save (`Customer`, `Supplier`, `Sales Invoice`)

```
   Tax ID Entered?
         │
    ┌────┴────┐
    ▼         ▼
  [NO]      [YES]
    │         │
    │         ▼
    │    Is EU Format? (e.g. DE123456789)
    │         │
    │    ┌────┴────┐
    │    ▼         ▼
    │  [NO]      [YES]
    │    │         │
    │    │         ▼
    │    │   Country Matches Customer Country?
    │    │         │
    │    │    ┌────┴────┐
    │    │    ▼         ▼
    │    │  [NO]      [YES]
    │    │    │         │
    │    │    │         ▼
    │    │    │   Query EU VIES REST API
    │    │    │         │
    │    │    │    ┌────┴────┐
    │    │    │    ▼         ▼
    │    │    │ [Invalid]  [Valid]
    ▼    ▼    ▼    │         │
 ┌─────────────────┴─┐       ▼
 │ No Tax Exemption  │   ┌───────────────────────────────┐
 │ (Standard VAT)    │   │ • Mark Intra-Community Valid  │
 └───────────────────┘   │ • Auto-assign 'EU B2B' (if    │
                         │   cross-border transaction)   │
                         │ • Store VIES Name & Address   │
                         └───────────────────────────────┘
```

---

## 🧩 Custom Fields Included

The app provisions the following standard custom fields via fixtures:

| DocType | Fieldname | Fieldtype | Description |
| :--- | :--- | :--- | :--- |
| `Customer` | `pia_intra_community_valid` | Check | Set to 1 when verified via VIES |
| `Customer` | `pia_vies_company_name` | Data | Registered company name from VIES |
| `Customer` | `pia_vies_address` | Small Text | Registered fiscal address from VIES |
| `Supplier` | `pia_intra_community_valid` | Check | Set to 1 when verified via VIES |
| `Supplier` | `pia_vies_company_name` | Data | Registered company name from VIES |
| `Supplier` | `pia_vies_address` | Small Text | Registered fiscal address from VIES |
| `Tax Category` | `pia_legal_note` | Text | Legal intra-community invoice note |

---

## 🌐 Translations

Translations use standard GNU gettext `.po` catalogs located in `eu_vat/locale/`:

```text
eu_vat/eu_vat/locale/
├── main.pot      # Master gettext translation template
├── de.po         # German (Deutsch)
├── es.po         # Spanish (Español)
├── fr.po         # French (Français)
└── it.po         # Italian (Italiano)
```

To update or recompile translations manually:
```bash
cd eu_vat/eu_vat/locale
msgfmt es.po -o es.mo
msgfmt de.po -o de.mo
msgfmt fr.po -o fr.mo
msgfmt it.po -o it.mo
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [license.txt](license.txt) file for details.

Developed with ❤️ for the Frappe & ERPNext European Community.
