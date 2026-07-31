<script setup>
import { Button } from 'frappe-ui'
</script>

<template>
  <div class="p-8 bg-surface-base min-h-screen text-ink-gray-9">
    <div class="max-w-2xl mx-auto space-y-4">
      <h1 class="text-3xl font-bold tracking-tight">Induct Shop Dashboard</h1>
      <p class="text-ink-gray-7">
        frappe-ui integration complete. Design tokens, Vue Router, and FrappeUI Provider are configured.
      </p>
      <div class="flex items-center gap-3">
        <Button variant="solid" theme="gray" icon-left="lucide-plus" label="Create Task" />
        <Button variant="outline" theme="gray" icon-left="lucide-refresh-cw" label="Refresh" />
      </div>
    </div>
  </div>
</template>
