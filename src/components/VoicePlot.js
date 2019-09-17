import React from 'react'
import { connect } from 'dva'
import styles from '../components/styles.css'

class VoicePlot extends React.Component {
    constructor(props) {
        super(props)
        this.dispatch = this.props.dispatch
    }
    componentDidUpdate() {

        const canvas = document.getElementById('canvas')
        const ctx = canvas.getContext('2d')

        ctx.lineWidth = 1
        ctx.strokeStyle = `black`

        const draw = (data) => {
            ctx.clearRect(0, 0, canvas.width, canvas.height)
            ctx.beginPath()
            let x = 0
            const pointWidth = canvas.width / data.length
            for (let i = 0; i < data.length; i++) {
                let y = data[i] / canvas.height + canvas.height / 2
                if (i === 0) {
                    ctx.moveTo(x, y)
                } else {
                    ctx.lineTo(x, y)
                }
                x += pointWidth
            }
            ctx.lineTo(canvas.width, canvas.height / 2)
            ctx.stroke()
        }

        draw(this.props.Index.wave)


    }



    render() {
        return <canvas id='canvas' className={styles.canvas}></canvas>
    }
}
export default connect(({ Index }) => ({
    Index,
}))(VoicePlot)