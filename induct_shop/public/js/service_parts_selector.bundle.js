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
                method: 'induct_shop.api.service_parts_selector.ingest_service',
                args: { url: url },
                freeze: true,
                freeze_message: __('Ingesting Service...'),
                callback: (r) => {
                    if(r.message) {
                        frappe.show_alert({message: __('Service Ingested Successfully'), indicator: 'green'});
                        this.dialog.fields_dict.search_query.set_value(r.message.item_code);
                        this.search();
                    }
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
            
            html += `
                <div class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${item.item_code}</strong> - ${item.item_name}
                        <div><small class="text-muted">${item.description || ''}${frt_info}</small></div>
                        ${badge}
                    </div>
                    <div>
            `;
            
            if(item.is_stock_item && item.batches && item.batches.length > 0) {
                html += `<select class="form-control form-control-sm mb-1 batch-selector" data-item="${item.item_code}">`;
                item.batches.forEach(b => {
                    html += `<option value="${b.name}">${b.name} (${b.custom_condition}, ${b.custom_oem_status})</option>`;
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
        
        // Bind click events
        container.find('.btn-add-item').on('click', (e) => {
            let btn = $(e.currentTarget);
            let item_code = btn.attr('data-item-code');
            let is_stock = btn.attr('data-is-stock') === "1";
            let frt = parseFloat(btn.attr('data-frt'));
            
            let batch_no = null;
            if(is_stock) {
                batch_no = btn.closest('.list-group-item').find('.batch-selector').val();
            }
            
            this.add_item_to_doc(item_code, is_stock, frt, batch_no);
        });
    }
    
    add_item_to_doc(item_code, is_stock, frt, batch_no, parent_service = null) {
        let row = this.frm.add_child('items');
        
        // Set basic values
        frappe.model.set_value(row.doctype, row.name, 'item_code', item_code).then(() => {
            if(is_stock) {
                if(batch_no) {
                    frappe.model.set_value(row.doctype, row.name, 'batch_no', batch_no);
                }
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
                        // If we blindly add it, we don't have batch_no right away, but standard ERPNext will fetch default batch if set, 
                        // or user can select it on the grid.
                        this.add_item_to_doc(part_code, true, 0, null, parent_service);
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
