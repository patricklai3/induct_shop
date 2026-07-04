import { createApp } from 'vue'
import { FrappeUI } from 'frappe-ui'
// Import router to avoid Button injection warnings, even if it's a dummy router
import { createRouter, createMemoryHistory } from 'vue-router'
import ServicePartsSelector from './components/ServicePartsSelector.vue'
import './style.css' // ensure styles are bundled

// Dummy router to satisfy frappe-ui requirements without breaking Frappe Desk routing
const router = createRouter({
  history: createMemoryHistory(),
  routes: [],
})

class ServicePartsSelectorDialog {
    constructor(frm) {
        this.frm = frm;
        this.make();
    }
    
    make() {
        this.dialog = new frappe.ui.Dialog({
            title: __('Service & Parts Selector'),
            size: 'extra-large',
            fields: [
                {
                    fieldname: 'vue_wrapper',
                    fieldtype: 'HTML',
                }
            ],
            on_hide: () => {
                if (this.app) {
                    this.app.unmount();
                    this.app = null;
                }
            }
        });
        
        // Custom styling for the dialog to ensure Vue takes full space
        this.dialog.$wrapper.find('.modal-dialog').css('width', '80%').css('max-width', '1000px');
        this.dialog.$wrapper.find('.modal-body').css('padding', '0');
        
        this.dialog.show();
        
        this.app = createApp(ServicePartsSelector, {
            frm: this.frm,
            dialog: this.dialog
        });
        
        this.app.use(router);
        this.app.use(FrappeUI);
        
        // Mount into the HTML field wrapper
        const wrapper = this.dialog.fields_dict.vue_wrapper.$wrapper.get(0);
        this.app.mount(wrapper);
    }
}

// Make it globally available so standard doctype scripts can call it
window.ServicePartsSelectorDialog = ServicePartsSelectorDialog;

// Inject custom button into targeted DocTypes
const targetDocTypes = ['Quotation', 'Sales Order', 'Sales Invoice', 'Purchase Receipt', 'Stock Entry'];

targetDocTypes.forEach(doctype => {
    frappe.ui.form.on(doctype, {
        refresh(frm) {
            frm.add_custom_button(__('Service & Parts Selector'), () => {
                new ServicePartsSelectorDialog(frm);
            }, __('Utilities'));
        }
    });
});
