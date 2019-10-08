import * as api from '../services'
import { notification, message } from 'antd'


export default {

  namespace: 'Index',

  state: {
    step: 0,
    error: '',
    hints: [],
    range: [],
    orders: [],
    rangeStr: [],
    messages: [],
    orderIng: [],
    orderFin: [],
    features: [],
    lessOrder: [],
    camera: false,
    record: false,
    splineData: [],
    equipments: [],
    checked: false,
    nextModal: false,
    checkModal: false,
    restFields: false,
    photograph: false,
    registModal: false,
    repos: [0, 0, 0, 0, 0],
    userParam: { name: '', gender: '', phone: '' },
    rcv: { repos: [0, 0, 0, 0, 0], m130: 0, guangMu: 0 },
    params: { name: '', phone: '', gender: '', taste: '' },
    searchParam: { '姓名': '', '性别': '', '电话': '', '口味': '', '接单时间': '', '订单号': '', '订单状态': '', '完成时间': '' },
    breads: window.innerWidth > 1300 ? [['shopping-cart', '订单跟踪', 'fllow'], ['table', '订单报表', 'table'], ['pie-chart', '订单绘图', 'chart'], ['robot', '设备状态', 'equipment']] : [['ordered-list', '下单', 'order']],
  },

  effects: {
    *logRange({ e }, { put }) {
      yield put({
        type: 'saveRange',
        e
      })
    },
    *intelligenceModel({ checked }, { call, put }) {
      yield call(api.intelligenceModel, { checked })
      yield put({
        type: 'saveSwitch',
        checked
      })
    },
    *calcFeature({ _ }, { call, put }) {
      const response = yield call(api.calcFeature)
      yield put({
        type: 'saveFeature',
        features: response.data.res
      })
    },
    *isNewUser({ person, camera,record }, { put }) {
      if (person === 'unknown') {
        yield put({
          type: 'saveRegistModal',
          visible: true,
          camera,
          record
        })
      } else {
        yield put({
          type: 'saveRegistModal',
          visible: false,
          camera,
          record
        })
      }
    },
    * closeRegistModal({ _ }, { call, put }) {
      yield call(api.deleteTempFile)
      yield put({
        type: 'saveFields',
        restFields: true,
        params: { name: '', phone: '', gender: '', taste: '' },
      })
    },
    * recordUserParam({ key, val }, { put, select }) {
      const userParam = yield select(state => state.Index.userParam)
      userParam[key] = val
      yield put({
        type: 'saveUserParam',
        userParam
      })
    },
    * photograph({ userParam }, { call, put }) {
      const response = yield call(api.photograph, { ...userParam })
      if (response.data.ok === 'ok') {
        message.info('拍照成功')
        yield put({
          type: 'savePhotograph',
          photograph: true
        })
      }
    },
    * saveUser({ _ }, { call, put, select }) {
      const userParam = yield select(state => state.Index.userParam)
      const response = yield call(api.addUser, { userParam })
      if (response.data.ok === 'ok') {
        yield put({
          type: 'saveFields',
          restFields: true,
          params: { name: '', phone: '', gender: '', taste: '' },
        })
        yield put({
          type: 'savePhotograph',
          photograph: false
        })
      } else {
        message.warning('您已注册过，请不要重复注册')
      }
    },
    * rangeClick({ _ }, { call, put, select }) {
      const range = yield select(state => state.Index.range)
      let start, stop
      if (range.length === 0) {
        const date = new Date()
        const year = date.getFullYear()
        let month = date.getMonth() + 1
        if (month < 10) {
          month = `0${month}`
        }
        const day = date.getUTCDate()
        start = `${year}-${month}-01`
        stop = `${year}-${month}-${day}`
      } else {
        const startDate = range[0]._d
        const stopDate = range[1]._d
        let startMonth = startDate.getMonth() + 1
        let stopMonth = stopDate.getMonth() + 1
        if (startMonth < 10) {
          startMonth = `0${startMonth}`
        }
        if (stopMonth < 10) {
          stopMonth = `0${stopMonth}`
        }
        start = `${startDate.getFullYear()}-${startMonth}-${startDate.getUTCDate()}`
        stop = `${stopDate.getFullYear()}-${stopMonth}-${stopDate.getUTCDate()}`
      }
      const response = yield call(api.rangeClick, { start, stop })
      yield put({
        type: 'saveSeries',
        splineData: response.data.spline,
        rangeStr: [start, stop]
      })
    },
    * checkModalChange({ checkModal }, { put }) {
      yield put({
        type: 'saveCheckModal',
        checkModal,
      })
      yield put({
        type: 'saveStep',
        step: 1
      })
    },
    * nextOrder({ nextModal, text }, { put }) {
      yield put({
        type: 'saveStep',
        step: 0
      })
      yield put({
        type: 'saveNextModal',
        nextModal
      })
      if (text === 'clear') {
        yield put({
          type: 'saveFields',
          restFields: true,
          params: { name: '', phone: '', gender: '', taste: '' },
        })
      }
    },
    * queryServerData({ _ }, { call, put, select }) {
      const searchParam = yield select(state => state.Index.searchParam)
      const response = yield call(api.queryOrder, searchParam)
      yield put({
        type: 'saveOrders',
        orders: response.data.orders,
      })
    },
    * PLCON({ addr }, { call }) {
      yield call(api.PLCON, { addr })
    },
    * PLCOFF({ addr }, { call }) {
      yield call(api.PLCOFF, { addr })
    },
    * logOrderInfo({ key, val }, { put, select }) {
      const param = yield select(state => state.Index.params)
      param[key] = val
      yield put({
        type: 'saveParam',
        param
      })
    },
    * queryRcv({ _ }, { call, put }) {
      const response = yield call(api.addCheck)
      yield put({
        type: 'saveRcv',
        rcv: response.data.rcv,
        less: response.data.less
      })
    },
    * addOrder({ _ }, { call, put, select }) {
      const param = yield select(state => state.Index.params)
      const check = yield call(api.addCheck)
      const rcv = check.data.rcv
      if (rcv.coverNo === 1) {
        notification.open({
          message: '杯盖不足',
          description:
            '无杯盖，请补充',
        })
      } else if (rcv.repos.toString() === [1, 1, 1, 1, 1].toString()) {
        notification.open({
          message: '仓位不足',
          description:
            '仓位已满，请先取杯',
        })
      } else if (rcv.aError === 1) {
        notification.open({
          message: '1号机准备未完成',
          description:
            '请上电完成后在尝试下单',
        })
      } else if (rcv.bError === 1) {
        notification.open({
          message: '2号机准备未完成',
          description:
            '请上电完成后在尝试下单',
        })
      } else if (rcv.cupNo === 1) {
        notification.open({
          message: '纸杯不足',
          description:
            '无纸杯，请补充',
        })
      } else if (rcv.cafe1Material === 1) {
        notification.open({
          message: '咖啡豆不足',
          description:
            '1号机缺豆，请补充',
        })
      } else if (rcv.cafe2Material === 1) {
        notification.open({
          message: '咖啡豆不足',
          description:
            '2号机缺豆，请补充',
        })
      } else if (rcv.cafe1Rubbish === 1) {
        notification.open({
          message: '残渣已满',
          description:
            '1号机渣满，请清理',
        })
      } else if (rcv.cafe2Rubbish === 1) {
        notification.open({
          message: '残渣已满',
          description:
            '2号机渣满，请清理',
        })
      } else {
        yield call(api.addOrder, param)
        yield put({
          type: 'saveCheckModal',
          checkModal: false,
          nextModal: true
        })
        yield put({
          type: 'saveStep',
          step: 2
        })
      }
    },
    * searchOrder({ key, val }, { call, put, select }) {
      const search = yield select(state => state.Index.searchParam)
      const response = yield call(api.searchOrderByVal, { key, val })
      search[key] = val
      yield put({
        type: 'saveSearchOrders',
        orders: response.data.data,
        search
      })
    },
    * logEquipments({ equipments }, { put }) {
      yield put({
        type: 'saveSocketEquipment',
        equipments
      })
    },
    * readPLC({ rcv }, { call, put, select }) {
      yield call(api.logRcv, { rcv })
      let hints = yield select(state => state.Index.hints)
      const ing = yield select(state => state.Index.orderIng)
      const isIng = ing.length > 0 ? '努力加工咖啡中0' : '没有订单哦0'
      if (rcv.coverLess === 1) {
        hints.push('要没盖子啦1')
      } else {
        hints = hints.filter(item => item !== '要没盖子啦1')
        hints.push(isIng)
      }
      if (rcv.cupLess === 1) {
        hints.push('要没杯子啦1')
      } else {
        hints = hints.filter(item => item !== '要没杯子啦1')
        hints.push(isIng)
      }
      if (rcv.cupNo === 1) {
        hints.push('没有杯子啦2')
      } else {
        hints = hints.filter(item => item !== '没有杯子啦2')
        hints.push(isIng)
      }
      if (rcv.coverNo === 1) {
        hints.push('没有盖子啦2')
      } else {
        hints = hints.filter(item => item !== '没有盖子啦2')
        hints.push(isIng)
      }
      if (rcv.tagErr === 1) {
        hints.push('标签吸取失败2')
      } else {
        hints = hints.filter(item => item !== '标签吸取失败2')
        hints.push(isIng)
      }
      if (rcv.cafe1Material === 1) {
        hints.push('1号机没豆啦2')
      } else {
        hints = hints.filter(item => item !== '1号机没豆啦2')
        hints.push(isIng)
      }
      if (rcv.cafe2Material === 1) {
        hints.push('2号机没豆啦2')
      } else {
        hints = hints.filter(item => item !== '2号机没豆啦2')
        hints.push(isIng)
      }
      if (rcv.robotErr === 1) {
        hints.push('机器人故障2')
      } else {
        hints = hints.filter(item => item !== '机器人故障2')
        hints.push(isIng)
      }
      if (rcv.cafe1Rubbish === 1) {
        hints.push('1号机渣满啦2')
      } else {
        hints = hints.filter(item => item !== '1号机渣满啦2')
        hints.push(isIng)
      }
      if (rcv.cafe2Rubbish === 1) {
        hints.push('2号机渣满啦2')
      } else {
        hints = hints.filter(item => item !== '2号机渣满啦2')
        hints.push(isIng)
      }
      if (rcv.repos.toString() === [1, 1, 1, 1, 1].toString()) {
        hints.push('没有仓位啦1')
      } else {
        hints = hints.filter(item => item !== '没有仓位啦1')
        hints.push(isIng)
      }
      let newHint = Array.from(new Set(hints))
      if (newHint.indexOf('没有订单哦0') !== -1 && newHint.indexOf('努力加工咖啡中0') !== -1) {
        newHint = newHint.filter(item => item !== '没有订单哦0')
      }
      yield put({
        type: 'saveHints',
        rcv,
        hints: newHint.length === 1 ? newHint : newHint.filter(item => item !== '努力加工咖啡中0' && item !== '没有订单哦0')
      })
    },
    * loopDB({ _ }, { call, put, select }) {
      const rcv = yield select(state => state.Index.rcv)
      const response = yield call(api.loopDB, { rcv })
      const messages = []
      response.data.fin.forEach(item => {
        messages.push([item.Uname, item.Gender === '男' ? '先生' : '女士', item.Pos])
      })
      yield put({
        type: 'saveOrderState',
        messages,
        ing: response.data.ing,
        fin: response.data.fin,
      })
    },
    * changeRestFields({ _ }, { put }) {
      yield put({
        type: 'saveFields',
        restFields: false,
        params: { name: '', phone: '', gender: '', taste: '' },
      })
    },
  },

  reducers: {
    saveOrders(state, action) {
      return {
        ...state,
        orders: action.orders.reverse(),
      }
    },
    saveSearchOrders(state, action) {
      return {
        ...state,
        orders: action.orders.reverse(),
        searchParam: action.search
      }
    },
    saveParam(state, action) {
      return {
        ...state,
        params: action.param
      }
    },
    saveHints(state, action) {
      return {
        ...state,
        rcv: action.rcv,
        hints: action.hints,
      }
    },
    savePhotograph(state, action) {
      return {
        ...state,
        photograph: action.photograph,
      }
    },
    saveRcv(state, action) {
      return {
        ...state,
        rcv: action.rcv,
        lessOrder: action.less,
      }
    },
    saveFields(state, action) {
      return {
        ...state,
        restFields: action.restFields,
        params: action.params,
        userParam: action.params
      }
    },
    saveSocketEquipment(state, action) {
      return {
        ...state,
        equipments: action.equipments
      }
    },
    saveCheckModal(state, action) {
      return {
        ...state,
        step: action.step,
        nextModal: action.nextModal,
        checkModal: action.checkModal,
      }
    },
    saveNextModal(state, action) {
      return {
        ...state,
        nextModal: action.nextModal,
      }
    },
    saveRegistModal(state, action) {
      return {
        ...state,
        registModal: action.visible,
        camera: action.camera,
        record: action.record,
      }
    },
    saveSeries(state, action) {
      return {
        ...state,
        splineData: action.splineData,
        rangeStr: action.rangeStr,
      }
    },
    logRange(state, action) {
      return {
        ...state,
        range: action.e,
      }
    },
    saveStep(state, action) {
      return {
        ...state,
        step: action.step,
      }
    },
    saveUserParam(state, action) {
      return {
        ...state,
        userParam: action.userParam
      }
    },
    saveFeature(state, action) {
      return {
        ...state,
        features: action.features
      }
    },
    saveSwitch(state, action) {
      return {
        ...state,
        checked: action.checked
      }
    },
    saveOrderState(state, action) {
      return {
        ...state,
        orderIng: action.ing,
        orderFin: action.fin,
        messages: action.messages,
      }
    },
  },
}
