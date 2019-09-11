import styles from './styles.css'
import Register from './Register'
import * as utils from '../utils/utils'
import { Breadcrumb, Icon, Modal, Row, Button, Table, Steps, Result } from 'antd'

const { Step } = Steps

const Header = () => {
    return <div className={`${styles.header} ${styles.flexRow}`}>
        <div className={styles.logo}></div>
        <div className={styles.name}>工业机器人调制饮品体验工作站</div>
    </div>
}
const Breads = ({ breads }) => {
    return <Breadcrumb className={`${styles.bread} ${styles.flexRow}`}>
        {breads.map(item => (
            <Breadcrumb.Item style={{ color: `#/${item[2]}` === window.location.hash ? 'rgb(72, 164, 240)' : 'black' }} key={item[2]} href={`http://${window.location.host}/#/${item[2]}`}>
                <Icon type={item[0]} style={{ fontSize: '1.5vw' }} />
                <span>{item[1]}</span>
            </Breadcrumb.Item>
        ))}
    </Breadcrumb>
}
const CafeType = ({ params, dispatch }) => {
    return <div className={`${styles.flexRow} ${styles.tasteType}`}>
        {['清咖啡', '浓咖啡'].map((item, ind) => (
            <div key={ind}>
                <div className={`${ind === 0 ? styles.taste : styles.taste1} ${styles.flexCol}`} style={{ boxShadow: `inset 0 0 ${params.taste === item ? '100px' : '10px'} snow` }} onClick={() => utils.valueChange({ target: { value: item } }, 'taste', dispatch)}></div>
                <div className={`${styles.tasteName} ${styles.flexRow}`} style={{ color: params.taste === item ? 'green' : 'black' }}><Icon type='check-circle' style={{ display: params.taste === item ? 'block' : 'none' }} />{item}</div>
            </div>
        ))}
    </div>
}
const SuccessModal = ({ nextModal, dispatch }) => {
    return <Modal
        width={300}
        centered={true}
        closable={false}
        okText='继续下单'
        cancelText='关闭'
        visible={nextModal}
        onOk={() => utils.nextOrder('', dispatch)}
        onCancel={() => utils.nextOrder('clear', dispatch)}
    >
        <Result
            status='success'
            title='下单成功'
            subTitle='系统已接单，请耐心等待'
        />
    </Modal>
}
const RegistModal = ({ dispatch, userParam, registModal, restFields, photograph }) => {
    return <Modal
        width={300}
        footer={null}
        centered={true}
        closable={false}
        visible={registModal}
    >
        <Register userParam={userParam} dispatch={dispatch} restFields={restFields} photograph={photograph} />
    </Modal>
}
const CheckInfoModal = ({ checkModal, dispatch, params, checkInfo }) => {
    return <Modal
        okText='确认'
        width={200}
        centered={true}
        closable={false}
        cancelText='取消'
        visible={checkModal}
        title={<span>订单确认</span>}
        onOk={() => utils.addOrder(dispatch)}
        onCancel={() => utils.closeModal(dispatch)}
    >
        <div className={styles.flexCol}>
            {checkInfo.map((item, ind) => (
                <div key={ind} className={`${styles.flexRow} ${styles.orderInfo}`}>
                    <span>{`${item.ch}:`}</span>
                    <span>{params[item.en]}</span>
                </div>
            ))}
        </div>
    </Modal>
}
const EquipmentState = ({ equipments }) => {
    return <div className={`${styles.epuipment} ${styles.flexRow}`}>
        {equipments.map((item, ind) => (
            <div className={`${styles.flexCol}`} key={ind}>
                <span className={styles.equipTitle}>{item.title}</span>
                {item.data.map((item, ind) => (
                    <Row type='flex' align='middle' key={ind} style={{ width: '15vw' }}>
                        <div className={item.status === 1 ? styles.lambOn : styles.lambOff}></div>
                        <div className={styles.lambFont}>{item.desc}</div>
                    </Row>
                ))}
            </div>
        ))}
    </div>
}
const EquipmentButton = ({ buttons, orderIng, dispatch }) => {
    return <div className={`${styles.flexRow} ${styles.stateBtns}`}>
        {buttons.map((item, ind) => (
            <Button key={ind} className={styles.btnStyle} disabled={ind === 3 ? false : orderIng.length > 0 ? true : false} onMouseDown={e => utils.PLCON(e, item.addr, dispatch)} onMouseUp={e => utils.PLCOFF(e, item.addr, dispatch)} type='primary'>{item.desc}</Button>
        ))}
    </div>
}
const FollowTable = ({ orderIng, orderFin }) => {
    return <Row type='flex'>
        {['进行中订单', '待取走订单'].map((item, ind) => (
            <Table
                bordered
                key={ind}
                pagination={false}
                className={styles.followTable}
                columns={utils.FollowColumns(item)}
                title={() => (<span>{item}</span>)}
                dataSource={item === '进行中订单' ? orderIng : orderFin}
                rowClassName={(record, index) => (index % 2 === 0 ? styles.odd : styles.even)}
            />
        ))}
    </Row>
}
const ScrollWord = ({ messages }) => {
    return <div className={`${styles.flexCol} ${styles.scrollWord}`}>
        {messages.map((item, ind) => (
            <div key={ind}>
                <span className={styles.hintStyle}>{`${item[0]}`}</span>
                <span>{`${item[1]}，您的咖啡已制作完毕，请到`}</span>
                <span className={styles.hintStyle}>{`${item[2]}`}</span>
                <span>{`号位取杯`}<Icon type='smile' style={{ color: 'green' }} /></span>
            </div>
        ))}
    </div>
}
const FollowError = ({ hints }) => {
    return <div className={utils.errStyle(window.errLevel)}>
        {hints.map((item, ind) => {
            const content = item.substring(0, item.length - 1)
            const level = item.substr(-1)
            window.errLevel = level
            return <span className={utils.errorSelect(level)} key={ind}><Icon type={utils.selectEmo(level)} />{content}</span>
        })}
    </div>
}
const OrderShow = ({ lessCol, lessOrder }) => {
    return <Table
        columns={lessCol}
        pagination={false}
        dataSource={lessOrder}
        className={styles.lessOrder}
    />
}
const ProgStep = ({ step }) => {
    return <div className={styles.stepContainer}>
        <Steps current={step} className={`${styles.steps} ${styles.flexRow}`}>
            <Step icon={<Icon type='form' />} title='填写信息' />
            <Step icon={<Icon type='file-search' />} title='确认信息' />
            <Step icon={<Icon type='check-circle' />} title='完成下单' />
        </Steps>
    </div>
}

export { Header, Breads, CafeType, SuccessModal, CheckInfoModal, EquipmentState, EquipmentButton, FollowTable, ScrollWord, FollowError, OrderShow, ProgStep, RegistModal }