// vite.config.js
import { defineConfig } from "file:///workspace/development/frappe-bench/apps/induct_shop/frontend/node_modules/vite/dist/node/index.js";
import vue from "file:///workspace/development/frappe-bench/apps/induct_shop/frontend/node_modules/@vitejs/plugin-vue/dist/index.mjs";
import frappeui from "file:///workspace/development/frappe-bench/apps/induct_shop/frontend/node_modules/frappe-ui/vite/index.js";
var vite_config_default = defineConfig({
  plugins: [
    frappeui({
      frappeProxy: true,
      jinjaBootData: true,
      buildConfig: true,
      frontendRoute: "/frontend"
    }),
    vue()
  ],
  optimizeDeps: {
    exclude: ["frappe-ui"],
    include: [
      "feather-icons",
      "tippy.js",
      "engine.io-client",
      "socket.io-client",
      "debug"
    ]
  }
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcuanMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCIvd29ya3NwYWNlL2RldmVsb3BtZW50L2ZyYXBwZS1iZW5jaC9hcHBzL2luZHVjdF9zaG9wL2Zyb250ZW5kXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ZpbGVuYW1lID0gXCIvd29ya3NwYWNlL2RldmVsb3BtZW50L2ZyYXBwZS1iZW5jaC9hcHBzL2luZHVjdF9zaG9wL2Zyb250ZW5kL3ZpdGUuY29uZmlnLmpzXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ltcG9ydF9tZXRhX3VybCA9IFwiZmlsZTovLy93b3Jrc3BhY2UvZGV2ZWxvcG1lbnQvZnJhcHBlLWJlbmNoL2FwcHMvaW5kdWN0X3Nob3AvZnJvbnRlbmQvdml0ZS5jb25maWcuanNcIjtpbXBvcnQgeyBkZWZpbmVDb25maWcgfSBmcm9tICd2aXRlJ1xuaW1wb3J0IHZ1ZSBmcm9tICdAdml0ZWpzL3BsdWdpbi12dWUnXG5pbXBvcnQgZnJhcHBldWkgZnJvbSAnZnJhcHBlLXVpL3ZpdGUnXG5cbmV4cG9ydCBkZWZhdWx0IGRlZmluZUNvbmZpZyh7XG4gIHBsdWdpbnM6IFtcbiAgICBmcmFwcGV1aSh7XG4gICAgICBmcmFwcGVQcm94eTogdHJ1ZSxcbiAgICAgIGppbmphQm9vdERhdGE6IHRydWUsXG4gICAgICBidWlsZENvbmZpZzogdHJ1ZSxcbiAgICAgIGZyb250ZW5kUm91dGU6ICcvZnJvbnRlbmQnLFxuICAgIH0pLFxuICAgIHZ1ZSgpLFxuICBdLFxuICBvcHRpbWl6ZURlcHM6IHtcbiAgICBleGNsdWRlOiBbJ2ZyYXBwZS11aSddLFxuICAgIGluY2x1ZGU6IFtcbiAgICAgICdmZWF0aGVyLWljb25zJyxcbiAgICAgICd0aXBweS5qcycsXG4gICAgICAnZW5naW5lLmlvLWNsaWVudCcsXG4gICAgICAnc29ja2V0LmlvLWNsaWVudCcsXG4gICAgICAnZGVidWcnLFxuICAgIF0sXG4gIH0sXG59KVxuIl0sCiAgIm1hcHBpbmdzIjogIjtBQUF5VyxTQUFTLG9CQUFvQjtBQUN0WSxPQUFPLFNBQVM7QUFDaEIsT0FBTyxjQUFjO0FBRXJCLElBQU8sc0JBQVEsYUFBYTtBQUFBLEVBQzFCLFNBQVM7QUFBQSxJQUNQLFNBQVM7QUFBQSxNQUNQLGFBQWE7QUFBQSxNQUNiLGVBQWU7QUFBQSxNQUNmLGFBQWE7QUFBQSxNQUNiLGVBQWU7QUFBQSxJQUNqQixDQUFDO0FBQUEsSUFDRCxJQUFJO0FBQUEsRUFDTjtBQUFBLEVBQ0EsY0FBYztBQUFBLElBQ1osU0FBUyxDQUFDLFdBQVc7QUFBQSxJQUNyQixTQUFTO0FBQUEsTUFDUDtBQUFBLE1BQ0E7QUFBQSxNQUNBO0FBQUEsTUFDQTtBQUFBLE1BQ0E7QUFBQSxJQUNGO0FBQUEsRUFDRjtBQUNGLENBQUM7IiwKICAibmFtZXMiOiBbXQp9Cg==
