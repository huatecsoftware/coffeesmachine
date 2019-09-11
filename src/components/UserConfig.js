import React from 'react'
import styles from './styles.css'
import * as utils from '../utils/utils'
import { Form, Input, Button, Radio, message, Row } from 'antd'

const RadioGroup = Radio.Group

class UserConfig extends React.Component {
    constructor(props) {
        super(props)
        this.dispatch = this.props.dispatch
    }
    handleSubmit = (e) => {
        e.preventDefault()
        if (this.props.params.taste === '') {
            message.warning('请先选择咖啡')
        } else {
            this.props.form.validateFields((err) => {
                if (!err) {
                    this.dispatch({
                        type: 'Index/checkModalChange',
                        checkModal: true
                    })
                }
            })
        }
    }

    faceRecognition = () => {
        this.dispatch({
            type: 'Index/faceRecognition'
        })
    }


    componentDidUpdate() {
        const { restFields, params } = this.props
        if (restFields) {
            this.props.form.resetFields()
        }
        if (Object.values(params).indexOf('') !== -1 && restFields) {
            this.dispatch({
                type: 'Index/changeRestFields'
            })
        }
    }
    render() {
        const { getFieldDecorator } = this.props.form
        return <Form onSubmit={this.handleSubmit} className={`${styles.myForm} ${styles.flexCol}`} labelCol={{ xs: { span: 24 }, sm: { span: 8 } }} wrapperCol={{ xs: { span: 24 }, sm: { span: 16 } }}>
            <Row type='flex' style={{ width: '50vw' }}>
                <Form.Item label='姓名' style={{ marginRight: 'auto' }}>
                    {getFieldDecorator('uname', {
                        rules: [{ required: true, message: '请输入姓名' }],
                    })(<Input style={{ width: '15vw' }} autoComplete='off' onChange={e => utils.valueChange(e, 'name', this.dispatch)} placeholder='姓名' />)}
                </Form.Item>
                <Form.Item label='电话' style={{ marginLeft: 'auto' }}>
                    {getFieldDecorator('phone', {
                        rules: [{ required: true, message: '请输入手机号码' }, { pattern: /^[1][3,4,5,7,8][0-9]{9}$/, message: '号码非法 请确认' }],
                        validateTrigger: 'onSubmit'
                    })(<Input style={{ width: '15vw' }} autoComplete='off' onChange={e => utils.valueChange(e, 'phone', this.dispatch)} placeholder='电话号码' />)}
                </Form.Item>
            </Row>
            <Row type='flex' style={{ width: '50vw' }}>
                <Form.Item label='性别' style={{ marginRight: 'auto' }}>
                    {getFieldDecorator('gender', {
                        rules: [{ required: true, message: '请选择性别' }],
                    })(<RadioGroup style={{ width: '15vw' }} options={['先生', '女士']} onChange={e => utils.valueChange(e, 'gender', this.dispatch)} />)}
                </Form.Item>
                <Form.Item wrapperCol={{ sm: { span: 16, offset: 2 } }}>
                    <Row type='flex' justify='space-between' align='middle' style={{ width: '20vw' }}>
                        <Button type='primary' onClick={() => this.faceRecognition()}>智能模式</Button>
                        <Button type='primary' htmlType='submit'>确定下单</Button>
                    </Row>
                </Form.Item>
            </Row>
        </Form>
    }
}

const WrappedUserConfig = Form.create()(UserConfig)

export default WrappedUserConfig