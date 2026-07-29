class ServicePartsSelectorDialog {
    constructor(opts) {
        this.frm = opts.frm;
        this.is_stock_doc = ['Purchase Receipt', 'Stock Entry'].includes(this.frm.doc.doctype);
        
        // Get project from doc if available
        this.project = this.frm.doc.project || null;
        
        this.make();
    }

    make() {
        this.dialog = new frappe.ui.Dialog({
            title: __('Service & Parts Selector'),
            size: 'extra-large',
            fields: [
                {
                    fieldname: 'search_query',
                    fieldtype: 'Data',
                    label: __('Search Parts & Services'),
                    description: __('Enter part number, name, or service keyword.')
                },
                {
                    fieldtype: 'HTML',
                    fieldname: 'results_html'
                }
            ],
            primary_action_label: __('Close'),
            primary_action: (values) => {
                this.dialog.hide();
            }
        });

        // Hide service-related UI if this is a stock document
        if (!this.is_stock_doc) {
            this.setup_ingestion_tabs();
        } else {
            this.setup_part_ingestion_only();
        }

        this.setup_events();
        this.dialog.show();
    }
    
    setup_ingestion_tabs() {
        // We can append custom HTML to the dialog for ingestion
        let html = `
            <div class="mt-4 border-top pt-4">
                <h5>${__('Ingestion Tools')}</h5>
                <div class="row">
                    <div class="col-sm-6">
                        <h6>${__('Ingest Service')}</h6>
                        <input type="text" class="form-control" id="ingest-service-url" placeholder="${__('Tesla Service Manual URL')}">
                        <button class="btn btn-sm btn-default mt-2" id="btn-ingest-service">${__('Ingest Service')}</button>
                    </div>
                    <div class="col-sm-6">
                        <h6>${__('Ingest Part')}</h6>
                        <textarea class="form-control" id="ingest-part-text" rows="2" placeholder="${__('Paste Tab-delimited Part Data')}"></textarea>
                        <button class="btn btn-sm btn-default mt-2" id="btn-ingest-part">${__('Ingest Part')}</button>
                    </div>
                </div>
            </div>
        `;
        this.dialog.fields_dict.results_html.$wrapper.append(html);
        
        this.dialog.fields_dict.results_html.$wrapper.find('#btn-ingest-service').on('click', () => {
            let url = this.dialog.fields_dict.results_html.$wrapper.find('#ingest-service-url').val();
            if(!url) return;
            
            frappe.call({
                method: 'induct_shop.api.service_parts_selector.get_all_equipment_tags',
                callback: (tag_res) => {
                    let available_tags = tag_res.message || [];
                    
                    frappe.call({
                        method: 'induct_shop.api.service_parts_selector.ingest_service',
                        args: { url: url },
                        freeze: true,
                        freeze_message: __('Ingesting Service...'),
                        callback: (r) => {
                            if(r.message) {
                                let service_info = r.message;
                                this.show_equipment_tag_modal(service_info, available_tags);
                            }
                        }
                    });
                }
            });
        });
        
        this.dialog.fields_dict.results_html.$wrapper.find('#btn-ingest-part').on('click', () => {
            let payload = this.dialog.fields_dict.results_html.$wrapper.find('#ingest-part-text').val();
            if(!payload) return;
            frappe.call({
                method: 'induct_shop.api.service_parts_selector.ingest_part',
                args: { payload: payload },
                freeze: true,
                freeze_message: __('Ingesting Part...'),
                callback: (r) => {
                    if(r.message && r.message.length > 0) {
                        frappe.show_alert({message: __('Part(s) Ingested Successfully'), indicator: 'green'});
                        this.dialog.fields_dict.search_query.set_value(r.message[0].item_code);
                        this.search();
                    }
                }
            });
        });
    }

    show_equipment_tag_modal(service_info, available_tags, is_edit_mode = false) {
        let current_tags = Array.from(service_info.equipment_requirements || []);
        
        let d = new frappe.ui.Dialog({
            title: is_edit_mode ? __('Edit Equipment Requirements') : __('Service Ingested - Equipment Requirements'),
            fields: [
                {
                    fieldtype: 'HTML',
                    fieldname: 'summary_html'
                },
                {
                    fieldtype: 'Section Break',
                    label: __('Equipment Requirements')
                },
                {
                    fieldtype: 'HTML',
                    fieldname: 'tags_container_html'
                },
                {
                    fieldname: 'new_tag_select',
                    fieldtype: 'Autocomplete',
                    label: __('Add Equipment Tag'),
                    options: available_tags.map(t => t.tag_name)
                }
            ],
            primary_action_label: __('Save Requirements'),
            primary_action: () => {
                frappe.call({
                    method: 'induct_shop.api.service_parts_selector.update_service_equipment_requirements',
                    args: {
                        item_code: service_info.item_code,
                        equipment_requirements: current_tags
                    },
                    freeze: true,
                    callback: (res) => {
                        frappe.show_alert({
                            message: __('Updated equipment requirements for {0}', [service_info.item_code]), 
                            indicator: 'green'
                        });
                        d.hide();
                        this.dialog.fields_dict.search_query.set_value(service_info.item_code);
                        this.search();
                    }
                });
            }
        });

        let render_tags = () => {
            let html = `
                <div class="mb-3">
                    <p class="text-muted small mb-2">${__('Tags required for this service. If empty, service is considered Mobile Capable.')}</p>
                    <div id="equipment-tag-chips">
            `;
            if (current_tags.length === 0) {
                html += `<span class="badge badge-info p-2 mr-1"><i class="fa fa-truck mr-1"></i> Mobile Capable (No Equipment Required)</span>`;
            } else {
                current_tags.forEach((tag, idx) => {
                    html += `
                        <span class="badge badge-warning p-2 mr-2 mb-1" style="font-size: 13px;">
                            <i class="fa fa-wrench mr-1"></i> ${tag}
                            <a class="text-danger ml-2 remove-tag-btn" data-index="${idx}" style="cursor:pointer; text-decoration:none;">&times;</a>
                        </span>
                    `;
                });
            }
            html += `</div></div>`;
            d.fields_dict.tags_container_html.$wrapper.html(html);

            d.fields_dict.tags_container_html.$wrapper.find('.remove-tag-btn').on('click', (e) => {
                let idx = $(e.currentTarget).data('index');
                current_tags.splice(idx, 1);
                render_tags();
            });
        };

        let summary_html = `
            <div class="alert alert-secondary mb-2">
                <strong>${service_info.item_code}</strong> - ${service_info.title || service_info.item_name || ''}
                ${service_info.frt_value ? `<div><small class="text-muted">${__('FRT')}: ${service_info.frt_value} ${__('hours')}</small></div>` : ''}
            </div>
        `;
        d.fields_dict.summary_html.$wrapper.html(summary_html);

        render_tags();

        d.fields_dict.new_tag_select.$input.on('change', () => {
            let val = d.get_value('new_tag_select');
            if (val && !current_tags.includes(val)) {
                current_tags.push(val);
                d.set_value('new_tag_select', '');
                render_tags();
            }
        });

        d.show();
    }

    setup_part_ingestion_only() {
        let html = `
            <div class="mt-4 border-top pt-4">
                <h5>${__('Ingestion Tools')}</h5>
                <div>
                    <h6>${__('Ingest Part')}</h6>
                    <textarea class="form-control" id="ingest-part-text" rows="2" placeholder="${__('Paste Tab-delimited Part Data')}"></textarea>
                    <button class="btn btn-sm btn-default mt-2" id="btn-ingest-part">${__('Ingest Part')}</button>
                </div>
            </div>
        `;
        this.dialog.fields_dict.results_html.$wrapper.append(html);
        
        this.dialog.fields_dict.results_html.$wrapper.find('#btn-ingest-part').on('click', () => {
            let payload = this.dialog.fields_dict.results_html.$wrapper.find('#ingest-part-text').val();
            if(!payload) return;
            frappe.call({
                method: 'induct_shop.api.service_parts_selector.ingest_part',
                args: { payload: payload },
                freeze: true,
                freeze_message: __('Ingesting Part...'),
                callback: (r) => {
                    if(r.message && r.message.length > 0) {
                        frappe.show_alert({message: __('Part(s) Ingested Successfully'), indicator: 'green'});
                        this.dialog.fields_dict.search_query.set_value(r.message[0].item_code);
                        this.search();
                    }
                }
            });
        });
    }

    setup_events() {
        // Search trigger
        this.dialog.fields_dict.search_query.$input.on('keyup', frappe.utils.debounce(() => {
            this.search();
        }, 500));
        
        // Container for results
        this.dialog.fields_dict.results_html.$wrapper.prepend(`
            <div id="smart-suggestions-container" style="display:none;" class="mb-3"></div>
            <div id="search-results-container" style="max-height: 400px; overflow-y: auto;">
                <p class="text-muted text-center mt-4">${__('Type to search...')}</p>
            </div>
        `);
    }

    search() {
        let query = this.dialog.get_value('search_query');
        if (!query) return;

        let container = this.dialog.fields_dict.results_html.$wrapper.find('#search-results-container');
        container.html(`<p class="text-muted text-center mt-4">${__('Searching...')}</p>`);

        frappe.call({
            method: 'induct_shop.api.service_parts_selector.search_catalog',
            args: {
                query: query,
                doc_type: this.frm.doc.doctype,
                project: this.project
            },
            callback: (r) => {
                if (r.message && r.message.length > 0) {
                    this.render_results(r.message, container);
                } else {
                    container.html(`<p class="text-muted text-center mt-4">${__('No results found.')}</p>`);
                }
            }
        });
    }

    render_results(results, container) {
        let html = '<div class="list-group">';
        
        results.forEach(item => {
            let badge = item.is_stock_item ? '<span class="badge badge-primary">Part</span>' : '<span class="badge badge-success">Service</span>';
            let frt_info = item.custom_frt ? ` - FRT: ${item.custom_frt}` : '';
            
            let tag_badges = '';
            if (!item.is_stock_item) {
                if (item.equipment_requirements && item.equipment_requirements.length > 0) {
                    item.equipment_requirements.forEach(t => {
                        tag_badges += `<span class="badge badge-warning mr-1" style="font-size: 11px;"><i class="fa fa-wrench mr-1"></i> ${t}</span>`;
                    });
                } else {
                    tag_badges += `<span class="badge badge-info mr-1" style="font-size: 11px;"><i class="fa fa-truck mr-1"></i> Mobile Capable</span>`;
                }
                tag_badges += `<button class="btn btn-xs btn-link text-muted btn-edit-equipment-tags p-0 ml-1" data-item-code="${item.item_code}" title="${__('Edit Equipment Tags')}"><i class="fa fa-pencil"></i></button>`;
            }

            html += `
                <div class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${item.item_code}</strong> - ${item.item_name}
                        <div><small class="text-muted">${item.description || ''}${frt_info}</small></div>
                        <div class="mt-1">${badge} ${tag_badges}</div>
                    </div>
                    <div>
            `;
            
            if(item.is_stock_item && item.variants && item.variants.length > 0) {
                html += `<select class="form-control form-control-sm mb-1 variant-selector" data-item="${item.item_code}">`;
                item.variants.forEach(v => {
                    let qty_str = (v.qty !== undefined && v.qty > 0) ? ` - ${v.qty} in stock` : ' - Out of Stock';
                    html += `<option value="${v.name}">${v.name} (${v.custom_condition}, ${v.custom_oem_status}${qty_str})</option>`;
                });
                html += `</select>`;
            }
            
            html += `
                        <button class="btn btn-sm btn-primary btn-add-item" 
                            data-item-code="${item.item_code}" 
                            data-is-stock="${item.is_stock_item}"
                            data-frt="${item.custom_frt || 0}">
                            ${__('Add')}
                        </button>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        container.html(html);

        // Bind edit equipment tags event
        container.find('.btn-edit-equipment-tags').on('click', (e) => {
            let item_code = $(e.currentTarget).data('item-code');
            let item_obj = results.find(i => i.item_code === item_code);
            frappe.call({
                method: 'induct_shop.api.service_parts_selector.get_all_equipment_tags',
                callback: (tag_res) => {
                    let available_tags = tag_res.message || [];
                    this.show_equipment_tag_modal({
                        item_code: item_obj.item_code,
                        title: item_obj.item_name,
                        frt_value: item_obj.custom_frt,
                        equipment_requirements: item_obj.equipment_requirements || []
                    }, available_tags, true);
                }
            });
        });
        
        // Bind click events
        container.find('.btn-add-item').on('click', (e) => {
            let btn = $(e.currentTarget);
            let item_code = btn.attr('data-item-code');
            let is_stock = btn.attr('data-is-stock') === "1";
            let frt = parseFloat(btn.attr('data-frt'));
            
            let variant_code = null;
            if(is_stock) {
                variant_code = btn.closest('.list-group-item').find('.variant-selector').val();
            }
            
            this.add_item_to_doc(variant_code || item_code, is_stock, frt);
        });
    }
    
    add_item_to_doc(item_code, is_stock, frt, parent_service = null) {
        let items = this.frm.doc.items || [];
        let row = items.find(r => !r.item_code || !r.item_code.trim());
        if (!row) {
            row = this.frm.add_child('items');
        }
        
        // Set basic values
        frappe.model.set_value(row.doctype, row.name, 'item_code', item_code).then(() => {
            if(is_stock) {
                if(parent_service) {
                    frappe.model.set_value(row.doctype, row.name, 'custom_parent_service_reference', parent_service);
                }
            } else {
                // It's a service
                frappe.model.set_value(row.doctype, row.name, 'qty', frt);
                frappe.model.set_value(row.doctype, row.name, 'uom', 'Hour');
                frappe.model.set_value(row.doctype, row.name, 'stock_uom', 'Hour');
                
                // Show smart suggestions
                this.load_smart_suggestions(item_code);
            }
            
            this.frm.refresh_field('items');
            frappe.show_alert({message: __('Added {0}', [item_code]), indicator: 'green'});
        });
    }
    
    load_smart_suggestions(service_code) {
        if(this.is_stock_doc) return; // shouldn't happen but just in case
        
        frappe.call({
            method: 'induct_shop.api.service_parts_selector.get_smart_suggestions',
            args: { service_code: service_code },
            callback: (r) => {
                if (r.message && r.message.length > 0) {
                    let suggestions_container = this.dialog.fields_dict.results_html.$wrapper.find('#smart-suggestions-container');
                    
                    let html = `
                        <div class="alert alert-info">
                            <strong>${__('Suggested Parts for {0}', [service_code])}</strong>
                            <div class="list-group mt-2">
                    `;
                    
                    // We only have part_codes from the suggestion API. We might need a small fetch or just basic display
                    r.message.forEach(s => {
                        html += `
                            <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center p-2">
                                <span>${s.part_code} <small class="text-muted">(freq: ${s.frequency})</small></span>
                                <button class="btn btn-xs btn-default btn-add-suggestion" data-part="${s.part_code}" data-service="${service_code}">${__('Add')}</button>
                            </div>
                        `;
                    });
                    
                    html += `</div></div>`;
                    suggestions_container.html(html).show();
                    
                    suggestions_container.find('.btn-add-suggestion').on('click', (e) => {
                        let btn = $(e.currentTarget);
                        let part_code = btn.attr('data-part');
                        let parent_service = btn.attr('data-service');
                        
                        // We need to fetch item details or just blindly add it and let set_value do the work
                        // If we blindly add it, user will need to select the right variant via grid if they didn't get a specific one
                        this.add_item_to_doc(part_code, true, 0, parent_service);
                    });
                }
            }
        });
    }
}

// Inject button into Targeted DocTypes
const TARGET_DOCTYPES = ['Quotation', 'Sales Order', 'Sales Invoice', 'Purchase Receipt', 'Stock Entry'];

TARGET_DOCTYPES.forEach(dt => {
    frappe.ui.form.on(dt, {
        refresh: function(frm) {
            frm.add_custom_button(__('Service & Parts Selector'), () => {
                new ServicePartsSelectorDialog({ frm: frm });
            }, __('Utilities'));
        }
    });
});
