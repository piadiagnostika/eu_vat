// Client script for Supplier DocType - EU VAT VIES Integration
frappe.ui.form.on('Supplier', {
    refresh: function(frm) {
        if (frm.fields_dict['pia_intra_community_valid']) {
            frm.set_df_property('pia_intra_community_valid', 'read_only', 1);
        } else if (frm.fields_dict['intra_community_valid']) {
            frm.set_df_property('intra_community_valid', 'read_only', 1);
        }
        toggle_checkbox_style(frm);
        render_vies_card(frm);
    },
    pia_intra_community_valid: function(frm) {
        toggle_checkbox_style(frm);
    },
    intra_community_valid: function(frm) {
        toggle_checkbox_style(frm);
    },
    tax_id: function(frm) {
        render_vies_card(frm);
    }
});

function toggle_checkbox_style(frm) {
    let field = frm.get_field('pia_intra_community_valid') || frm.get_field('intra_community_valid');
    if (field && field.$wrapper) {
        let checkbox = field.$wrapper.find('input[type="checkbox"]');
        let isValid = frm.doc.pia_intra_community_valid === 1 || frm.doc.intra_community_valid === 1;
        
        if (checkbox.length) {
            if (isValid) {
                checkbox.css({
                    'background-color': '#a3d9a5',
                    'border-color': '#a3d9a5',
                    'appearance': 'none',
                    '-webkit-appearance': 'none',
                    'width': '16px',
                    'height': '16px',
                    'border-radius': '4px',
                    'cursor': 'pointer',
                    'display': 'inline-grid',
                    'place-content': 'center',
                    'transition': 'all 0.2s ease'
                });
                
                if (!checkbox.find('.tick-blanco').length) {
                    checkbox.html('<span class="tick-blanco" style="color: white; font-size: 11px; font-weight: bold; line-height: 1;">✓</span>');
                }
            } else {
                checkbox.css({
                    'background-color': '',
                    'border-color': '',
                    'appearance': '',
                    '-webkit-appearance': '',
                    'width': '',
                    'height': '',
                    'border-radius': '',
                    'cursor': '',
                    'transition': ''
                });
                checkbox.empty();
            }
        }
    }
}

