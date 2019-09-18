import React from 'react'
import { Router, Route, Switch } from 'dva/router'
import Chart from './components/Chart'
import Order from './components/Order'
import Follow from './components/Follow'
import MyTable from './components/MyTable'
import Equipment from './components/Equipment'

function RouterConfig({ history }) {
  return (
    <Router history={history}>
      <Switch>
        {/* <Route path="/" exact component={window.innerWidth > 1300 ? Follow : Order} /> */}
        <Route path="/" exact component={Order} />
        <Route path="/chart" exact component={Chart} />
        <Route path="/fllow" exact component={Follow} />
        <Route path="/table" exact component={MyTable} />
        <Route path="/equipment" exact component={Equipment} />
      </Switch>
    </Router>
  )
}

export default RouterConfig
