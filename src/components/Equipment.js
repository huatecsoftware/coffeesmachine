import React from 'react'
import { connect } from 'dva'
import * as Component from './Component'
import styles from '../components/styles.css'

class Equipment extends React.Component {
    constructor(props) {
        super(props)
        this.dispatch = this.props.dispatch
        this.buttons = [{ 'desc': '咖啡机1上电', 'addr': 'M88.0' }, { 'desc': '咖啡机2上电', 'addr': 'M88.1' }, { 'desc': '气缸复位', 'addr': 'M189.0' }, { 'desc': '故障再启动', 'addr': 'M29.7' },]
    }
    componentDidMount() {
        if (window.innerWidth > 1300) {
            window.socket.onmessage = (message) => {
                const rcv = JSON.parse(message.data)
                this.dispatch({
                    type: 'Index/logEquipments',
                    equipments: rcv.equipment
                })
            }
        }
    }
    render() {
        const { breads, equipments, orderIng } = this.props.Index
        return <div className={styles.main}>
            <Component.Header />
            <Component.Breads breads={breads} />
            <div className={styles.container}>
                <Component.EquipmentButton buttons={this.buttons} orderIng={orderIng} dispatch={this.dispatch} />
                <Component.EquipmentState equipments={equipments} />
            </div>
        </div>
    }
}
export default connect(({ Index }) => ({
    Index,
}))(Equipment)