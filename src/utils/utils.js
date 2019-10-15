import { Row, Icon, Input } from 'antd'
import styles from '../components/styles.css'

const Search = Input.Search

export const addOrder = (dispatch) => {
    dispatch({
        type: 'Index/addOrder',
    })
}

export const queryAllOrder = (dispatch) => {
    dispatch({
        type: 'Index/queryServerData',
    })
}
export const querySeries = (dispatch) => {
    dispatch({
        type: 'Index/rangeClick',
    })
}

export const valueChange = (e, name, dispatch) => {
    dispatch({
        type: 'Index/logOrderInfo',
        key: name,
        val: e.target.value
    })
}

export const searchOrder = (e, dispatch, dataIndex) => {
    dispatch({
        type: 'Index/searchOrder',
        key: dataIndex,
        val: e
    })
}

export const rangeClick = (e, dispatch) => {
    dispatch({
        type: 'Index/logRange',
        e
    })
}

export const getColumnSearchProps = (dataIndex, dispatch) => ({
    filterDropdown: () => {
        return <Row type='flex' justify='center' align='middle' >
            <Search
                style={{ width: '10vw' }}
                placeholder={`按${dataIndex}查询...`}
                onSearch={e => searchOrder(e, dispatch, dataIndex)}
            />
        </Row>
    },
    filterIcon: filtered => <Icon type='search' style={{ color: filtered ? '#1890ff' : undefined, fontSize: '1vw' }} />
})

export const columns = (dispatch) => {
    return [
        { title: '姓名', dataIndex: 'Uname', key: 'Uname', width: '5%', ...getColumnSearchProps('姓名', dispatch) },
        { title: '性别', dataIndex: 'Gender', key: 'Gender', width: '5%', ...getColumnSearchProps('性别', dispatch) },
        { title: '口味', dataIndex: 'Taste', key: 'Taste', width: '5%', ...getColumnSearchProps('口味', dispatch) },
        { title: '订单状态', dataIndex: 'Status', key: 'Status', width: '5%', ...getColumnSearchProps('订单状态', dispatch) },
        { title: '订单号', dataIndex: 'Number', key: 'Number', width: '7%', ...getColumnSearchProps('订单号', dispatch) },
        { title: '电话', dataIndex: 'Phone', key: 'Phone', width: '7%', ...getColumnSearchProps('电话', dispatch) },
        { title: '接单时间', dataIndex: 'Stime', key: 'Stime', width: '10%', ...getColumnSearchProps('接单时间', dispatch) },
        { title: '完成时间', dataIndex: 'Etime', key: 'Etime', width: '10%', ...getColumnSearchProps('完成时间', dispatch) },
    ]
}

export const clearFinish = (dispatch) => {
    dispatch({
        type: 'Index/logClear'
    })
}

export const closeModal = (dispatch) => {
    dispatch({
        type: 'Index/checkModalChange',
        checkModal: false
    })
}

export const nextOrder = (text, dispatch) => {
    dispatch({
        type: 'Index/nextOrder',
        nextModal: false,
        text
    })
}
export const PLCON = (e, addr, dispatch) => {
    e.preventDefault()
    dispatch({
        type: 'Index/PLCON',
        addr
    })
}
export const PLCOFF = (e, addr, dispatch) => {
    e.preventDefault()
    dispatch({
        type: 'Index/PLCOFF',
        addr
    })
}

export const FollowColumns = (item) => {
    return item === '进行中订单' ? [
        { title: '订单号', dataIndex: 'Number', key: 'Number', width: '33.33%', render: (text) => (<span><Icon type='loading' style={{ color: 'green' }} />{text}</span>) },
        { title: '客户名', dataIndex: 'Uname', key: 'Uname', width: '33.33%' },
        { title: '口味', dataIndex: 'Taste', key: 'Taste', width: '33.33%' },
    ] : [
            { title: '订单号', dataIndex: 'Number', key: 'Number', width: '33.33%', render: (text) => (<span><Icon type='smile' style={{ color: 'green' }} />{text}</span>) },
            { title: '客户名', dataIndex: 'Uname', key: 'Uname', width: '33.33%' },
            { title: '仓位号', dataIndex: 'Pos', key: 'Pos', width: '33.33%' },
        ]
}

export const errStyle = (level) => {
    if (level === '1') {
        return `${styles.right2} ${styles.flexCol} ${styles.errLevel1}`
    } else if (level === '2') {
        return `${styles.right2} ${styles.flexCol} ${styles.errLevel2}`
    } else {
        return `${styles.right2} ${styles.flexCol}`
    }
}

export const errorSelect = (level) => {
    if (level === '1') {
        return styles.errorStyle1
    } else if (level === '2') {
        return styles.errorStyle2
    } else {
        return styles.errorStyle
    }
}

export const selectEmo = (level) => {
    if (level === '1') {
        return 'meh'
    } else if (level === '2') {
        return 'frown'
    } else {
        return 'smile'
    }
}

