import React from 'react'
import { Form, Input, Button, Radio, message, Row } from 'antd'

const RadioGroup = Radio.Group

class RegistrationForm extends React.Component {

    constructor(props) {
        super(props)
        this.dispatch = this.props.dispatch
    }

    handleSubmit = e => {
        e.preventDefault()
        this.props.form.validateFieldsAndScroll((err, values) => {
            if (!err) {
                this.dispatch({
                    type: 'Index/saveUser'
                })
            }
        })
    }

    recordUserParam = (e, key, dispatch) => {
        dispatch({
            type: 'Index/recordUserParam',
            val: e.target.value,
            key,
        })
    }

    photograph = (userParam) => {
        if (userParam.name === '' || userParam.phone === '') {
            message.warning('请先输入姓名和手机号')
        } else {
            this.dispatch({
                type: 'Index/photograph',
                userParam
            })
        }
    }

    close = () => {
        this.dispatch({
            type: 'Index/closeRegistModal'
        })
    }

    componentDidUpdate() {
        const { restFields, userParam } = this.props
        if (restFields) {
            this.props.form.resetFields()
        }
        if (Object.values(userParam).indexOf('') !== -1 && restFields) {
            this.dispatch({
                type: 'Index/changeRestFields'
            })
        }
    }

    render() {
        const { userParam } = this.props
        const { getFieldDecorator } = this.props.form

        const formItemLayout = {
            labelCol: {
                sm: { span: 6 },
            },
            wrapperCol: {
                sm: { span: 18 },
            },
        }
        const tailFormItemLayout = {
            wrapperCol: {
                sm: { span: 24 },
            },
        }

        return <Form {...formItemLayout} onSubmit={this.handleSubmit}>
            <Form.Item label='姓名'>
                {getFieldDecorator('name', {
                    rules: [
                        {
                            required: true,
                            message: '请输入您的姓名',
                        },
                    ],
                })(<Input onChange={e => this.recordUserParam(e, 'name', this.dispatch)} />)}
            </Form.Item>
            <Form.Item label='手机'>
                {getFieldDecorator('phone', {
                    rules: [{ required: true, message: '请输入您的手机号' }],
                })(<Input onChange={e => this.recordUserParam(e, 'phone', this.dispatch)} />)}
            </Form.Item>
            <Form.Item label='性别'>
                {getFieldDecorator('gender', {
                    rules: [{ required: true, message: '请选择性别' }],
                })(<RadioGroup options={['先生', '女士']} onChange={e => this.recordUserParam(e, 'gender', this.dispatch)} />)}
            </Form.Item>
            <Form.Item label='照片'>
                {getFieldDecorator('picture', {})(<Button disabled={(userParam.name === '' || userParam.phone === '') ? true : false} onClick={() => this.photograph(userParam)}>拍照</Button>)}
            </Form.Item>
            <Form.Item {...tailFormItemLayout}>
                <Row type='flex' justify='space-around'>
                    <Button type='primary' htmlType='submit'>确认注册</Button>
                    <Button type='primary' onClick={() => this.close()}>放弃注册</Button>
                </Row>
            </Form.Item>
        </Form>
    }
}

const WrappedRegistrationForm = Form.create({ name: 'register' })(RegistrationForm)

export default WrappedRegistrationForm