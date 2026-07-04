<template>
  <FrappeUIProvider>
    <div class="flex flex-col h-[70vh] bg-surface-base rounded-lg overflow-hidden font-sans text-ink-gray-9">
      <!-- Header / Search -->
      <div class="px-5 border-b border-outline-gray-1 flex gap-2 items-center bg-surface-gray-1 min-h-12">
        <FormControl
          v-model="searchQuery"
          type="text"
          placeholder="Search parts by number or name, services by correction code..."
          class="flex-1"
          @keyup.enter="performSearch"
        />
        <Button @click="performSearch" variant="solid" theme="gray" :loading="searchResource.loading" label="Search" />
        <Button @click="showIngestion = true" variant="subtle" icon-left="lucide-plus" label="Ingest" />
      </div>

      <!-- Main Content -->
      <div class="flex-1 overflow-auto flex relative bg-surface-base">
        <!-- Search Results -->
        <div class="flex-1 p-5" v-if="!showIngestion">
          <div v-if="searchResource.loading" class="flex justify-center p-8">
            <LoadingIndicator class="w-6 h-6 text-ink-gray-5" />
          </div>
          <div v-else-if="results.length === 0 && searchResource.isFinished" class="text-center p-8 text-p-base text-ink-gray-5">
            No results found.
          </div>
          <div v-else-if="results.length === 0 && !searchResource.isFinished && !searchResource.loading" class="text-center p-8 text-p-base text-ink-gray-5">
            Search for a part or service to begin.
          </div>
          <div v-else class="space-y-4">
            <div v-for="item in results" :key="item.item_code + (item.batch_no || '')" class="border border-outline-gray-1 rounded-md p-4 flex justify-between items-center hover:bg-surface-gray-2 transition-colors">
              <div>
                <div class="text-lg">{{ item.item_code }} - {{ item.item_name }}</div>
                <div class="text-p-sm text-ink-gray-7">{{ item.description }}</div>
                
                <div class="flex flex-wrap gap-2 mt-2" v-if="item.batch_no">
                   <Badge :label="'Batch: ' + item.batch_no" theme="gray" />
                   <Badge v-if="item.condition" :label="item.condition" theme="blue" />
                   <Badge v-if="item.oem_status" :label="item.oem_status" theme="gray" />
                </div>
                <div class="mt-2" v-if="item.frt_value">
                   <Badge :label="'Service FRT: ' + item.frt_value" theme="gray" />
                </div>
              </div>
              <div class="flex flex-col items-end gap-2 shrink-0 w-32">
                <div class="text-base text-ink-green-6" v-if="item.price">{{ formatCurrency(item.price) }}</div>
                <div class="text-sm text-ink-blue-link" v-if="item.actual_qty !== undefined">Stock: {{ item.actual_qty }}</div>
                <Button @click="selectItem(item)" size="sm" variant="subtle" label="Add to Doc" />
              </div>
            </div>
          </div>
        </div>

        <!-- Ingestion UI -->
        <div class="flex-1 p-5" v-else>
          <div class="flex justify-between items-center mb-5">
            <h2 class="text-lg">Ingest Data</h2>
            <Button @click="showIngestion = false" variant="ghost" label="Back to Search" />
          </div>
          
          <div class="space-y-5">
            <!-- Service Ingestion -->
            <div class="border border-outline-gray-1 p-4 rounded-md bg-surface-gray-1" v-if="canAddServices">
              <h3 class="text-md mb-3">Ingest Service</h3>
              <div class="flex gap-2">
                <FormControl v-model="serviceUrl" type="text" placeholder="Tesla Service Manual URL..." class="flex-1" />
                <Button @click="ingestService" :loading="ingestServiceResource.loading" variant="solid" theme="gray" label="Ingest" />
              </div>
            </div>

            <!-- Part Ingestion -->
            <div class="border border-outline-gray-1 p-4 rounded-md bg-surface-gray-1">
              <h3 class="text-md mb-3">Ingest Part</h3>
              <FormControl v-model="partPayload" type="textarea" placeholder="Paste tab-delimited text from parts catalog..." />
              <div class="flex justify-end mt-3">
                <Button @click="ingestPart" :loading="ingestPartResource.loading" variant="solid" theme="gray" label="Ingest Part" />
              </div>
            </div>
          </div>
        </div>

        <!-- Smart Suggestions Sidebar -->
        <div class="w-64 border-l border-outline-gray-1 bg-surface-gray-1 p-4" v-if="suggestions.length > 0 && !showIngestion">
          <h3 class="text-sm mb-3 flex items-center gap-2">
             <span class="lucide-sparkles size-4 text-ink-blue-link" aria-hidden="true" />
             Smart Suggestions
          </h3>
          <div class="space-y-3">
            <div v-for="sugg in suggestions" :key="sugg.part_code" class="bg-surface-base p-3 rounded-md border border-outline-gray-1 text-sm flex flex-col gap-2">
              <span class="font-medium truncate" :title="sugg.part_code">{{ sugg.part_code }}</span>
              <Button size="sm" class="w-full" variant="subtle" @click="addSuggestedPart(sugg.part_code)" label="Add to Doc" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </FrappeUIProvider>
