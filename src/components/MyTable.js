import React from 'react'
import { Table } from 'antd'
import { connect } from 'dva'
import * as utils from '../utils/utils'
import * as Component from './Component'
import styles from '../components/styles.css'

class MyTable extends React.Component {
    constructor(props) {
        super(props)
        this.dispatch = this.props.dispatch
    }
    componentDidMount() {
        const queryAll = () => utils.queryAllOrder(this.dispatch)
        window.tableTimer = setInterval(queryAll, 1000)
    }
    componentWillUnmount() {
        clearInterval(window.tableTimer)
        return
    }
    render() {
        const { orders, breads } = this.props.Index
        return <div className={styles.main}>
            <Component.Header />
            <Component.Breads breads={breads} />
            <div className={styles.container}>
                <Table
                    dataSource={orders}
                    columns={utils.columns(this.dispatch)}
                    pagination={{ defaultPageSize: 7 }}
                    title={() => (<span>销量统计表</span>)}
                    rowClassName={(record, index) => (index % 2 === 0 ? styles.odd : styles.even)}
                />
            </div>
        </div>
    }
}

export default connect(({ Index }) => ({
    Index,
}))(MyTable)