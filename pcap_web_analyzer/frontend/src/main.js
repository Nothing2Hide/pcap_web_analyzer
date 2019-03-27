import 'babel-polyfill'
import Vue from 'vue'
import VueLocalStorage from 'vue-localstorage'
import './plugins/vuetify'
import App from './App.vue'
import router from './router'

Vue.config.productionTip = false

Vue.use(VueLocalStorage)

new Vue({
  render: h => h(App),
  router
}).$mount('#app')
