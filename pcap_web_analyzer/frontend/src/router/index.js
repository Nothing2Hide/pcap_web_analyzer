import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/Home'
import Start from '@/components/Start'
import Analysis from '@/components/Analysis'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home
    },
    {
      path: '/start',
      name: 'Start',
      component: Start
    },
    {
      path: '/analysis/:id',
      name: 'Analysis',
      component: Analysis
    }
  ]
})
