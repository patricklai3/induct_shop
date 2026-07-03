import { createApp } from 'vue'
import { FrappeUI } from 'frappe-ui'
import { router } from './router'
import './style.css'
import App from './App.vue'

const app = createApp(App)
app.use(router)   // required — frappe-ui's <Button> injects Symbol(router)
app.use(FrappeUI) // installs the plugin (resource provider, etc.)
app.mount('#app')
