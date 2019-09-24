import React from 'react'
import { connect } from 'dva'

const faceapi = require('face-api.js')

class Face extends React.Component {
    constructor(props) {
        super(props)
        this.dispatch = this.props.dispatch
    }

    componentDidMount() {

        this.dispatch({
            type: 'Index/calcFeature'
        })

        async function play() {
            await faceapi.nets.ssdMobilenetv1.load('../../weights')
            await faceapi.loadFaceLandmarkModel('../../weights')
            await faceapi.loadFaceRecognitionModel('../../weights')
            const videoEl = document.getElementById('inputVideo')
            console.log(window)
            console.log(navigator,'navigator')
            const stream = await navigator.mediaDevices.getUserMedia({ video: true })
            videoEl.srcObject = stream
        }
        play()
    }


    componentDidUpdate() {
        const { features } = this.props.Index
        async function render() {
            try {
                const videoEl = document.getElementById('inputVideo')
                const results = await faceapi.detectAllFaces(videoEl, new faceapi.SsdMobilenetv1Options({ minConfidence: 0.5 })).withFaceLandmarks().withFaceDescriptors()
                if (results.length === 0) {
                    document.getElementById("titleSpan").innerHTML = 'unknown'
                    render()
                }
                const featureArr = []
                Object.values(features).forEach(feature => {
                    featureArr.push(faceapi.euclideanDistance(results[0].descriptor, feature))
                })
                const minIndex = featureArr.indexOf(Math.min.apply(Math, featureArr))
                if (Math.min.apply(Math, featureArr) < 0.4) {
                    document.getElementById("titleSpan").innerHTML = Object.keys(features)[minIndex].substring(0, Object.keys(features)[minIndex].length - 4)
                } else {
                    document.getElementById("titleSpan").innerHTML = 'unknown'
                }
                render()
            } catch (e) { }
        }
        render()
    }



    render() {
        return <div style={{ zIndex: 999, position: 'absolute', width: '25vw', height: '30vh' }}>
            <video style={{ width: '100%', height: '100%' }} id="inputVideo" autoPlay muted playsInline></video>
            <span id='titleSpan' style={{ color: 'snow', fontSize: '2vw', fontFamily: "simsun", zIndex: 999, position: 'absolute', left: '24px', top: '10vh' }}></span>
        </div>

    }
}
export default connect(({ Index }) => ({
    Index,
}))(Face)