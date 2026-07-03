import { createRouter, createWebHistory } from 'vue-router'

export const router = createRouter({
  history: createWebHistory('/frontend'), // Since we're hosting on /frontend
  routes: [
    { path: '/', name: 'Home', component: () => import('./pages/HomeScreen.vue') },
  ],
})