function render_vies_card(frm, vData) {
    let field = frm.get_field('pia_intra_community_valid') || frm.get_field('intra_community_valid');
    if (!field || !field.$wrapper) return;

    let existingCard = field.$wrapper.find('.vies-details-card');
    if (existingCard.length) {
        existingCard.remove();
    }

    let taxId = (frm.doc.tax_id || '').trim().toUpperCase();
    let isValid = (vData && vData.valid) ? true : (frm.doc.pia_intra_community_valid === 1 || frm.doc.intra_community_valid === 1);
    let supplierCountry = frm.doc.country || frm.doc.territory || '';
    let compName = (vData && vData.name) ? vData.name : (frm.doc.pia_vies_company_name || '');
    let compAddress = (vData && vData.address) ? vData.address : (frm.doc.pia_vies_address || '');

    let cardTitle = isValid ? __('✓ VIES Verified (Intra-community Operator)') : __('ℹ️ VIES VAT Status');
    let badgeText = isValid ? __('EU Active') : (taxId ? __('Domestic / No Exemption') : __('No Tax ID'));
    let btnText = __('⚡ Verify VIES');
    let helpPrompt = __('Enter a Tax ID to verify European VIES validity.');
    let labelTaxId = __('Tax ID:');
    let labelSuppCountry = __('Supplier Country:');

    let cardHtml = `
    <div class="vies-details-card" style="margin-top: 10px; padding: 12px 14px; border-radius: 8px; font-size: 12px; border: 1px solid ${isValid ? '#bbf7d0' : '#e2e8f0'}; background: ${isValid ? '#f0fdf4' : '#f8fafc'};">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <div style="display: flex; align-items: center; gap: 6px;">
                <span style="font-weight: 700; color: ${isValid ? '#15803d' : '#475569'};">
                    ${cardTitle}
                </span>
                <span style="padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: 600; background: ${isValid ? '#dcfce7' : '#e2e8f0'}; color: ${isValid ? '#166534' : '#64748b'};">
                    ${badgeText}
                </span>
            </div>
            ${taxId ? `<button type="button" class="btn btn-xs btn-default btn-check-vies" style="font-size: 11px; padding: 2px 8px; border-radius: 4px; background: #ffffff; border: 1px solid #cbd5e1; cursor: pointer;">${btnText}</button>` : ''}
        </div>

        <div class="vies-card-body" style="color: #475569; line-height: 1.5;">
            ${taxId ? `<div><b>${labelTaxId}</b> <span class="vies-vat-code" style="font-family: monospace; font-weight: ${isValid ? '700' : '600'}; color: ${isValid ? '#15803d' : '#1e293b'};">${taxId}</span> ${isValid ? `(${__('VIES Valid')})` : ''}</div>` : `<div>${helpPrompt}</div>`}
            ${supplierCountry ? `<div><b>${labelSuppCountry}</b> <span>${supplierCountry}</span></div>` : ''}
            ${compName ? `<div style="margin-top: 4px; padding-top: 4px; border-top: 1px dashed #cbd5e1;"><b>${__('Registered Name:')}</b> <span>${compName}</span></div>` : ''}
            ${compAddress ? `<div><b>${__('Registered Address:')}</b> <span>${compAddress.replace(/\n/g, ', ')}</span></div>` : ''}
        </div>
    </div>
    `;

    field.$wrapper.append(cardHtml);

    field.$wrapper.find('.btn-check-vies').on('click', function(e) {
        e.preventDefault();
        let btn = $(this);
        btn.prop('disabled', true).text(__('Checking...'));

        frappe.call({
            method: 'eu_vat.api.check_vies_vat',
            args: {
                tax_id: frm.doc.tax_id,
                customer_country: supplierCountry
            },
            callback: function(r) {
                btn.prop('disabled', false).text(__('⚡ Verify VIES'));
                if (r.message) {
                    let m = r.message;
                    let body = field.$wrapper.find('.vies-card-body');
                    
                    if (m.country_mismatch) {
                        let warnMsg = __('Notice: The VAT prefix ({0}) does not match the supplier country ({1}).').replace('{0}', m.country_code).replace('{1}', supplierCountry);
                        frappe.msgprint({
                            title: __('Country Mismatch'),
                            indicator: 'orange',
                            message: warnMsg
                        });
                        body.html(`
                            <div style="color: #b45309; font-weight: 600;">⚠️ ${__('Country Mismatch Detected')}</div>
                            <div style="font-size: 11px; color: #78350f;">${__('Tax ID belongs to {0} but supplier is registered in {1}.').replace('{0}', '<b>' + m.country_code + '</b>').replace('{1}', '<b>' + supplierCountry + '</b>')}</div>
                        `);
                    } else if (m.valid) {
                        if (frm.fields_dict['pia_vies_company_name'] && m.name) {
                            frm.set_value('pia_vies_company_name', m.name);
                        }
                        if (frm.fields_dict['pia_vies_address'] && m.address) {
                            frm.set_value('pia_vies_address', m.address);
                        }
                        frm.set_value('pia_intra_community_valid', 1);
                        toggle_checkbox_style(frm);
                        render_vies_card(frm, m);
                    } else {
                        frm.set_value('pia_intra_community_valid', 0);
                        toggle_checkbox_style(frm);
                        body.html(`
                            <div><b>${__('Tax ID:')}</b> <span style="font-family: monospace; color: #475569;">${taxId}</span></div>
                            <div style="color: #64748b; font-size: 11px;">${m.message || __('Not registered in the official European VIES registry.')}</div>
                        `);
                    }
                }
            }
        });
    });
}
