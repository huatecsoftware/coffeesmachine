import React from 'react'
import { connect } from 'dva'
import * as Component from './Component'
import styles from '../components/styles.css'

class Follow extends React.Component {
    constructor(props) {
        super(props)
        this.dispatch = this.props.dispatch
    }
    componentDidMount() {
        const loopDB = () => {
            this.dispatch({
                type: 'Index/loopDB',
            })
        }
        setInterval(loopDB, 1500)
        if (window.innerWidth > 1300) {
            window.socket.onmessage = (message) => {
                const rcv = JSON.parse(message.data)
                this.dispatch({
                    type: 'Index/readPLC',
                    rcv,
                })
            }
        }
    }
    render() {
        const { hints, orderIng, orderFin, breads, messages } = this.props.Index
        return <div>
            <Component.Header />
            <Component.Breads breads={breads} />
            <Component.ScrollWord messages={messages} />
            <div className={`${styles.container} ${styles.flexRow}`}>
                <Component.FollowTable orderFin={orderFin} orderIng={orderIng} />
                <Component.FollowError hints={hints} />
            </div>
        </div>
    }
}
export default connect(({ Index }) => ({
    Index,
}))(Follow)