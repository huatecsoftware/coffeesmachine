import React from 'react'
import { connect } from 'dva'
import VoicePlot from './VoicePlot'
import UserConfig from './UserConfig'
import * as Component from './Component'
import styles from '../components/styles.css'

const aiSocket = new WebSocket('ws://127.0.0.1:8899/AI')
aiSocket.onopen = () => {
    aiSocket.send('start')
    console.log('数据发送中...')
}

class Order extends React.Component {
    constructor(props) {
        super(props)
        this.dispatch = this.props.dispatch
        this.checkInfo = [{ 'ch': '姓名', 'en': 'name' }, { 'ch': '电话', 'en': 'phone' }, { 'ch': '种类', 'en': 'taste' },]
        this.lessCol = [{ title: '姓名', dataIndex: 'Uname', key: 'Uname' }, { title: '口味', dataIndex: 'Taste', key: 'Taste' }, { title: '订单号', dataIndex: 'Number', key: 'Number' },]
    }
    componentDidMount() {
        /* const queryRcv = () => {
            this.dispatch({
                type: 'Index/queryRcv'
            })
        } */
        //setInterval(queryRcv, 1000)

        aiSocket.onmessage = (res) => {
            const data = JSON.parse(res.data)
            this.props.dispatch({
                type: 'Index/isNewUser',
                person: data.person,
                wave: data.wave,
            })
        }

    }



    render() {
        const { params, checkModal, lessOrder, nextModal, restFields, step, userParam, registModal, photograph, checked } = this.props.Index
        return <div className={styles.main}>
            <Component.SuccessModal nextModal={nextModal} dispatch={this.dispatch} />
            <Component.RegistModal dispatch={this.dispatch} userParam={userParam} restFields={restFields} photograph={photograph} registModal={registModal} />
            <Component.CheckInfoModal checkModal={checkModal} dispatch={this.dispatch} params={params} checkInfo={this.checkInfo} />
            <Component.Header />
            <div className={`${styles.container} ${styles.flexRow}`}>
                <div className={`${styles.left} ${styles.flexCol}`}>
                    <Component.CafeType params={params} dispatch={this.dispatch} />
                    <UserConfig dispatch={this.dispatch} params={params} restFields={restFields} checked={checked} />
                    <Component.ProgStep step={step} />
                </div>
                <div className={`${styles.right} ${styles.flexCol}`}>
                    <Component.OrderShow lessCol={this.lessCol} lessOrder={lessOrder} />
                    <VoicePlot checked={checked} />
                </div>
            </div>
        </div>
    }
}
export default connect(({ Index }) => ({
    Index,
}))(Order)