</template>

<script setup>
import { ref, computed } from 'vue'
import { FrappeUIProvider, FormControl, Button, Badge, LoadingIndicator, useCall, toast } from 'frappe-ui'

const props = defineProps({
  frm: {
    type: Object,
    required: true
  },
  dialog: {
    type: Object,
    required: true
  }
})

// Context logic
const stockDocs = ['Purchase Receipt', 'Stock Entry']
const canAddServices = computed(() => !stockDocs.includes(props.frm.doc.doctype))

// State
const searchQuery = ref('')
const results = ref([])
const showIngestion = ref(false)

const serviceUrl = ref('')
const partPayload = ref('')

const suggestions = ref([])
const activeServiceCode = ref(null)

// Resources
const searchResource = useCall({
  url: '/api/method/induct_shop.api.service_parts_selector.search_catalog',
  method: 'POST',
  immediate: false,
  onSuccess: (data) => {
    // data here is often the value inside `message` for frappe responses,
    // frappe-ui handles unnesting `message` if it's there
    results.value = data || []
  },
  onError: (err) => toast.error(err.message || 'Error searching catalog')
})

const suggestResource = useCall({
  url: '/api/method/induct_shop.api.service_parts_selector.get_smart_suggestions',
  method: 'POST',
  immediate: false,
  onSuccess: (data) => {
    if (data && data.length > 0) {
      suggestions.value = data
    }
  }
})

const ingestServiceResource = useCall({
  url: '/api/method/induct_shop.api.service_parts_selector.ingest_service',
  method: 'POST',
  immediate: false,
  onSuccess: (data) => {
    toast.success('Service ingested successfully')
    serviceUrl.value = ''
    showIngestion.value = false
    
    if (data && data.item_code) {
      searchQuery.value = data.item_code
      performSearch()
    }
  },
  onError: (err) => toast.error(err.message || 'Error ingesting service')
})

const ingestPartResource = useCall({
  url: '/api/method/induct_shop.api.service_parts_selector.ingest_part',
  method: 'POST',
  immediate: false,
  onSuccess: () => {
    toast.success('Part(s) ingested successfully')
    partPayload.value = ''
    showIngestion.value = false
  },
  onError: (err) => toast.error(err.message || 'Error ingesting part')
})

const searchByCodeResource = useCall({
  url: '/api/method/induct_shop.api.service_parts_selector.search_catalog',
  method: 'POST',
  immediate: false
})

const performSearch = async () => {
  if (!searchQuery.value.trim()) return
  await searchResource.submit({
    query: searchQuery.value,
    doc_type: props.frm.doc.doctype,
    project: props.frm.doc.project || null
  })
}

const selectItem = async (item) => {
  const isService = !!item.frt_value
  
  let row = props.frm.add_child("items")
  
  await frappe.model.set_value(row.doctype, row.name, 'item_code', item.item_code)
  
  if (isService) {
    await frappe.model.set_value(row.doctype, row.name, 'uom', 'Hour')
    await frappe.model.set_value(row.doctype, row.name, 'qty', item.frt_value)
    
    activeServiceCode.value = item.item_code
    await suggestResource.submit({ service_code: item.item_code })
  } else {
    if (item.batch_no) {
      await frappe.model.set_value(row.doctype, row.name, 'batch_no', item.batch_no)
    }
    
    if (activeServiceCode.value && frappe.meta.has_field(row.doctype, 'parent_service_reference')) {
      await frappe.model.set_value(row.doctype, row.name, 'parent_service_reference', activeServiceCode.value)
    }
  }
  
  toast.success(`Added ${item.item_code} to document.`)
}

const addSuggestedPart = async (partCode) => {
  try {
    const res = await searchByCodeResource.submit({ query: partCode, doc_type: props.frm.doc.doctype })
    
    if (res && res.length > 0) {
      selectItem(res[0])
    } else {
      let row = props.frm.add_child("items")
      await frappe.model.set_value(row.doctype, row.name, 'item_code', partCode)
      if (activeServiceCode.value && frappe.meta.has_field(row.doctype, 'parent_service_reference')) {
        await frappe.model.set_value(row.doctype, row.name, 'parent_service_reference', activeServiceCode.value)
      }
      toast.success(`Added ${partCode} to document.`)
    }
  } catch (e) {
    console.error(e)
    toast.error('Failed to add suggested part')
  }
}

const ingestService = async () => {
  if (!serviceUrl.value.trim()) return
  await ingestServiceResource.submit({ url: serviceUrl.value })
}

const ingestPart = async () => {
  if (!partPayload.value.trim()) return
  await ingestPartResource.submit({ payload: partPayload.value })
}

const formatCurrency = (val) => {
  return typeof val === 'number' ? `$${val.toFixed(2)}` : val
}
</script>
