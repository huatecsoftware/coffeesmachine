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
            type: 'Index/calcFaceEncoding'
        })

        async function play() {
            await faceapi.nets.ssdMobilenetv1.load('../../weights')
            await faceapi.loadFaceLandmarkModel('../../weights')
            await faceapi.loadFaceRecognitionModel('../../weights')
            const videoEl = document.getElementById('inputVideo')
            const stream = await navigator.mediaDevices.getUserMedia({ video: true })
            videoEl.srcObject = stream
        }
        play()
    }

    componentDidUpdate() {
        const { features, personRes } = this.props.Index
        async function recognition(dispatch) {
            try {
                const videoEl = document.getElementById('inputVideo')
                const canvas = document.getElementById('canvas')
                faceapi.matchDimensions(canvas, videoEl, true)
                const results = await faceapi.detectAllFaces(videoEl, new faceapi.SsdMobilenetv1Options({ minConfidence: 0.5 })).withFaceLandmarks().withFaceDescriptors()
                let label = ''
                const featureArr = []
                Object.values(features).forEach(feature => {
                    featureArr.push(faceapi.euclideanDistance(results[0].descriptor, feature))
                })
                const minIndex = featureArr.indexOf(Math.min.apply(Math, featureArr))
                if (Math.min.apply(Math, featureArr) < 0.4) {
                    label = Object.keys(features)[minIndex].substring(0, Object.keys(features)[minIndex].length - 4)
                    if (personRes) {
                        dispatch({
                            type: 'Index/savePerson',
                            person: Object.keys(features)[minIndex]
                        })
                    }
                } else {
                    label = 'unknown'
                    if (personRes) {
                        dispatch({
                            type: 'Index/savePerson',
                            person: 'unknown'
                        })
                    }
                }
                results.forEach(({ detection }) => {
                    const drawBox = new faceapi.draw.DrawBox(detection.box, { label })
                    drawBox.draw(canvas)
                })
                //faceapi.draw.drawFaceLandmarks(canvas, faceapi.resizeResults(results, faceapi.matchDimensions(canvas, videoEl, true)))

            } catch (e) {
                console.log(e)
             }
        }
        recognition(this.dispatch)
    }

    render() {
        return <div style={{ zIndex: 999, position: 'absolute' }}>
            <video style={{ width: 320, height: 240 }} id="inputVideo" autoPlay muted playsInline></video>
            <canvas id='canvas' style={{ width: 320, height: 240, position: 'absolute', left: 0 }}></canvas>
        </div>

    }
}
export default connect(({ Index }) => ({
    Index,
}))(Face)
