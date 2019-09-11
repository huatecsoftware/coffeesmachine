import React from 'react'
import { connect } from 'dva'
import MixChart from './MixChart'
import { DatePicker } from 'antd'
import * as utils from '../utils/utils'
import * as Component from './Component'
import styles from '../components/styles.css'

const { RangePicker } = DatePicker

class Chart extends React.Component {
    constructor(props) {
        super(props)
        this.dispatch = this.props.dispatch
    }
    componentDidMount() {
        const querySeries = () => utils.querySeries(this.dispatch)
        window.chartTimer = setInterval(querySeries, 1000)
    }
    componentWillUnmount() {
        clearInterval(window.chartTimer)
        return
    }
    render() {
        const { splineData, breads, rangeStr } = this.props.Index
        return <div className={styles.main}>
            <Component.Header />
            <Component.Breads breads={breads} />
            <div className={styles.container}>
                <MixChart data={splineData} rangeStr={rangeStr} />
                <RangePicker className={styles.rangePicker} onChange={(e) => utils.rangeClick(e, this.dispatch)} />
            </div>
        </div>
    }
}
export default connect(({ Index }) => ({
    Index,
}))(Chart)