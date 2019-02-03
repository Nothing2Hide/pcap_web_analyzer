<template>
  <div>
    <h1>Analysis</h1>
    <p>Here is some information. This is the home page</p>
    <p>{{ status }} </p>
  </div>
</template>

<script>
import * as axios from 'axios'
export default {
  name: 'Analysis',
  data () {
    return {
      uid: null,
      status: null,
      result: null
    }
  },
  methods: {
    update () {
      axios
        .get('http://127.0.0.1:8000/analysis/' + this.uid)
        .then((response) => {
          this.status = response['data']['status']
          this.result = response['data']['result']
        }
        )
    }
  },
  mounted () {
    this.uid = this.$route.params.id
    this.update()
  }
}
</script>
<style>
</style>
