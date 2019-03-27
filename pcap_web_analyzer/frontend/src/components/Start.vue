<!-- HTML Template -->
<template>
  <v-container fluid>
    <v-layout row>
      <v-flex xs10 offset-xs1 md6 offset-md3>
        <v-stepper v-model="e1">
          <v-stepper-header>
            <v-stepper-step :complete="e1 > 1" step="1">PCAP Upload</v-stepper-step>
            <v-divider></v-divider>
            <v-stepper-step :complete="e1 > 2" step="2">Analysis</v-stepper-step>
            <v-divider></v-divider>
            <v-stepper-step step="3">Results</v-stepper-step>
          </v-stepper-header>
          <v-stepper-items>
            <v-stepper-content step="1">
                <h1>Upload a PCAP file</h1>
                <v-text-field label="Select PCAP" @click='pickFile' v-model='fileName' prepend-icon='attach_file'></v-text-field>
                <input
						type="file"
                        id="file"
						style="display: none"
						ref="file"
						accept=".pcap,.pcap-ng"
						@change="handleFileUpload"
					>
                    <center><v-btn color="info" v-on:click="submitFile()">Submit</v-btn></center>
                    <div v-if="isSaving">

                      <v-progress-linear v-model="uploadPercentage"></v-progress-linear>
                    </div>
            </v-stepper-content>
            <v-stepper-content step="2">
              <h1>Analysis In Progress</h1>
              <div class="text-xs-center">
                <v-progress-circular
                  :size="50"
                  color="primary"
                  indeterminate
                ></v-progress-circular>
              </div>
            </v-stepper-content>
            <v-stepper-content step="3">
            </v-stepper-content>
          </v-stepper-items>
        </v-stepper>
      </v-flex>
    </v-layout>
  </v-container>
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
      fileName: '',
      uploadError: null,
      currentStatus: null,
      uid: null,
      e1: 1,
      result: '',
      alerts: [],
      uploadPercentage: 0
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
    pickFile () {
      this.$refs.file.click ()
    },
    handleFileUpload (e) {
      const files = e.target.files
      if(files[0] !== undefined) {
        this.fileName = files[0].name
        this.file = files[0]
      } else {
        this.fileName = ''
        this.file = ''
      }
    },
    submitFile () {
      if (this.file != '') {
        // Create a new file
        axios
          .get('/analysis/new')
          .then(response => (this.uploadFile(response['data']['id'])))
      }
    },
    uploadFile (uid) {
      this.uid = uid
      this.currentStatus = STATUS_SAVING
      let formData = new FormData()
      formData.append('file', this.file)
      axios.post('/analysis/' + uid + '/upload',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: function( progressEvent ) {
            this.uploadPercentage = parseInt( Math.round( ( progressEvent.loaded * 100 ) / progressEvent.total ) );
          }.bind(this)
        }
      ).then(() => {
        this.e1 = 2
        this.checkAnalysis()
      })
        .catch(function () {
          // TODO: redirect to error here
          this.currentStatus = STATUS_FAILED
        })
    },
    checkAnalysis() {
      axios
      .get('/analysis/' + this.uid)
      .then((response) => {
        if (response['data']['status'] == 'AnalysisStatus.INDICATOR'){
          if (this.e1 == 1){
            this.e1 == 2
          }
          setTimeout(this.checkAnalysis, 2000);
        } else if (response['data']['status'] == 'AnalysisStatus.SEARCH'){
          if (this.e1 == 1){
            this.e1 == 2
          }
          setTimeout(this.checkAnalysis, 2000);
        } else if (response['data']['status'] == 'AnalysisStatus.DONE') {
          var pcaps = JSON.parse(this.$localStorage.get('pcaps', []))
          pcaps.push(response['data'])
          this.$localStorage.set('pcaps', JSON.stringify(pcaps));
          this.$router.push({ path: '/analysis/' + this.uid })
        }
      }
      )
    }
  },
  mounted () {
    this.reset()
  }
}
</script>

<style>
</style>
