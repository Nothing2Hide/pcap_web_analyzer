<!-- App.vue -->

<!-- HTML Template -->
<template>
  <form enctype="multipart/form-data" novalidate v-if="isInitial || isSaving">
    <h1>Upload a PCAP file</h1>
    <div class="dropbox">
      <label>File
        <input type="file" id="file" ref="file" v-on:change="handleFileUpload()" accept=".pcap,.pcap-ng"/>
      </label>
      <button v-on:click="submitFile()">Submit</button>
      <p v-if="isInitial">
        Drag your file(s) here to begin<br> or click to browse
      </p>
      <p v-if="isSaving">
      Uploading files...
      </p>
    </div>
  </form>
</template>

<!-- Javascript -->
<script>
import * as axios from 'axios'
const STATUS_INITIAL = 0
const STATUS_SAVING = 1
const STATUS_SUCCESS = 2
const STATUS_FAILED = 3
export default {
  name: 'Start',
  data () {
    return {
      file: '',
      uploadError: null,
      currentStatus: null,
      uid: null
    }
  },
  computed: {
    isInitial () {
      return this.currentStatus === STATUS_INITIAL
    },
    isSaving () {
      return this.currentStatus === STATUS_SAVING
    },
    isSuccess () {
      return this.currentStatus === STATUS_SUCCESS
    },
    isFailed () {
      return this.currentStatus === STATUS_FAILED
    }
  },
  methods: {
    reset () {
      // reset form to initial state
      this.currentStatus = STATUS_INITIAL
      this.file = ''
      this.uploadError = null
      this.uid = null
    },
    handleFileUpload () {
      this.file = this.$refs.file.files[0]
    },
    submitFile () {
      // Create a new file
      this.currentStatus = STATUS_SAVING
      axios
        .get('http://127.0.0.1:8000/analysis/new')
        .then(response => (this.uploadFile(response['data']['id'])))
    },
    uploadFile (uid) {
      console.log(uid)
      this.uid = uid
      let formData = new FormData()
      formData.append('file', this.file)
      axios.post('http://127.0.0.1:8000/analysis/' + uid + '/upload',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      ).then((response) => {
        this.$router.push({ path: '/analysis/' + uid })
      })
        .catch(function () {
          // TODO: redirect to error here
          this.currentStatus = STATUS_FAILED
        })
    }
  },
  mounted () {
    this.reset()
  }
}
</script>

<style>
</style>
