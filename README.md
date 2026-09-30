# EU VAT & VIES Validation for ERPNext

[![ERPNext Version](https://img.shields.io/badge/ERPNext-v14%20%7C%20v15%20%7C%20v16-blue.svg)](https://erpnext.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![API: European Commission VIES](https://img.shields.io/badge/API-EU%20VIES%20REST-green.svg)](https://ec.europa.eu/taxation_customs/vies/)
[![Translations](https://img.shields.io/badge/Translations-EN%20%7C%20ES%20%7C%20DE%20%7C%20FR%20%7C%20IT-purple.svg)](https://www.gnu.org/software/gettext/)

Official EU VAT validation, VIES real-time registry verification, and automatic intra-community tax rules for **ERPNext** (v14, v15, and v16).

---

## ✨ Features

- **⚡ Real-time EU VIES Validation**: Queries the European Commission's official VIES REST API instantly without requiring API keys or subscriptions.
- **🌍 Universal European Support**: Dynamically detects the home country of your ERPNext Company (or Global Defaults). Works out-of-the-box for companies based in **any EU member state** (Spain, Germany, France, Italy, Austria, Netherlands, etc.).
- **🛡️ Country Mismatch Prevention**: Checks that the VAT prefix matches the customer/supplier country (e.g. alerts if an `ES` VAT is entered for a German customer), preventing fraudulent or erroneous intra-community tax exemptions.
- **🏷️ Automated Tax Category Routing**:
  - Automatically assigns the **`EU B2B`** tax category when a valid cross-border EU VAT number is confirmed.
  - Leaves domestic transactions subject to standard national VAT.
  - Blocks saving with `EU B2B` if the VAT number is invalid or missing.
- **🏢 Registered Company Name & Address Auto-Capture**: Automatically retrieves the official business name and registered address returned by VIES.
- **🎨 Interactive UI Card in Desk**: Displays a sleek status card in the Tax section of Customer and Supplier forms with an instant **"⚡ Verify VIES"** button and visual indicators.
- **🌐 Full GNU Gettext Localization (ERPNext 16 Compliant)**:
  - English (default)
  - Spanish (`es`)
  - German (`de`)
  - French (`fr`)
  - Italian (`it`)

---

## 📋 Requirements

- Frappe Framework v16 (actively tested)
- ERPNext v16 (actively tested)
- Python packages: `requests` (included with Frappe)

---

## 🚀 Installation

From your bench directory:

```bash
# 1. Fetch the application repository
bench get-app https://github.com/<your-username>/eu_vat.git

# 2. Install the app onto your target site
bench --site <your-site-name> install-app eu_vat

# 3. Run database migrations to load custom fields & fixtures
bench --site <your-site-name> migrate

# 4. (Optional) Rebuild client assets
bench build
```

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

1. **Domestic Tax IDs**: If a national tax ID is provided (without an EU country code prefix), it is saved normally as a standard domestic tax ID.
2. **Country Consistency**: If a customer located in France is assigned an Italian VAT (`IT...`), the system triggers a country mismatch warning.
3. **EU B2B Enforcement**: If a user attempts to select the `EU B2B` tax category for an entity whose VAT is not registered in VIES, saving is prevented with an informative error.

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
